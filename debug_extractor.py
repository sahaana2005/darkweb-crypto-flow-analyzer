from scraper.wallet_extractor import extract_wallets

test_cases = [
    "0xF1d93361cd0cBff0669845BB21208547913Ac0e9",
    "Sent to 0xF1d93361cd0cBff0669845BB21208547913Ac0e9 recently",
    "List: 0xF1d93361cd0cBff0669845BB21208547913Ac0e9, 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
]

for t in test_cases:
    found = extract_wallets(t)
    print(f"Text: {t}")
    print(f"Found: {found}")
    print("-" * 20)
