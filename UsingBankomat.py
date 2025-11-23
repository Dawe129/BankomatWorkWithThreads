import threading
import time
import random

atm_semaphore = threading.Semaphore(2)

class Customer(threading.Thread):
    def __init__(self, customer_id):
        super().__init__()
        self.customer_id = customer_id

    def run(self):
        print(f"Zákazník {self.customer_id} čeká na bankomat.")
        
        with atm_semaphore:
            print(f"Zákazník {self.customer_id} právě používá bankomat.")
            time.sleep(random.randint(1, 5))
            print(f"Zákazník {self.customer_id} dokončil práci a odchází.")

def main():
    customers = []

    for i in range(1, 6):
        c = Customer(i)
        customers.append(c)
        c.start()
        time.sleep(random.uniform(0, 1))

    for c in customers:
        c.join()

    print("Simulace bankomatů dokončena.")

if __name__ == "__main__":
    main()
