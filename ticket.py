class Ticket:
    def __init__(self, ticket_id, is_vip, account_id, request_type, amount, target_account_id=None):
        self.ticket_id = ticket_id
        self.is_vip = is_vip
        self.account_id = account_id
        self.request_type = request_type
        self.amount = amount
        self.target_account_id = target_account_id
