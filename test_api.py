# test_api.py
from blockchain.fetch_transactions import fetch_transactions

wallets = [
    "1A1zP1eP5OGefi2DMPTfTL5SLmv7DivfNa",
    "bc1qar0srrr7xfkvy516431ydnw9re59gtzzwf5mdq",
    "3FZbgi29cpjq2GjdwV8eyHuJNkLtktZc5"
]

for wallet in wallets:
    txs = fetch_transactions(wallet)
    print(f"{wallet[:12]}...: {len(txs)} transactions")
    print("-" * 40)