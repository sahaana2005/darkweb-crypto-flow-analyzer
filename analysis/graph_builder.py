import networkx as nx

def build_graph(wallet, txs):
    G = nx.DiGraph()

    # add wallet node
    G.add_node(wallet)

    # add transactions connected to wallet
    for tx in txs:
        G.add_node(tx)
        G.add_edge(wallet, tx)

    return G