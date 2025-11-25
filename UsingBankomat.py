import threading
import time
import random
from queue import PriorityQueue

operator_semaphore = threading.Semaphore(2)

class Account:
    def __init__(self, account_id, balance):
        self.account_id = account_id
        self.balance = balance

class Ticket(threading.Thread):
    def __init__(self, ticket_id, is_vip, account, request_type, amount, queue):
        super().__init__()
        self.ticket_id = ticket_id
        self.is_vip = is_vip
        self.account = account
        self.request_type = request_type
        self.amount = amount
        self.queue = queue

    def run(self):
        priority = 0 if self.is_vip else 1
        self.queue.put((priority, self.ticket_id, self))
        print(f"{'VIP ' if self.is_vip else ''}Požadavek {self.ticket_id}: {self.request_type} {self.amount if self.amount else ''} zadán do fronty.")

def operator_worker(queue):
    while True:
        operator_semaphore.acquire()
        try:
            priority, ticket_id, ticket_thread = queue.get(timeout=3)
        except Exception:
            operator_semaphore.release()
            break

        acc = ticket_thread.account
        req = ticket_thread.request_type
        amount = ticket_thread.amount

        if req == "deposit":
            acc.balance += amount
            print(f"{'VIP ' if priority==0 else ''}Účet {acc.account_id}: Vklad {amount}. Nový zůstatek {acc.balance}.")
        elif req == "withdraw":
            if acc.balance >= amount:
                acc.balance -= amount
                print(f"{'VIP ' if priority==0 else ''}Účet {acc.account_id}: Výběr {amount}. Nový zůstatek {acc.balance}.")
            else:
                print(f"{'VIP ' if priority==0 else ''}Účet {acc.account_id}: Nedostatek prostředků!")
        elif req == "balance":
            print(f"{'VIP ' if priority==0 else ''}Účet {acc.account_id}: Zůstatek {acc.balance}.")
        
        time.sleep(random.randint(3, 6))
        operator_semaphore.release()
        queue.task_done()

def main():
    queue = PriorityQueue()
    accounts = [
        Account(1, 5000),
        Account(2, 12000)
    ]

    tickets = [
        Ticket(1, False, accounts[0], "withdraw", 1500, queue),
        Ticket(2, True, accounts[1], "deposit", 3000, queue),
        Ticket(3, False, accounts[0], "balance", None, queue),
        Ticket(4, True, accounts[1], "withdraw", 8000, queue),
        Ticket(5, False, accounts[0], "deposit", 2000, queue),
    ]

    for t in tickets:
        t.start()
        time.sleep(random.uniform(0, 1))

    workers = []
    for _ in range(2):
        w = threading.Thread(target=operator_worker, args=(queue,))
        w.daemon = True
        w.start()
        workers.append(w)

    for t in tickets:
        t.join()
    queue.join()
    print("Všechny akce u bankomatu byly zpracovány.")

if __name__ == "__main__":
    main()
