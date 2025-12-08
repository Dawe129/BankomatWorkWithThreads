import time

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
