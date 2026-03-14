import sys
import os
sys.path.insert(0, os.path.abspath("."))

from scraper.wallet_extractor import extract_wallets
from blockchain.fetch_transactions import fetch_transactions
from analysis.graph_builder import build_graph
from analysis.pattern_detector import detect_patterns, calculate_risk_score

text = "0xF1d93361cd0cBff0669845BB21208547913Ac0e9"
wallets = extract_wallets(text)
print("Extracted wallets:", wallets)

for wallet in wallets:
    print(f"\nProcessing {wallet}:")
    try:
        txs = fetch_transactions(wallet)
        print(f"Transactions fetched: {len(txs)}")
        G = build_graph(wallet, txs)
        print(f"Graph nodes: {G.number_of_nodes()}, edges: {G.number_of_edges()}")
        patterns = detect_patterns(wallet, txs, G)
        print(f"Patterns detected: {len(patterns)}")
        score = calculate_risk_score(wallet, patterns, len(txs))
        print(f"Risk score: {score}")
    except Exception as e:
        import traceback
        traceback.print_exc()
