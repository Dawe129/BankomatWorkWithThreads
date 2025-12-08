import random
import time

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
