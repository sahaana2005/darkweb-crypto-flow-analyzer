import json
from blockchain.fetch_transactions import _query_snowtrace, fetch_avalanche_transactions

test_addr = "0xF1d93361cd0cBff0669845BB21208547913Ac0e9"
print(f"Testing Snowtrace API directly for {test_addr} on Fuji Testnet...")
success, txs = _query_snowtrace(test_addr, is_testnet=True)
print(f"Success: {success}, Txs count: {len(txs)}")
if len(txs) > 0:
    print(f"First tx: {json.dumps(txs[0], indent=2)}")

print("\nTesting full fetch_avalanche_transactions flow...")
txs = fetch_avalanche_transactions(test_addr)
print(f"Final returned txs count: {len(txs)}")
if len(txs) > 0:
    print(f"First returned tx: {json.dumps(txs[0], indent=2)}")
