import multiprocessing
import time
import random

class Account:
    def __init__(self, account_id, balance, daily_limit):
        self.account_id = account_id
        self.balance = balance
        self.daily_limit = daily_limit
        self.withdrawn_today = 0

class Ticket:
    def __init__(self, ticket_id, is_vip, account, request_type, amount):
        self.ticket_id = ticket_id
        self.is_vip = is_vip
        self.account = account
        self.request_type = request_type
        self.amount = amount

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
        print('\n' + '=' * 60)
        print(header)
        print('-' * 60)

        suspicious = amount is not None and amount >= suspicious_limit

        if req == "deposit":
            acc.balance += amount
            print(f" > Vklad: {amount} Kč")
            print(f" > Nový zůstatek: {acc.balance} Kč")
        elif req == "withdraw":
            if amount is None:
                print(" > Chyba: částka musí být zadána.")
            elif amount > acc.daily_limit - acc.withdrawn_today:
                print(f" > Překročení denního limitu!")
                print(f" > Dnes již vybráno: {acc.withdrawn_today} Kč, denní limit: {acc.daily_limit} Kč.")
            elif acc.balance >= amount:
                acc.balance -= amount
                acc.withdrawn_today += amount
                print(f" > Výběr: {amount} Kč")
                print(f" > Dnes celkem vybráno: {acc.withdrawn_today} / {acc.daily_limit} Kč")
                print(f" > Nový zůstatek: {acc.balance} Kč")
            else:
                print(f" > Nedostatek prostředků! Dostupné: {acc.balance} Kč, požadováno: {amount} Kč.")
        elif req == "balance":
            print(f" > Aktuální zůstatek: {acc.balance} Kč")
            print(f" > Dnes vybráno: {acc.withdrawn_today} / {acc.daily_limit} Kč")
        else:
            print(" > Neznámý typ požadavku.")

        if suspicious and req in ("withdraw", "deposit"):
            print(" ! POZOR: Tato transakce je označena jako PODEZŘELÁ (vysoká částka)!")

        print('=' * 60 + '\n')

        time.sleep(random.randint(2, 4))
        semaphore.release()

def main():
    manager = multiprocessing.Manager()
    shared_list = manager.list()
    semaphore = multiprocessing.Semaphore(2)

    suspicious_limit = 7000

    accounts = manager.list([
        Account(1, 5000, daily_limit=4000),
        Account(2, 12000, daily_limit=10000)
    ])

    tickets = [
        Ticket(1, False, accounts[0], "withdraw", 1500),
        Ticket(2, True, accounts[1], "deposit", 3000),
        Ticket(3, False, accounts[0], "balance", None),
        Ticket(4, True, accounts[1], "withdraw", 8000),
        Ticket(5, False, accounts[0], "deposit", 2000),
        Ticket(6, True, accounts[1], "withdraw", 9500),
    ]

    workers = []
    for _ in range(2):
        p = multiprocessing.Process(
            target=operator_worker,
            args=(shared_list, accounts, semaphore, suspicious_limit)
        )
        p.daemon = True
        p.start()
        workers.append(p)

    for t in tickets:
        priority = 0 if t.is_vip else 1
        print('-' * 40)
        print(f"{'VIP ' if t.is_vip else ''}Požadavek {t.ticket_id}: {t.request_type.upper()}"
              f"{f' {t.amount}' if t.amount is not None else ''}")
        print('Zadán do fronty.')
        print('-' * 40)
        shared_list.append((priority, t.ticket_id, t))
        time.sleep(random.uniform(0, 1))

    for p in workers:
        p.join(timeout=10)
    print("Všechny akce u bankomatu byly zpracovány.")

if __name__ == "__main__":
    main()
