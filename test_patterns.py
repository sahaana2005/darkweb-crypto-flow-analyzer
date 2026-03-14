# test_patterns.py
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis.pattern_detector import detect_patterns, calculate_risk_score, get_risk_level
from blockchain.fetch_transactions import fetch_transactions

print("=" * 60)
print("TESTING PATTERN DETECTOR")
print("=" * 60)

# Test with a real Bitcoin wallet
wallet = "1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY"
print(f"\n📊 Testing wallet: {wallet}")

# Fetch transactions
print("🔄 Fetching transactions...")
txs = fetch_transactions(wallet)
print(f"✅ Found {len(txs)} transactions")

# Detect patterns
print("🔍 Detecting patterns...")
patterns = detect_patterns(wallet, txs)

# Calculate risk score
score = calculate_risk_score(wallet, patterns, len(txs))
risk_level, color = get_risk_level(score)

# Display results
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)

print(f"\n📈 Risk Score: {score}/100")
print(f"⚠️  Risk Level: {risk_level}")

print(f"\n🔴 Patterns Detected: {len(patterns)}")
if patterns:
    for i, p in enumerate(patterns, 1):
        print(f"\n  {i}. {p['title']}")
        print(f"     {p['description']}")
        print(f"     Severity: {p['severity']}")
else:
    print("  No suspicious patterns detected")

print("\n" + "=" * 60)