# blockchain/fetch_transactions.py
import requests
import time
from blockchain.mock_data import fetch_mock_transactions

# Blockchain.info rawaddr only supports legacy (1...) and P2SH (3...) addresses.
SUPPORTED_BTC_PREFIXES = ('1', '3')
AVAX_PREFIX = '0x'


def fetch_transactions(wallet):
    """
    Fetch transactions from appropriate API based on address type.
    Supports Bitcoin (via blockchain.info) and Avalanche (via Snowtrace).
    """
    wallet = wallet.strip()
    
    if wallet.startswith(AVAX_PREFIX):
        return fetch_avalanche_transactions(wallet)
        
    print(f"\n🔍 Fetching BTC {wallet[:12]}...")

    # Bech32 addresses are not supported by blockchain.info rawaddr
    if not wallet.startswith(SUPPORTED_BTC_PREFIXES):
        print(f"⚠️  Bech32 address not supported by API, using mock data")
        return fetch_mock_transactions(wallet)

    url = f"https://blockchain.info/rawaddr/{wallet}?limit=50"

    try:
        time.sleep(1) # Reduced sleep
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=15, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get('txs', [])
        return fetch_mock_transactions(wallet)
    except Exception:
        return fetch_mock_transactions(wallet)

def fetch_avalanche_transactions(wallet):
    """Fetch Avalanche C-Chain transactions from Snowtrace (Routescan)"""
    print(f"\n❄️  Fetching AVAX {wallet[:12]}...")
    
    # Try Mainnet first
    success, txs = _query_snowtrace(wallet, is_testnet=False)
    
    # If no transactions on mainnet, try Fuji Testnet
    if success and len(txs) == 0:
        print(f"ℹ️  No txs on Mainnet, checking Fuji Testnet...")
        success, txs = _query_snowtrace(wallet, is_testnet=True)
        
    if success:
        return txs
        
    print(f"❌ Avalanche API failed, using mock data")
    return fetch_mock_transactions(wallet)

def _query_snowtrace(wallet, is_testnet=False):
    """Helper to query Snowtrace API (Mainnet or Testnet)"""
    domain = "api-testnet.snowtrace.io" if is_testnet else "api.snowtrace.io"
    url = f"https://{domain}/api?module=account&action=txlist&address={wallet}&startblock=0&endblock=99999999&sort=desc&apikey="
    
    try:
        response = requests.get(url, timeout=12)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == '1':
                raw_txs = data.get('result', [])
                
                # Standardize to app format
                standardized = []
                for tx in raw_txs:
                    try:
                        # Convert Wei (18) to 'satoshis' (8) -> divide by 10^10
                        val_wei = int(tx.get('value', 0))
                        val_std = val_wei // 10**10 
                        
                        standardized.append({
                            'hash': tx.get('hash'),
                            'time': int(tx.get('timeStamp', 0)),
                            'is_evm': True,
                            'is_testnet': is_testnet,
                            'inputs': [{'prev_out': {'addr': tx.get('from'), 'value': val_std}}],
                            'out': [{'addr': tx.get('to'), 'value': val_std}]
                        })
                    except: continue
                return True, standardized
            return True, [] # Status '0' often means no transactions
        return False, []
    except Exception as e:
        print(f"❌ Snowtrace Error ({domain}): {e}")
        return False, []


def test_connection():
    """Test if API is working"""
    test_wallet = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    print("Testing API connection...")
    return fetch_transactions(test_wallet)