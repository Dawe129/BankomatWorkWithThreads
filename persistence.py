import json
from pathlib import Path
from account import Account

ACCOUNTS_FILE = Path("accounts.json")

def load_accounts():
    if not ACCOUNTS_FILE.exists():
        data = [
            {"id": 1, "balance": 5000,  "daily_limit": 4000,  "withdrawn_today": 0, "history": []},
            {"id": 2, "balance": 12000, "daily_limit": 10000, "withdrawn_today": 0, "history": []},
            {"id": 3, "balance": 8000,  "daily_limit": 5000,  "withdrawn_today": 0, "history": []},
            {"id": 4, "balance": 20000, "daily_limit": 15000, "withdrawn_today": 0, "history": []},
            {"id": 5, "balance": 3000,  "daily_limit": 3000,  "withdrawn_today": 0, "history": []},
        ]
        ACCOUNTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        data = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
    return data

def accounts_from_data(data, manager):
    accounts = manager.list()
    for d in data:
        acc = manager.dict()
        acc['account_id'] = d["id"]
        acc['balance'] = d["balance"]
        acc['daily_limit'] = d["daily_limit"]
        acc['withdrawn_today'] = d["withdrawn_today"]
        acc['history'] = manager.list(d.get("history", []))
        accounts.append(acc)
    return accounts

def save_accounts(accounts):
    payload = []
    for acc in accounts:
        payload.append({
            "id": acc['account_id'],
            "balance": acc['balance'],
            "daily_limit": acc['daily_limit'],
            "withdrawn_today": acc['withdrawn_today'],
            "history": list(acc['history']),
        })
    ACCOUNTS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")