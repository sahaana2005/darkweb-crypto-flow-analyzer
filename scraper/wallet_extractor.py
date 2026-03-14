"""
Bitcoin wallet address extractor for darkweb crypto flow analysis.
Supports all common formats: legacy P2PKH (1...), P2SH (3...), Bech32 (bc1q/bc1p).
Returns unique list of matches. Basic length/format validation only (no checksum).
"""

import re
from typing import List, Set


def extract_wallets(text: str) -> List[str]:
    """
    Extract Bitcoin wallet addresses from input text using regex.
    
    Args:
        text: Input text potentially containing wallet addresses
        
    Returns:
        List of unique Bitcoin addresses found
        
    Example:
        >>> extract_wallets("Send to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa bc1qar0srrr7xfkvy5l643zdckpt7hysr0u2r2nct")
        ['1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'bc1qar0srrr7xfkvy5l643zdckpt7hysr0u2r2nct']
    """
    # Comprehensive Bitcoin address regex patterns (case-insensitive)
    patterns = [
        # Legacy P2PKH: starts with '1', 26-35 chars
        r'\b1[1-9A-HJ-NP-Za-km-z]{25,34}\b',
        # P2SH: starts with '3', 26-35 chars  
        r'\b3[1-9A-HJ-NP-Za-km-z]{25,34}\b',
        # Bech32 (P2WPKH/P2WSH): bc1q/bc1p + 39/59 chars (witness v0/v1)
        r'\bbc1[qxp][0-9a-z]{38,58}\b',
        # Avalanche/Ethereum (C-Chain): 0x followed by 40 hex chars
        r'\b0x[a-fA-F0-9]{40}\b'
    ]
    
    # Combine patterns
    full_pattern = '|'.join(patterns)
    flags = re.IGNORECASE | re.VERBOSE
    
    # Find all matches
    matches: Set[str] = set(re.findall(full_pattern, text, flags))
    
    # Return as sorted list (by address string length then alphabetically)
    return sorted(list(matches), key=lambda x: (len(x), x))

