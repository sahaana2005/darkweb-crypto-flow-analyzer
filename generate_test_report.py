import hashlib

def get_seed_mod(wallet):
    return int(hashlib.sha256(wallet.encode()).hexdigest()[:8], 16) % 100

def get_level(mod):
    if mod < 33: return "LOW"
    if mod < 66: return "MEDIUM"
    return "HIGH"

# Generate some random looking strings to find clear examples
test_pool = [f"wallet_test_{i}" for i in range(100)]
examples = {"LOW": [], "MEDIUM": [], "HIGH": []}

for i in range(500):
    w = hashlib.md5(str(i).encode()).hexdigest()
    # Mock addresses look like real ones
    addr = f"1{w[:33]}"
    mod = get_seed_mod(addr)
    level = get_level(mod)
    if len(examples[level]) < 3:
        examples[level].append(addr)

print("=== TEST DATA REPORT ===")
for level, wallets in examples.items():
    print(f"\n[{level} RISK EXAMPLES]")
    for w in wallets:
        print(w)
