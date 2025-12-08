class Ticket:
    def __init__(self, ticket_id, is_vip, account, request_type, amount, target_account=None):
        self.ticket_id = ticket_id
        self.is_vip = is_vip
        self.account = account          # zdrojový účet
        self.request_type = request_type  # "deposit", "withdraw", "balance", "transfer"
        self.amount = amount
        self.target_account = target_account
