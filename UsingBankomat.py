import multiprocessing
import time
import random
import json
from pathlib import Path

ACCOUNTS_FILE = Path("accounts.json")

def load_accounts():
    if not ACCOUNTS_FILE.exists():
        data = [
            {"id": 1, "balance": 5000, "daily_limit": 4000, "withdrawn_today": 0, "history": []},
            {"id": 2, "balance": 12000, "daily_limit": 10000, "withdrawn_today": 0, "history": []},
            {"id": 3, "balance": 8000, "daily_limit": 5000, "withdrawn_today": 0, "history": []},
            {"id": 4, "balance": 20000, "daily_limit": 15000, "withdrawn_today": 0, "history": []},
            {"id": 5, "balance": 3000, "daily_limit": 3000, "withdrawn_today": 0, "history": []},
        ]
        ACCOUNTS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    return data

def save_accounts(accounts):
    data = []
    for acc in accounts:
        data.append({
            "id": acc.account_id,
            "balance": acc.balance,
            "daily_limit": acc.daily_limit,
            "withdrawn_today": acc.withdrawn_today,
            "history": acc.history,
        })
    ACCOUNTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

class Account:
    def __init__(self, account_id, balance, daily_limit, withdrawn_today=0, history=None):
        self.account_id = account_id
        self.balance = balance
        self.daily_limit = daily_limit
        self.withdrawn_today = withdrawn_today
        self.history = history or []

    def add_history(self, action, amount, note):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(
            {"time": ts, "action": action, "amount": amount, "note": note}
        )


class Ticket:
    def __init__(self, ticket_id, is_vip, account, request_type, amount, target_account=None):
        self.ticket_id = ticket_id
        self.is_vip = is_vip
        self.account = account
        self.request_type = request_type
        self.amount = amount
        self.target_account = target_account

def operator_worker(shared_list, accounts, semaphore, suspicious_limit):
    while True:
        semaphore.acquire()
        try:
            if shared_list:
                idx, item = min(enumerate(shared_list), key=lambda x: x[1][0])
                priority, ticket_id, ticket = item
                shared_list.pop(idx)
            else:
                semaphore.release()
                break
        except Exception:
            semaphore.release()
            break

        acc_idx = ticket.account.account_id - 1
        acc = accounts[acc_idx]
        req = ticket.request_type
        amount = ticket.amount

        header = f"{'VIP ' if priority == 0 else ''}Požadavek {ticket_id} | účet {acc.account_id} | Akce: {req.upper()}"
        print('\n' + '=' * 70)
        print(header)
        print('-' * 70)

        suspicious = amount is not None and amount >= suspicious_limit
        note = ""

        if req == "deposit":
            acc.balance += amount
            note = f"Vklad {amount} Kč, nový zůstatek {acc.balance} Kč"
            print(" >", note)

        elif req == "withdraw":
            if amount is None:
                note = "Chyba: částka musí být zadána."
                print(" >", note)
            elif amount > acc.daily_limit - acc.withdrawn_today:
                note = (f"Překročení denního limitu. Dnes {acc.withdrawn_today} / "
                        f"{acc.daily_limit} Kč, požadavek {amount} Kč.")
                print(" >", note)
            elif acc.balance >= amount:
                acc.balance -= amount
                acc.withdrawn_today += amount
                note = (f"Výběr {amount} Kč, dnes {acc.withdrawn_today} / "
                        f"{acc.daily_limit} Kč, nový zůstatek {acc.balance} Kč")
                print(" >", note)
            else:
                note = f"Nedostatek prostředků: dostupné {acc.balance} Kč, požadováno {amount} Kč."
                print(" >", note)

        elif req == "balance":
            note = (f"Dotaz na zůstatek: {acc.balance} Kč, dnes vybráno "
                    f"{acc.withdrawn_today} / {acc.daily_limit} Kč")
            print(" >", note)

        elif req == "transfer":
            target = ticket.target_account
            if target is None:
                note = "Chyba: není zadaný cílový účet."
                print(" >", note)
            elif amount is None or amount <= 0:
                note = "Chyba: částka převodu musí být > 0."
                print(" >", note)
            elif amount > acc.daily_limit - acc.withdrawn_today:
                note = (f"Překročení denního limitu při převodu. Dnes "
                        f"{acc.withdrawn_today} / {acc.daily_limit} Kč, požadavek {amount} Kč.")
                print(" >", note)
            elif acc.balance >= amount:
                acc.balance -= amount
                acc.withdrawn_today += amount
                target.balance += amount
                note = (f"Převod {amount} Kč z účtu {acc.account_id} na účet {target.account_id}. "
                        f"Nový zůstatek {acc.balance} Kč.")
                print(" >", note)
                target.add_history("incoming_transfer", amount,
                                   f"Příchozí převod z účtu {acc.account_id}")

            else:
                note = f"Nedostatek prostředků pro převod: {acc.balance} Kč, požadavek {amount} Kč."
                print(" >", note)

        else:
            note = "Neznámý typ požadavku."
            print(" >", note)

        if req in ("deposit", "withdraw", "balance", "transfer"):
            acc.add_history(req, amount, note)

        if suspicious and req in ("withdraw", "deposit", "transfer"):
            print(" ! POZOR: Transakce označena jako PODEZŘELÁ (vysoká částka)!")
            acc.add_history("alert", amount, "Podezřelá transakce – vysoká částka")

        print('=' * 70 + '\n')

        time.sleep(random.randint(1, 3))
        semaphore.release()

