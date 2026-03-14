from scraper.wallet_extractor import extract_wallets

text = """0xF1d93361cd0cBff0669845BB21208547913Ac0e9

this is a valid wallet address for avalanche fuji testnet but the web app is unable to detect the wallet address"""

print("Result:", extract_wallets(text))
