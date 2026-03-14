from scraper.wallet_extractor import extract_wallets

test_addr = "0xF1d93361cd0cBff0669845BB21208547913Ac0e9"
found = extract_wallets(test_addr)
print(f"Text: {test_addr}")
print(f"Found count: {len(found)}")
if found:
    print(f"First match: {found[0]}")
