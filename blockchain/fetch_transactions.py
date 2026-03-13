import requests

def fetch_transactions(wallet):

    url = f"https://blockchain.info/rawaddr/{wallet}"

    response = requests.get(url)

    data = response.json()

    transactions = []

    for tx in data["txs"][:10]:
        transactions.append(tx["hash"])

    return transactions