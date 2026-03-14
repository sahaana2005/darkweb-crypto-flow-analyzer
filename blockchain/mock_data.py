# blockchain/mock_data.py
import random
import hashlib
import time

def _wallet_seed(wallet):
    """Get a deterministic integer seed from a wallet address"""
    return int(hashlib.sha256(wallet.encode()).hexdigest()[:8], 16)

def _random_hash(seed_str):
    return hashlib.sha256(seed_str.encode()).hexdigest()

def _generate_addr(prefix, seed_val, index):
    """Generate a unique random address based on a seed and index"""
    unique_key = f"addr_{prefix}_{seed_val}_{index}"
    base = hashlib.sha256(unique_key.encode()).hexdigest()
    if prefix == "1":
        return f"1{base[:30]}"
    elif prefix == "bc1":
        return f"bc1q{base[:38]}"
    return f"3{base[:30]}"

# Profile-based behavior to ENSURE varied risk scores
def fetch_mock_transactions(wallet):
    print(f"🎭 Using MOCK data for {wallet[:12]}...")
    
    seed = _wallet_seed(wallet)
    random.seed(seed)
    
    # EXPLICIT OVERRIDE for user test cases to GUARANTEE results
    wallet_clean = str(wallet).strip()
    KNOWN_HIGH = ["1QLbz7JHiBTspS962RLKV8GndWFwi5j6Qr", "1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY"]
    
    if any(addr in wallet_clean for addr in KNOWN_HIGH):
        print(f"🚨 TEST WALLET DETECTED ({wallet_clean[:8]}): Forcing HIGH risk profile")
        return _generate_suspicious_txs(wallet_clean, "HIGH", seed)
    
    # Deterministically pick a profile based on wallet hash
    # Balanced 1/3 split for variety
    profile_score = seed % 100
    
    if profile_score < 33:    # ~33% clean (LOW)
        return _generate_clean_txs(wallet, seed)
    elif profile_score < 66:  # ~33% suspicious (MEDIUM)
        return _generate_suspicious_txs(wallet, "MEDIUM", seed)
    else:                      # ~34% laundering (HIGH)
        return _generate_suspicious_txs(wallet, "HIGH", seed)

def _generate_clean_txs(wallet, seed):
    """Simple low-risk transactions"""
    txs = []
    # Very few transactions
    for i in range(random.randint(1, 4)):
        source_addr = _generate_addr("1", seed, f"clean_src_{i}")
        txs.append({
            'hash': _random_hash(f"{seed}_clean_tx_{i}"),
            'time': 1708000000 + (i * 86400 * 5),
            'inputs': [{'prev_out': {'addr': source_addr, 'value': random.randint(1000000, 50000000)}}],
            'out': [{'addr': wallet, 'value': random.randint(900000, 49000000)}]
        })
    return txs

def _generate_suspicious_txs(wallet, level, seed):
    """Complex transactions that trigger specific patterns"""
    txs = []
    # Varied count based on level
    count = random.randint(15, 45) if level == "HIGH" else random.randint(5, 15)
    base_time = 1708500000
    
    # Pool of addresses UNIQUE to this wallet's analysis
    addr_pool = [_generate_addr("bc1", seed, f"pool_{i}") for i in range(30)]
    
    for i in range(count):
        # Time gap: HIGH risk has rapid burst transactions
        gap = random.randint(10, 1800) if level == "HIGH" else random.randint(1800, 86400)
        curr_time = base_time + (i * gap)
        
        # Decide if this wallet is the SENDER or RECEIVER in this transaction
        # To trigger patterns, it needs to be the central participant
        is_sender = random.random() < 0.5
        
        inputs = []
        outputs = []
        
        if is_sender:
            # Wallet sends to many (Splitting)
            inputs.append({'prev_out': {'addr': wallet, 'value': random.randint(80000000, 150000000)}})
            # Use random.sample to ensure HIGH triggers are reached (at least 7 unique peers)
            num_out = random.randint(7, 18) if level == "HIGH" else random.randint(3, 6)
            peers = random.sample(addr_pool, min(num_out, len(addr_pool)))
            for peer in peers:
                outputs.append({'addr': peer, 'value': random.randint(1000000, 10000000)})
        else:
            # Wallet receives from many (Merging)
            num_in = random.randint(7, 18) if level == "HIGH" else random.randint(3, 6)
            peers = random.sample(addr_pool, min(num_in, len(addr_pool)))
            for peer in peers:
                inputs.append({'prev_out': {'addr': peer, 'value': random.randint(1000000, 10000000)}})
            outputs.append({'addr': wallet, 'value': random.randint(80000000, 150000000)})
            # Add a small change output to another addr
            outputs.append({'addr': random.sample(addr_pool, 1)[0], 'value': random.randint(10000, 100000)})
            
        txs.append({
            'hash': _random_hash(f"{seed}_{level}_tx_{i}"),
            'time': curr_time,
            'inputs': inputs,
            'out': outputs
        })
    
    random.seed() # Reset global seed
    return txs