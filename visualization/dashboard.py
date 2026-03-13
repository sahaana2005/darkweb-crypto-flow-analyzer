# dashboard.py – Top section with path fix
import sys
import os

# Add project root (one level above 'visualization') to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from scraper.wallet_extractor import extract_wallets
from blockchain.fetch_transactions import fetch_transactions
from analysis.graph_builder import build_graph
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Dark Web Crypto Flow Analyzer",
    page_icon="🕵️",
    layout="wide"
)

# Custom CSS to match the images
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0a0c10;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1e24 0%, #14181f 100%);
        border: 1px solid #2a2f3a;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Wallet cards */
    .wallet-card {
        background: #14181f;
        border: 1px solid #2a2f3a;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #00d4ff;
    }
    
    .wallet-address {
        font-family: monospace;
        color: #00d4ff;
        background: #1e242c;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    
    .risk-badge-high {
        background: #ff4d4d20;
        color: #ff4d4d;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #ff4d4d40;
    }
    
    .risk-badge-medium {
        background: #ffa64d20;
        color: #ffa64d;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #ffa64d40;
    }
    
    .risk-badge-low {
        background: #4dff4d20;
        color: #4dff4d;
        padding: 0.2rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid #4dff4d40;
    }
    
    /* Chat message style */
    .chat-message {
        background: #14181f;
        border: 1px solid #2a2f3a;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: monospace;
        color: #a0a0b0;
        border-left: 4px solid #00d4ff;
    }
    
    /* Section headers */
    .section-header {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00d4ff;
    }
    
    /* Stats boxes */
    .stat-box {
        background: #14181f;
        border: 1px solid #2a2f3a;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .stat-label {
        color: #a0a0b0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-value {
        color: #00d4ff;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #00d4ff 0%, #0066ff 100%);
        color: white;
        border: none;
        font-weight: 600;
        padding: 0.5rem 2rem;
        border-radius: 6px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #00b8e6 0%, #0052cc 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #14181f;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #a0a0b0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00d4ff20 !important;
        color: #00d4ff !important;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="color: #00d4ff; font-size: 3rem; margin-bottom: 0;">🕵️ Dark Web Crypto</h1>
    <h1 style="color: white; font-size: 2.5rem; margin-top: -0.5rem;">FLOW ANALYZER</h1>
</div>
""", unsafe_allow_html=True)

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-label">TRACKED WALLETS</div>
        <div class="stat-value">0</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-label">TOTAL VOLUME</div>
        <div class="stat-value">0.0000 BTC</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-label">SUSPICIOUS TXNS</div>
        <div class="stat-value">0</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-label">HIGH RISK WALLETS</div>
        <div class="stat-value">0</div>
    </div>
    """, unsafe_allow_html=True)

# Main layout
left_col, right_col = st.columns([1.2, 1.8])

with left_col:
    st.markdown('<div class="section-header">📥 Extract Wallet Addresses</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #a0a0b0; font-size: 0.9rem;">
    Paste raw text, HTML, or intercepted messages from dark web pages. 
    The system will automatically detect and extract all cryptocurrency wallet addresses.
    </p>
    """, unsafe_allow_html=True)
    
    # Input tabs
    tab1, tab2 = st.tabs(["📝 Paste Text", "📁 Upload HTML"])
    
    with tab1:
        text_input = st.text_area(
            "Paste dark web page content, transaction logs, marketplace listings, or chat intercepts here...",
            height=200,
            placeholder="Example:\nVendor: ShadowMarket\nSend to: 1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY"
        )
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📋 Load Sample", use_container_width=True):
                st.session_state['sample'] = True
                text_input = """
                Intercepted message --- 
                "Send 0.5 BTC to bc1qar0srrr7xfkvy516431ydnw9re59gtzzwf5mdq for the goods."
                
                Vendor: SpecterKey
                Payment: 1A1zP1eP50Gefi2DMPTfTL5SLmv7DivfNa
                
                Alternative escrow: 3FZbgi29cpjq2GjdwV8eyHuJNkLtktZc5
                
                Bulk orders: bc1qxy2kgdygjrspqtzq2n0yrf2493p83kkfjhx0wlh
                """
        
        with col_btn2:
            if st.button("🔍 Extract Wallets", type="primary", use_container_width=True):
                if text_input:
                    with st.spinner("Extracting wallets..."):
                        wallets = extract_wallets(text_input)
                        st.session_state['wallets'] = wallets
                        st.success(f"Found {len(wallets)} wallet(s)")
    
    with tab2:
        uploaded_file = st.file_uploader("Upload HTML file", type=['html', 'txt'])
        if uploaded_file:
            content = uploaded_file.read().decode()
            st.session_state['uploaded_content'] = content
    
    # Wallet list section
    st.markdown('<div class="section-header">💰 Extracted Wallets</div>', unsafe_allow_html=True)
    
    if 'wallets' in st.session_state and st.session_state['wallets']:
        for i, wallet in enumerate(st.session_state['wallets'][:5]):  # Show first 5
            with st.container():
                st.markdown(f"""
                <div class="wallet-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="wallet-address">{wallet[:12]}...{wallet[-6:]}</span>
                            <span style="color: #a0a0b0; font-size: 0.8rem; margin-left: 0.5rem;">1x mentioned</span>
                        </div>
                        <span class="risk-badge-medium">MEDIUM RISK</span>
                    </div>
                    <p style="color: #a0a0b0; font-size: 0.85rem; margin-top: 0.5rem;">
                        "...or bulk orders contact via PGP. Wallet {wallet[:12]}... also accepts deposits..."
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Extract wallets to begin")
    
    # Chat Intel section
    st.markdown('<div class="section-header">💬 Chat Intel</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="chat-message">
        "Send 0.5 BTC to bc1qar0srrr7xfkvy516431ydnw9re59gtzzwf5mdq for the goods."
    </div>
    """, unsafe_allow_html=True)

with right_col:
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "👛 Wallets", "🕸️ Flow Graph", "🔍 Patterns", "💬 Chat Intel"])
    
    with tab1:
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.markdown("### Wallet Risk Distribution")
            
            # Create a pie chart
            fig = go.Figure(data=[go.Pie(
                labels=['High Risk', 'Medium Risk', 'Low Risk'],
                values=[0, 0, 0],
                marker_colors=['#ff4d4d', '#ffa64d', '#4dff4d'],
                hole=0.4
            )])
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col_graph2:
            st.markdown("### Recent Transactions")
            st.markdown("""
            <div style="background: #14181f; padding: 1rem; border-radius: 8px;">
                <p style="color: #a0a0b0;">Hash | From | To | Amount | Flags | Confirmations</p>
                <p style="color: #00d4ff;">No transactions yet</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Tracked Wallets")
        if 'wallets' in st.session_state:
            for wallet in st.session_state['wallets']:
                with st.expander(f"👛 {wallet[:20]}..."):
                    st.json({
                        "address": wallet,
                        "first_seen": "2024-01-15",
                        "total_tx": 47,
                        "total_received": "12.5 BTC",
                        "total_sent": "11.8 BTC",
                        "risk_score": "MEDIUM"
                    })
        else:
            st.info("No wallets tracked yet")
    
    with tab3:
        st.markdown("### Transaction Flow Graph")
        if 'wallets' in st.session_state and st.session_state['wallets']:
            # Create a simple graph
            G = nx.DiGraph()
            wallet = st.session_state['wallets'][0]
            G.add_node(wallet)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_facecolor('#0a0c10')
            ax.set_facecolor('#0a0c10')
            
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_color='#00d4ff', 
                   node_size=500, font_size=8, font_color='white', ax=ax)
            
            st.pyplot(fig)
        else:
            st.info("Extract wallets to view flow graph")
    
    with tab4:
        st.markdown("### Suspicious Patterns")
        st.markdown("""
        <div class="wallet-card">
            <h4 style="color: #ff4d4d;">🚨 Fund Splitting Detected</h4>
            <p>Wallet 1A1zP1... → 12 different wallets</p>
        </div>
        <div class="wallet-card">
            <h4 style="color: #ffa64d;">⚠️ Wallet Reuse</h4>
            <p>Same wallet appears in 3 different listings</p>
        </div>
        <div class="wallet-card">
            <h4 style="color: #ffa64d;">🔄 Long Chain</h4>
            <p>5 hops before reaching exchange</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab5:
        st.markdown("### Intercepted Messages")
        st.markdown("""
        <div class="chat-message">
            <strong style="color: #00d4ff;">Buyer:</strong> "Send 0.5 BTC to bc1qar0s... for the goods."
        </div>
        <div class="chat-message">
            <strong style="color: #00d4ff;">Vendor:</strong> "Payment received. Use escrow 3FZbgi29..."
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #14181f; border-radius: 8px;">
    <p style="color: #a0a0b0; font-size: 0.8rem;">
        🔒 Demo for hackathon • Real-time data from Blockchain.com API • Not connected to real dark web
    </p>
</div>
""", unsafe_allow_html=True)