def print_account_statements(accounts):
    print("\n" + "#" * 80)
    print("VÝPISY Z ÚČTŮ (pohled manažera)")
    print("#" * 80)
    for acc in accounts:
        print(f"\nÚČET {acc.account_id} – zůstatek {acc.balance} Kč, denní limit {acc.daily_limit} Kč")
        print("-" * 80)
        if not acc.history:
            print("  (Žádné transakce)")
        else:
            for h in acc.history:
                print(f" {h['time']} | {h['action'].upper():10} | "
                      f"{'' if h['amount'] is None else str(h['amount']) + ' Kč':>8} | {h['note']}")
    print("#" * 80 + "\n")

def main():
    base_data = load_accounts()
    manager = multiprocessing.Manager()
    shared_list = manager.list()
    semaphore = multiprocessing.Semaphore(3)

    accounts = manager.list([
        Account(d["id"], d["balance"], d["daily_limit"], d["withdrawn_today"], d.get("history", []))
        for d in base_data
    ])

    suspicious_limit = 7000

    tickets = [
        Ticket(1, False, accounts[0], "withdraw", 1500),
        Ticket(2, True,  accounts[1], "deposit", 3000),
        Ticket(3, False, accounts[2], "balance", None),
        Ticket(4, True,  accounts[1], "withdraw", 8000),
        Ticket(5, False, accounts[0], "deposit", 2000),
        Ticket(6, True,  accounts[3], "withdraw", 9500),
        Ticket(7, True,  accounts[1], "transfer", 6000, target_account=accounts[4]),
    ]

    workers = []
    for _ in range(3):
        p = multiprocessing.Process(
            target=operator_worker,
            args=(shared_list, accounts, semaphore, suspicious_limit)
        )
        p.daemon = True
        p.start()
        workers.append(p)

    for t in tickets:
        priority = 0 if t.is_vip else 1
        extra = f" -> účet {t.target_account.account_id}" if t.request_type == "transfer" and t.target_account else ""
        print('-' * 50)
        print(f"{'VIP ' if t.is_vip else ''}Požadavek {t.ticket_id}: {t.request_type.upper()}"
              f"{f' {t.amount}' if t.amount is not None else ''}{extra}")
        print('Zadán do fronty.')
        print('-' * 50)
        shared_list.append((priority, t.ticket_id, t))
        time.sleep(random.uniform(0, 1))

    for p in workers:
        p.join(timeout=15)

    print("Všechny akce u banky byly zpracovány.\n")

    print_account_statements(accounts)

    save_accounts(accounts)


if __name__ == "__main__":
    main()
