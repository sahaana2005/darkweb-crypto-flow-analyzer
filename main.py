from scraper.wallet_extractor import extract_wallets
from blockchain.fetch_transactions import fetch_transactions
from analysis.graph_builder import build_graph
from visualization.dashboard import show_graph

text = """
Vendor: Shadow Market
Send payment to:
1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY
"""

wallets = extract_wallets(text)

transactions = fetch_transactions(wallets[0])

graph = build_graph(transactions)

show_graph(graph)