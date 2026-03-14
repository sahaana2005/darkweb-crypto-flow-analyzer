import hashlib
from analysis.pattern_detector import detect_patterns, calculate_risk_score, get_risk_level
from blockchain.mock_data import fetch_mock_transactions

wallet = "1QLbz7JHiBTspS962RLKV8GndWFwi5j6Qr"
txs = fetch_mock_transactions(wallet)
patterns = detect_patterns(wallet, txs)
score = calculate_risk_score(wallet, patterns, len(txs))
level, _ = get_risk_level(score)

print(f"Wallet: {wallet}")
print(f"Transactions: {len(txs)}")
print(f"Patterns: {len(patterns)}")
print(f"Score: {score}")
print(f"Level: {level}")
