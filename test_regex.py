import re

def extract_wallets(text):
    patterns = [
        r'\b1[1-9A-HJ-NP-Za-km-z]{25,34}\b',
        r'\b3[1-9A-HJ-NP-Za-km-z]{25,34}\b',
        r'\bbc1[qxp][0-9a-z]{38,58}\b',
        r'\b0x[a-fA-F0-9]{40}\b'
    ]
    full_pattern = '|'.join(patterns)
    return re.findall(full_pattern, text, re.IGNORECASE)

test_addr = "0xF1d93361cd0cBff0669845BB21208547913Ac0e9"
print(f"Testing: {test_addr}")
print(f"Result: {extract_wallets(test_addr)}")
