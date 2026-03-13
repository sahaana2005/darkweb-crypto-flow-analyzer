from scraper.wallet_extractor import extract_wallets
from blockchain.fetch_transactions import fetch_transactions
from analysis.graph_builder import build_graph

text = """
Vendor listing
Payment address:
1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY
"""

wallets = extract_wallets(text)

print("Detected wallets:", wallets)

for wallet in wallets:

    txs = fetch_transactions(wallet)

    print("Transactions:", txs)

    graph = build_graph(wallet, txs)

    print("Graph nodes:", graph.nodes())
    print("Graph edges:", graph.edges())