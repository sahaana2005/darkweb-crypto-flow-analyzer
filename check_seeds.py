import hashlib

def seed(w):
    return int(hashlib.sha256(w.encode()).hexdigest()[:8], 16)

wallets = [
    '1dice8EMZmqkvrGE4Qc9bUff9PX3xaYDp',
    '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
    '1QLbz7JHiBTspS962RLKV8GndWFwi5j6Qr'
]

for w in wallets:
    s = seed(w)
    print(f"{w}: {s % 100}")
