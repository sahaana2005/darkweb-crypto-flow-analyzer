import networkx as nx
from collections import Counter

def build_graph(source_wallet, transactions):
    """
    Build wallet-to-wallet transaction graph
    transactions: FULL transaction data from API
    """
    G = nx.DiGraph()
    
    # Add source wallet
    G.add_node(source_wallet, 
               type='source',
               label=source_wallet[:8])
    
    if not transactions:
        return G
    
    # Track connected wallets
    connected_wallets = set()
    
    for tx in transactions:
        tx_hash = tx.get('hash', '')
        
        # === GET INPUTS (wallets that sent TO this wallet) ===
        inputs = tx.get('inputs', [])
        for inp in inputs:
            prev_out = inp.get('prev_out', {})
            from_wallet = prev_out.get('addr')
            
            if from_wallet and from_wallet != source_wallet:
                # Add the sending wallet
                G.add_node(from_wallet,
                          type='wallet',
                          label=from_wallet[:8])
                
                # Add edge FROM sender TO source wallet
                G.add_edge(from_wallet, source_wallet,
                          tx=tx_hash,
                          amount=prev_out.get('value', 0) / 100000000,  # Convert to BTC
                          type='incoming')
                
                connected_wallets.add(from_wallet)
        
        # === GET OUTPUTS (wallets this wallet sent TO) ===
        outputs = tx.get('out', [])
        for out in outputs:
            to_wallet = out.get('addr')
            
            if to_wallet and to_wallet != source_wallet:
                # Add the receiving wallet
                G.add_node(to_wallet,
                          type='wallet',
                          label=to_wallet[:8])
                
                # Add edge FROM source wallet TO receiver
                G.add_edge(source_wallet, to_wallet,
                          tx=tx_hash,
                          amount=out.get('value', 0) / 100000000,
                          type='outgoing')
                
                connected_wallets.add(to_wallet)
    
    print(f"✅ Graph built: {len(G.nodes())} nodes, {len(G.edges())} edges")
    return G

def get_flow_summary(G, wallet):
    """
    Get summary of money flow for a wallet
    """
    summary = {
        'incoming': [],
        'outgoing': [],
        'total_received': 0,
        'total_sent': 0,
        'unique_senders': set(),
        'unique_recipients': set()
    }
    
    if wallet not in G:
        return summary
    
    # Get incoming edges
    for pred in G.predecessors(wallet):
        edge_data = G.get_edge_data(pred, wallet)
        if edge_data:
            summary['incoming'].append({
                'from': pred,
                'amount': edge_data.get('amount', 0),
                'tx': edge_data.get('tx', '')
            })
            summary['total_received'] += edge_data.get('amount', 0)
            summary['unique_senders'].add(pred)
    
    # Get outgoing edges
    for succ in G.successors(wallet):
        edge_data = G.get_edge_data(wallet, succ)
        if edge_data:
            summary['outgoing'].append({
                'to': succ,
                'amount': edge_data.get('amount', 0),
                'tx': edge_data.get('tx', '')
            })
            summary['total_sent'] += edge_data.get('amount', 0)
            summary['unique_recipients'].add(succ)
    
    # Convert sets to counts
    summary['unique_senders'] = len(summary['unique_senders'])
    summary['unique_recipients'] = len(summary['unique_recipients'])
    
    return summary