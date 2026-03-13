# analysis/pattern_detector.py

def detect_patterns(wallet, txs):
    """
    Detect suspicious patterns in a wallet's transactions.
    Returns a list of pattern names (strings)
    """
    patterns = []

    # Example: if more than 50 transactions, flag as high activity
    if len(txs) > 50:
        patterns.append("High Transaction Volume")

    # Example: if wallet has multiple incoming & outgoing patterns
    if len(txs) > 0 and len(txs) % 2 == 0:
        patterns.append("Suspicious Transaction Pattern")

    return patterns