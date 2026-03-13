# Write a Python function called extract_wallets(text)
# that extracts Bitcoin wallet addresses using regex
# and returns them as a list
import re

def extract_wallets(text):

    pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'

    wallets = re.findall(pattern, text)

    return wallets 
