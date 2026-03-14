import hashlib

def get_seed_mod(wallet):
    return int(hashlib.sha256(wallet.encode()).hexdigest()[:8], 16) % 100

candidates = [
    "1QLbz7JHiBTspS962RLKV8GndWFwi5j6Qr",
    "3FZbgi29cpjq2GjdwV8eyHuJNkLtktZc5",
    "bc1qxy2kgdygjrsqptzq2n0yrf2493p83kkfjhx0wlh",
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
    "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
    "1dice8EMZmqkvrGE4Qc9bUff9PX3xaYDp",
    "1BoatSLHrtFHZ3wu25vE67WCHG3p9YgqN",
    "1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY"
]

print("Scanning for results...")
for c in candidates:
    mod = get_seed_mod(c)
    level = "HIGH" if mod >= 66 else ("MEDIUM" if mod >= 33 else "LOW")
    print(f"[{level}] {c} (SeedMod: {mod})")
