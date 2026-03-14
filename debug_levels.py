import hashlib

def get_seed_mod(wallet):
    return int(hashlib.sha256(wallet.encode()).hexdigest()[:8], 16) % 100

def get_level(mod):
    if mod < 33: return "LOW"
    if mod < 66: return "MEDIUM"
    return "HIGH"

# Check some standard addresses
addrs = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", # Satoshi
    "1dice8EMZmqkvrGE4Qc9bUff9PX3xaYDp", # SatoshiDice
    "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
    "3FZbgi29cpjq2GjdwV8eyHuJNkLtktZc5",
    "bc1qxy2kgdygjrsqptzq2n0yrf2493p83kkfjhx0wlh",
    "1QLbz7JHiBTspS962RLKV8GndWFwi5j6Qr"
]

for a in addrs:
    mod = get_seed_mod(a)
    print(f"[{get_level(mod)}] {a} (Score: {mod})")
