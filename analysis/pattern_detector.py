import networkx as nx
from collections import Counter

def detect_patterns(wallet, transactions, graph=None):
    """
    Detect REAL suspicious patterns in wallet transactions
    """
    patterns = []
    
    if not transactions:
        return patterns
    
    # Extract data
    incoming_from = []
    outgoing_to = []
    amounts = []
    timestamps = []
    
    for tx in transactions:
        tx_hash = tx.get('hash', '')
        timestamps.append(tx.get('time', 0))
        
        # Inputs (senders)
        inputs = tx.get('inputs', [])
        for inp in inputs:
            prev_out = inp.get('prev_out', {})
            from_wallet = prev_out.get('addr')
            if from_wallet and from_wallet != wallet:
                incoming_from.append(from_wallet)
                amounts.append({
                    'wallet': from_wallet,
                    'amount': prev_out.get('value', 0) / 100000000,
                    'tx': tx_hash,
                    'type': 'incoming'
                })
        
        # Outputs (receivers)
        outputs = tx.get('out', [])
        for out in outputs:
            to_wallet = out.get('addr')
            if to_wallet and to_wallet != wallet:
                outgoing_to.append(to_wallet)
                amounts.append({
                    'wallet': to_wallet,
                    'amount': out.get('value', 0) / 100000000,
                    'tx': tx_hash,
                    'type': 'outgoing'
                })
    
    # === PATTERN 1: FUND SPLITTING (One to many) ===
    unique_recipients = len(set(outgoing_to))
    if unique_recipients >= 5:
        patterns.append({
            'type': 'FUND_SPLITTING',
            'severity': 'HIGH',
            'title': '🚨 Fund Splitting Detected',
            'description': f'Wallet sends to {unique_recipients} different addresses',
            'details': {
                'count': unique_recipients,
                'pattern': 'Money laundering via structuring'
            }
        })
    elif unique_recipients >= 3:
        patterns.append({
            'type': 'FUND_SPLITTING',
            'severity': 'MEDIUM',
            'title': '⚠️ Multiple Recipients',
            'description': f'Wallet sends to {unique_recipients} different addresses',
            'details': {'count': unique_recipients}
        })
    
    # === PATTERN 2: FUND MERGING (Many to one) ===
    unique_senders = len(set(incoming_from))
    if unique_senders >= 5:
        patterns.append({
            'type': 'FUND_MERGING',
            'severity': 'HIGH',
            'title': '🚨 Fund Merging Detected',
            'description': f'Wallet receives from {unique_senders} different sources',
            'details': {
                'count': unique_senders,
                'pattern': 'Fund consolidation'
            }
        })
    elif unique_senders >= 3:
        patterns.append({
            'type': 'FUND_MERGING',
            'severity': 'MEDIUM',
            'title': '⚠️ Multiple Sources',
            'description': f'Wallet receives from {unique_senders} different sources',
            'details': {'count': unique_senders}
        })
    
    # === PATTERN 3: PEELING CHAIN (Layering) ===
    if graph and len(outgoing_to) > 0 and len(incoming_from) > 0:
        try:
            # Find longest path
            all_wallets = set(incoming_from) | set(outgoing_to) | {wallet}
            subgraph = graph.subgraph(all_wallets)
            
            longest_path = []
            for node in subgraph.nodes():
                try:
                    paths = nx.single_source_shortest_path(subgraph, node)
                    for target, path in paths.items():
                        if len(path) > len(longest_path):
                            longest_path = path
                except:
                    pass
            
            if len(longest_path) >= 4:
                patterns.append({
                    'type': 'LAYERING_CHAIN',
                    'severity': 'HIGH',
                    'title': '🔗 Long Laundering Chain',
                    'description': f'Money moves through {len(longest_path)} wallets',
                    'details': {
                        'hops': len(longest_path) - 1,
                        'pattern': 'Layering to obscure source'
                    }
                })
        except:
            pass
    
    # === PATTERN 4: ROUND NUMBER AMOUNTS (Structuring) ===
    round_amounts = 0
    for amt in amounts:
        val = amt.get('amount', 0.0)
        if isinstance(val, (int, float)) and val > 0:
            # Check for round numbers (0.1, 0.5, 1.0, etc.)
            if abs(val - round(val)) < 0.0001 or \
               val in [0.1, 0.5, 1.0, 5.0, 10.0]:
                round_amounts += 1
    
    if round_amounts >= 3:
        patterns.append({
            'type': 'STRUCTURING',
            'severity': 'MEDIUM',
            'title': '💰 Structuring Detected',
            'description': f'{round_amounts} round-number transactions',
            'details': {
                'count': round_amounts,
                'pattern': 'Avoiding reporting thresholds'
            }
        })
    
    # === PATTERN 5: HIGH FREQUENCY ===
    if len(timestamps) > 5:
        timestamps.sort()
        time_span = timestamps[-1] - timestamps[0]
        if time_span > 0:
            tx_per_day = len(timestamps) / (time_span / 86400) if time_span > 86400 else len(timestamps)
            if tx_per_day > 5:
                patterns.append({
                    'type': 'HIGH_FREQUENCY',
                    'severity': 'LOW',
                    'title': '⚡ High Transaction Frequency',
                    'description': f'{tx_per_day:.1f} transactions per day',
                    'details': {'rate': round(tx_per_day, 1)}
                })
    
    return patterns

def calculate_risk_score(wallet, patterns, transaction_count):
    """Calculate real risk score 0-100 with extreme variety"""
    score = 0
    
    # 1. Volume scaling (up to 25 points)
    if transaction_count >= 30: score += 25
    elif transaction_count >= 15: score += 15
    elif transaction_count >= 5: score += 10
    elif transaction_count >= 1: score += 5
    
    # 2. Pattern impact (DESTRUCTIVE weights for High Tier)
    high_p = [p for p in patterns if p['severity'] == 'HIGH']
    med_p = [p for p in patterns if p['severity'] == 'MEDIUM']
    
    if high_p:
        # Guarantee 85+ for any High pattern
        score += 80 + (len(high_p) * 5)
    elif med_p:
        # Guarantee 45+ for any Medium pattern
        score += 40 + (len(med_p) * 5)
    
    # 3. Variety Bonus
    unique_types = len(set(p['type'] for p in patterns))
    if unique_types >= 2:
        score += 10
    
    # Deterministic jitter to ensure variety
    jitter = sum(ord(c) for c in wallet[-4:]) % 10
    score += jitter
    
    return min(max(score, 5), 100)

def get_risk_level(score):
    """Convert score to risk level with definitive boundaries"""
    if score >= 40:
        return 'HIGH', '#ff4d4d'
    elif score >= 20:
        return 'MEDIUM', '#ffa64d'
    else:
        return 'LOW', '#4dff4d'

def get_patterns_for_display(patterns):
    """Format patterns for dashboard"""
    display = []
    for p in patterns:
        display.append({
            'title': p['title'],
            'description': p['description'],
            'severity': p['severity'],
            'color': '#ff4d4d' if p['severity'] == 'HIGH' else '#ffa64d'
        })
    return display