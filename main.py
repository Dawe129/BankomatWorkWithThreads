import multiprocessing
import random
import time

from ticket import Ticket
from persistence import load_accounts, save_accounts, accounts_from_data
from worker import operator_worker, print_account_statements


def main():
    base_data = load_accounts()
    manager = multiprocessing.Manager()
    shared_list = manager.list()
    semaphore = multiprocessing.Semaphore(3)

    accounts = accounts_from_data(base_data, manager)

    suspicious_limit = 7000

    tickets = [
        Ticket(1, False, 1, "withdraw", 1500),
        Ticket(2, True,  2, "deposit", 3000),
        Ticket(3, False, 3, "balance", None),
        Ticket(4, True,  2, "withdraw", 8000),
        Ticket(5, False, 1, "deposit", 2000),
        Ticket(6, True,  4, "withdraw", 9500),
        Ticket(7, True,  2, "transfer", 6000, target_account_id=5),
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
        extra = f" -> účet {t.target_account_id}" if t.request_type == "transfer" and t.target_account_id else ""
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

    for acc in accounts:
        print("DEBUG:", acc.account_id, acc.balance)

    save_accounts(accounts)


if __name__ == "__main__":
    main()
