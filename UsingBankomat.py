import threading
import time
import random
from queue import PriorityQueue

atm_semaphore = threading.Semaphore(2)

class Customer(threading.Thread):
    def __init__(self, customer_id, is_vip, queue):
        super().__init__()
        self.customer_id = customer_id
        self.is_vip = is_vip
        self.queue = queue

    def run(self):
        priority = 0 if self.is_vip else 1
        self.queue.put((priority, self.customer_id, self))
        print(f"{'VIP ' if self.is_vip else ''}Zákazník {self.customer_id} čeká ve frontě.")

def atm_worker(queue):
    while True:
        atm_semaphore.acquire()
        try:
            priority, customer_id, customer_thread = queue.get(timeout=3)
        except Exception:
            atm_semaphore.release()
            break
        print(f"{'VIP ' if priority==0 else ''}Zákazník {customer_id} právě používá bankomat.")
        time.sleep(random.randint(3, 6))
        print(f"{'VIP ' if priority==0 else ''}Zákazník {customer_id} dokončil a odchází.")
        atm_semaphore.release()
        queue.task_done()

def main():
    queue = PriorityQueue()
    customers = [
        Customer(1, False, queue),
        Customer(2, True, queue),
        Customer(3, False, queue),
        Customer(4, False, queue),
        Customer(5, True, queue)
    ]

    for c in customers:
        c.start()
        time.sleep(random.uniform(0, 1))

    workers = []
    for _ in range(2):
        w = threading.Thread(target=atm_worker, args=(queue,))
        w.daemon = True
        w.start()
        workers.append(w)

    for c in customers:
        c.join()
    queue.join()
    print("Simulace bankomatů s VIP hotová.")

if __name__ == "__main__":
    main()
