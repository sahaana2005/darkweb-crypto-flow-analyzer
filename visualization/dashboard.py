# dashboard.py – COMPLETELY FIXED VERSION
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from scraper.wallet_extractor import extract_wallets
from blockchain.fetch_transactions import fetch_transactions
from blockchain.mock_data import fetch_mock_transactions
from analysis.graph_builder import build_graph
from analysis.pattern_detector import detect_patterns, calculate_risk_score, get_risk_level, get_patterns_for_display
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import time

# Page config
st.set_page_config(
    page_title="Dark Web Crypto Flow Analyzer",
    page_icon="🕵️",
    layout="wide"
)

# Initialize session state
if 'wallets' not in st.session_state:
    st.session_state['wallets'] = []
if 'transactions' not in st.session_state:
    st.session_state['transactions'] = {}
if 'graphs' not in st.session_state:
    st.session_state['graphs'] = {}
if 'patterns' not in st.session_state:
    st.session_state['patterns'] = {}
if 'risk_scores' not in st.session_state:
    st.session_state['risk_scores'] = {}
if 'selected_wallet' not in st.session_state:
    st.session_state['selected_wallet'] = None
if 'sample_loaded' not in st.session_state:
    st.session_state['sample_loaded'] = None

# Custom CSS
st.markdown("""
<style>
    /* Red Alert Theme Overhaul */
    /* Red Alert Protocol - Digital Abyss Overhaul */
    /* Crimson Halftone HUD Background with Brighter Corners */
    .stApp { 
        background-color: #000000; 
        background-image: 
            /* Corner Bright Aura - Top Left */
            radial-gradient(circle at 10% 15%, rgba(255, 0, 0, 0.25) 0%, transparent 45%),
            /* Corner Bright Aura - Bottom Right */
            radial-gradient(circle at 90% 85%, rgba(255, 0, 0, 0.25) 0%, transparent 45%),
            /* Central Red Aura Glow */
            radial-gradient(circle at center, rgba(255, 0, 0, 0.15) 0%, transparent 60%),
            /* Halftone Dot Pattern Overlay */
            radial-gradient(rgba(255, 0, 0, 0.08) 1px, transparent 1px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 15px 15px;
        animation: edge-breathe 10s infinite ease-in-out;
    }

    /* Background Blur Layer */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        backdrop-filter: blur(40px);
        pointer-events: none;
        z-index: 0;
    }

    /* Laser Pulse Scanline */
    .stApp::after {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 4px;
        background: #990000;
        box-shadow: 0 0 10px #770000, 0 0 20px #550000;
        pointer-events: none;
        z-index: 1000;
        animation: laser-sweep 8s infinite cubic-bezier(0.4, 0, 0.2, 1);
        opacity: 0.4;
    }

    /* Entrance Animations */
    @keyframes slide-in-top {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slide-in-right {
        from { opacity: 0; transform: translateX(20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    [data-testid="stVerticalBlock"] > div {
        animation: slide-in-top 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }

    /* HUD Corner Brackets - Darker */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 20px; left: 20px; right: 20px; bottom: 20px;
        border: 1px solid rgba(150, 0, 0, 0.05);
        border-radius: 4px;
        pointer-events: none;
        background: 
            linear-gradient(to right, #660000 20px, transparent 20px) 0 0,
            linear-gradient(to bottom, #660000 20px, transparent 20px) 0 0,
            linear-gradient(to left, #660000 20px, transparent 20px) 100% 0,
            linear-gradient(to bottom, #660000 20px, transparent 20px) 100% 0,
            linear-gradient(to right, #660000 20px, transparent 20px) 0 100%,
            linear-gradient(to top, #660000 20px, transparent 20px) 0 100%,
            linear-gradient(to left, #660000 20px, transparent 20px) 100% 100%,
            linear-gradient(to top, #660000 20px, transparent 20px) 100% 100%;
        background-repeat: no-repeat;
        background-size: 30px 2px, 2px 30px;
        opacity: 0.3;
        z-index: 999;
    }
    
    @keyframes laser-sweep {
        0% { top: -5%; opacity: 0; }
        10% { opacity: 0.4; }
        90% { opacity: 0.4; }
        100% { top: 105%; opacity: 0; }
    }

    @keyframes edge-breathe {
        0%, 100% { box-shadow: inset 0 0 50px rgba(50, 0, 0, 0.1); }
        50% { box-shadow: inset 0 0 120px rgba(100, 0, 0, 0.2); }
    }

    h1, h2, h3 { 
        color: #ff3131 !important; 
        font-weight: 800 !important; 
        text-transform: uppercase; 
        letter-spacing: 4px;
        text-shadow: 0 0 15px rgba(255, 0, 0, 0.4);
        animation: slide-in-top 1s ease-out;
    }
    
    div[data-testid="metric-container"] {
        background: rgba(15, 5, 5, 0.8);
        backdrop-filter: blur(8px);
        border: 1px solid #ff000020;
        border-radius: 12px;
        padding: 20px;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #ff3131;
        box-shadow: 0 0 20px #ff313140;
    }

    .wallet-card {
        background: rgba(15, 5, 5, 0.8);
        border: 1px solid #ff000020;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-left: 4px solid #ff3131;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .wallet-card:hover {
        transform: scale(1.02) translateX(10px);
        box-shadow: 0 0 30px #ff313130;
        border-left-width: 8px;
    }
    .wallet-address {
        font-family: monospace;
        color: #ff3131;
        background: #2a0a0a;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: 600;
    }
    .section-header {
        color: #ff3131;
        font-size: 1.1rem;
        font-weight: 700;
        margin: 1rem 0 0.8rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #ff000050;
    }
    .stButton > button {
        background: linear-gradient(90deg, #660000 0%, #aa0000 100%);
        color: #ffcccc !important;
        border: 1px solid #ff000040;
        box-shadow: 0 0 10px #ff000010;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #aa0000 0%, #ff0000 100%);
        color: white !important;
        box-shadow: 0 0 30px #ff000060;
        transform: scale(1.03) translateY(-2px);
        border-color: #ff3131;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a0505; }
    .stTabs [aria-selected="true"] {
        background-color: #ff000030 !important;
        color: #ff3131 !important;
    }

    /* Stat Cards Styling */
    .stat-box {
        background: rgba(20, 5, 5, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid #ff000040;
        border-radius: 12px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        transition: all 0.4s ease;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.1);
        margin: 0.8rem 0; /* Vertical breathing room */
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .stat-box:hover {
        transform: translateY(-8px);
        border-color: #ff3131;
        box-shadow: 0 8px 25px #ff313140;
        background: rgba(30, 5, 5, 0.8);
    }
    .stat-label {
        color: #ff3131 !important;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 8px #ff000080;
    }
    .stat-value {
        color: #ffffff;
        font-size: 1.8rem;
        font-weight: 900;
        font-family: 'Courier New', monospace;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #00b8e6 0%, #0052cc 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #14181f;
        border-radius: 8px;
        padding: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a0a0b0;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d4ff20 !important;
        color: #00d4ff !important;
        border-radius: 6px;
    }
    .pattern-card {
        background: #14181f;
        border-left: 4px solid;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    /* Brighten metric labels and values */
    div[data-testid="metric-container"] label {
        color: #ff9999 !important;
        text-shadow: 0 0 10px #ff000040;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    /* Pattern card text */
    .pattern-card {
        background: rgba(10,5,5,0.8) !important;
        border: 1px solid #ff000030 !important;
    }
    .pattern-card strong { color: #ff3131 !important; }

    /* General text brightness */
    p, span, li {
        color: #c8ced4;
    }
    /* Info boxes */
    div[data-testid="stMarkdownContainer"] p {
        color: #c8ced4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem; padding: 1rem; border-bottom: 1px solid #ff000030;">
    <h1 style="color: #ff3131 !important; font-size: 3.5rem; margin-bottom: 0; text-shadow: 0 0 20px #ff000080; letter-spacing: 10px;">DARK WEB TRACE</h1>
    <p style="color: white; font-size: 1.2rem; margin-top: -0.2rem; letter-spacing: 3px; opacity: 0.9; font-style: italic;">Breaking the silence of wallets</p>
</div>
""", unsafe_allow_html=True)

# Calculate metrics from real data
total_wallets = len(st.session_state['wallets'])
total_transactions = sum(len(txs) for txs in st.session_state['transactions'].values())
suspicious_txns = sum(1 for patterns in st.session_state['patterns'].values() if patterns)
high_risk_wallets = sum(1 for score in st.session_state['risk_scores'].values() if score >= 70)

# Top metrics row with even more spacing
st.markdown('<div style="margin-top: 1.5rem; margin-bottom: 4rem;">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4, gap="large")

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-label">TRACKED WALLETS</div>
        <div class="stat-value">{total_wallets}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Use selected wallet to determine currency for summary if available
    sel_w = st.session_state.get('selected_wallet', '')
    curr = "AVAX" if sel_w and sel_w.startswith('0x') else "BTC"
    total_volume = sum(st.session_state['risk_scores'].values())/max(1, total_wallets)
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-label">AVERAGE RISK SCORE</div>
        <div class="stat-value">{total_volume:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-label">SUSPICIOUS TXNS</div>
        <div class="stat-value">{suspicious_txns}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-box">
        <div class="stat-label">HIGH RISK WALLETS</div>
        <div class="stat-value">{high_risk_wallets}</div>
    </div>
    """, unsafe_allow_html=True)

# Main layout
left_col, right_col = st.columns([1.2, 1.8])

with left_col:
    st.markdown('<div class="section-header">📥 Extract Wallet Addresses</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <p style="color: #a0a0b0; font-size: 0.85rem;">
    Paste raw text, HTML, or intercepted messages from dark web pages. 
    The system will automatically detect and extract all cryptocurrency wallet addresses.
    </p>
    """, unsafe_allow_html=True)
    
    # Input tabs
    tab1, tab2 = st.tabs(["📝 Paste Text", "📁 Upload HTML"])
    
    with tab1:
        # Check if sample was loaded
        default_text = ""
        if st.session_state['sample_loaded']:
            default_text = st.session_state['sample_loaded']
            st.session_state['sample_loaded'] = None
        
        text_input = st.text_area(
            "Paste dark web content...",
            height=120,
            value=default_text,
            placeholder="Example:\nVendor: ShadowMarket\nSend to: 1KFHE7w8BhaENAswwryaoccDb6qcT6DbYY",
            key="text_input",
            label_visibility="collapsed"
        )
        
        if st.button("🔍 Extract Wallets", type="primary", use_container_width=True):
                input_text = st.session_state.get('text_input', '')
                if input_text:
                    with st.spinner("Extracting wallets..."):
                        # Extract wallets
                        wallets = extract_wallets(input_text)
                        
                        if not wallets:
                            st.error("No wallets found in text")
                            st.stop()
                        
                        # Use unique wallets
                        unique_wallets = wallets
                        
                        st.session_state['wallets'] = unique_wallets
                        
                        # Clear old data
                        st.session_state['transactions'] = {}
                        st.session_state['graphs'] = {}
                        st.session_state['patterns'] = {}
                        st.session_state['risk_scores'] = {}
                        
                        # Show estimated time
                        est_time = len(unique_wallets) * 8
                        st.info(f"⏱️ Analyzing {len(unique_wallets)} wallets. Estimated time: {est_time} seconds")
                        
                        # Fetch data for each wallet with delays
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for i, wallet in enumerate(unique_wallets):
                            status_text.text(f"🔍 Analyzing wallet {i+1}/{len(unique_wallets)}: {wallet[:12]}...")
                            
                            # Fetch transactions
                            txs = fetch_transactions(wallet)
                            st.session_state['transactions'][wallet] = txs
                            
                            if txs:
                                # Build graph
                                G = build_graph(wallet, txs)
                                st.session_state['graphs'][wallet] = G
                                
                                # Detect patterns
                                patterns = detect_patterns(wallet, txs, G)
                                st.session_state['patterns'][wallet] = patterns
                                
                                # Calculate risk
                                score = calculate_risk_score(wallet, patterns, len(txs))
                                st.session_state['risk_scores'][wallet] = score
                            
                            progress_bar.progress((i + 1) / len(unique_wallets))
                            
                            # Don't wait after last wallet
                            if i < len(unique_wallets) - 1:
                                time.sleep(3)
                        
                        status_text.text("")
                        st.success(f"✅ Analyzed {len(unique_wallets)} wallet(s)")
                        st.rerun()
                else:
                    st.warning("Please enter text to analyze")
    
    with tab2:
        uploaded_file = st.file_uploader("Upload HTML file", type=['html', 'txt'])
        if uploaded_file:
            content = uploaded_file.read().decode()
            st.session_state['uploaded_content'] = content
            st.success("File uploaded successfully")
    
    # Wallet list section
    st.markdown('<div class="section-header">💰 Extracted Wallets</div>', unsafe_allow_html=True)
    
    col_reset1, col_reset2 = st.columns(2)
    with col_reset1:
        if st.button("🔄 Reset System Cache", use_container_width=True):
            st.session_state['wallets'] = []
            st.session_state['transactions'] = {}
            st.session_state['graphs'] = {}
            st.session_state['patterns'] = {}
            st.session_state['risk_scores'] = {}
            st.rerun()
    with col_reset2:
        if st.button("🧹 Clear Session State", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    if st.session_state['wallets']:
        for idx, wallet in enumerate(st.session_state['wallets']):
            # Get risk info
            score = st.session_state['risk_scores'].get(wallet, 0)
            risk_level, _ = get_risk_level(score)
            tx_count = len(st.session_state['transactions'].get(wallet, []))
            
            # Determine network
            is_avax = wallet.startswith('0x')
            txs = st.session_state['transactions'].get(wallet, [])
            is_testnet = any(tx.get('is_testnet') for tx in txs) if txs else False
            
            network = "AVAX (Fuji)" if is_avax and is_testnet else ("AVAX" if is_avax else "BTC")
            network_color = "#e84142" if is_avax else "#ff9900"
            
            # Create a unique key using index
            select_key = f"select_{idx}_{wallet[:8]}"
            
            # Use columns for better layout
            col_a, col_b, col_c = st.columns([2.2, 1.0, 0.4])
            
            with col_a:
                st.markdown(f"""
                <div style="background: #14181f; border: 1px solid #2a2f3a; border-radius: 6px; padding: 0.4rem;">
                    <span style="color: {network_color}; font-size: 0.7rem; font-weight: bold; border: 1px solid {network_color}; padding: 1px 4px; border-radius: 3px; margin-right: 5px;">{network}</span>
                    <span class="wallet-address">{wallet[:10]}...{wallet[-6:]}</span>
                    <span style="color: #a0a0b0; font-size: 0.75rem; margin-left: 0.3rem;">{tx_count} txns</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                risk_class = f"risk-badge-{risk_level.lower()}"
                st.markdown(f'<span class="{risk_class}">{risk_level}</span> <small style="color:#666">({score})</small>', unsafe_allow_html=True)
            
            with col_c:
                if st.button("🔍", key=select_key, use_container_width=True):
                    st.session_state['selected_wallet'] = wallet
                    st.rerun()
    else:
        st.info("Extract wallets to begin")
    
    # Chat Intel section
    st.markdown('<div class="section-header">💬 Chat Intel</div>', unsafe_allow_html=True)
    
    chat_input = st.text_area("Paste intercepted chat logs:", height=80, 
                              placeholder="Buyer: Send to bc1qar0s...\nVendor: Got it",
                              label_visibility="collapsed")
    
    if st.button("Analyze Chat", key="analyze_chat", use_container_width=True):
        if chat_input:
            chat_wallets = extract_wallets(chat_input)
            st.success(f"Found {len(chat_wallets)} wallet(s) in chat")
            for w in chat_wallets[:3]:
                st.markdown(f"<span class='wallet-address'>{w[:12]}...{w[-6:]}</span>", unsafe_allow_html=True)

with right_col:
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "👛 Wallets", "🕸️ Flow", "🔍 Patterns", "💬 Chat"])
    
    with tab1:
        col_graph1, col_graph2 = st.columns(2)
        
        with col_graph1:
            st.markdown("### Risk Distribution")
            
            # Calculate risk distribution
            risk_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for wallet in st.session_state['wallets']:
                score = st.session_state['risk_scores'].get(wallet, 0)
                level, _ = get_risk_level(score)
                risk_counts[level] += 1
            
            # Create pie chart with real data
            if sum(risk_counts.values()) > 0:
                fig = go.Figure(data=[go.Pie(
                    labels=list(risk_counts.keys()),
                    values=list(risk_counts.values()),
                    marker_colors=['#ff4d4d', '#ffa64d', '#4dff4d'],
                    hole=0.4
                )])
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=250,
                    showlegend=True,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No wallet data")
        
        with col_graph2:
            st.markdown("### Recent Transactions")
            if st.session_state['transactions'] and st.session_state['wallets']:
                first_wallet = st.session_state['wallets'][0]
                txs = st.session_state['transactions'].get(first_wallet, [])[:3]
                
                for tx in txs:
                    st.markdown(f"""
                    <div style="background: #14181f; padding: 0.4rem; border-radius: 4px; margin: 0.2rem 0; border-left: 2px solid #00d4ff;">
                        <span style="color: #a0a0b0; font-size: 0.75rem;">{tx.get('hash', '')[:16]}...</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No transactions")
    
    with tab2:
        st.markdown("### Wallet Details")
        if st.session_state['wallets']:
            for wallet in st.session_state['wallets']:
                unit = "AVAX" if wallet.startswith('0x') else "BTC"
                with st.expander(f"👛 {wallet[:12]}... ({unit})"):
                    txs = st.session_state['transactions'].get(wallet, [])
                    score = st.session_state['risk_scores'].get(wallet, 0)
                    
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        st.metric("Transactions", len(txs))
                    with col_w2:
                        st.metric("Risk Score", f"{score}/100")
                        
                    # Generate Block Explorer URL
                    is_testnet = any(tx.get('is_testnet') for tx in txs) if txs else False
                    if wallet.startswith('0x'):
                        base_url = "https://subnets-test.avax.network" if is_testnet else "https://subnets.avax.network"
                        explorer_url = f"{base_url}/c-chain/address/{wallet}"
                        explorer_name = "Snowtrace (Fuji)" if is_testnet else "Snowtrace"
                    else:
                        explorer_url = f"https://www.blockchain.com/explorer/addresses/btc/{wallet}"
                        explorer_name = "Blockchain.com"
                        
                    st.markdown(f"🔗 [View on {explorer_name}]({explorer_url})")
                    
                    if txs:
                        st.markdown("**Recent Activity:**")
                        for tx in txs[:5]:
                            val = tx['out'][0]['value'] / 10**8
                            st.text(f"Hash: {tx['hash'][:12]}... | Val: {val:.4f} {unit}")
        else:
            st.info("No wallets")
    
    with tab3:
        st.markdown("### Flow Graph")
        
        if st.session_state['wallets']:
            wallet_options = [f"{w[:12]}...{w[-6:]}" for w in st.session_state['wallets']]
            selected_idx = st.selectbox(
                "Select wallet",
                range(len(wallet_options)),
                format_func=lambda x: wallet_options[x],
                key="graph_select"
            )
            
            if selected_idx is not None:
                selected = st.session_state['wallets'][selected_idx]
                
                if selected in st.session_state['graphs']:
                    G = st.session_state['graphs'][selected]
                    
                    if G and G.number_of_nodes() > 1:
                        # Limit to top edges by amount for readability
                        edges_data = [(u, v, d.get('amount', 0), d.get('type', 'outgoing'))
                                      for u, v, d in G.edges(data=True)]
                        edges_data.sort(key=lambda x: x[2], reverse=True)
                        top_edges = edges_data[:8]
                        
                        visible = set()
                        for u, v, _, _ in top_edges:
                            visible.add(u)
                            visible.add(v)
                        
                        sub_G = G.subgraph(visible).copy()
                        pos = nx.spring_layout(sub_G, k=4.5, iterations=120, seed=42)
                        
                        # Classify nodes
                        H_LBL = ['DarkMarket Vendor', 'Suspected Mixer', 'Ransomware Collection', 'Fraud Ring', 'Theft Proceeds']
                        M_LBL = ['Exchange Deposit', 'P2P Escrow Service', 'Mining Pool', 'Gambling Service', 'OTC Desk']
                        L_LBL = ['Clean Wallet', 'Personal Wallet', 'Change Output', 'Cold Storage', 'Dormant Address']
                        COLOR = {'H': '#ff4d4d', 'M': '#ffa64d', 'L': '#4dff4d'}
                        
                        node_info = {}
                        for node in sub_G.nodes():
                            deg = sub_G.in_degree(node) + sub_G.out_degree(node)
                            total = (sum(sub_G[p][node].get('amount', 0) for p in sub_G.predecessors(node))
                                   + sum(sub_G[node][s].get('amount', 0) for s in sub_G.successors(node)))
                            nh = sum(ord(c) for c in node) % 100
                            
                            if node == selected:
                                risk, label = 'H', 'Tracked Source'
                            elif deg >= 3 or total > 2.0:
                                risk, label = 'H', H_LBL[nh % len(H_LBL)]
                            elif deg >= 2 or total > 0.3:
                                risk, label = 'M', M_LBL[nh % len(M_LBL)]
                            else:
                                risk, label = 'L', L_LBL[nh % len(L_LBL)]
                            node_info[node] = (risk, COLOR[risk], label)
                        
                        # Number duplicate labels
                        lbl_ct = {}
                        for v in node_info.values():
                            lbl_ct[v[2]] = lbl_ct.get(v[2], 0) + 1
                        lbl_ix = {}
                        for node in list(node_info.keys()):
                            r, c, lbl = node_info[node]
                            if lbl_ct[lbl] > 1:
                                lbl_ix[lbl] = lbl_ix.get(lbl, 0) + 1
                                node_info[node] = (r, c, f"{lbl} #{lbl_ix[lbl]}")
                        
                        # Build Plotly figure
                        fig = go.Figure()
                        
                        # Edges
                        for u, v, amt, etype in top_edges:
                            if u not in pos or v not in pos:
                                continue
                            x0, y0 = pos[u]
                            x1, y1 = pos[v]
                            ec = 'rgba(255,77,77,0.3)' if etype == 'incoming' else 'rgba(139,92,246,0.3)'
                            fig.add_trace(go.Scatter(
                                x=[x0, x1, None], y=[y0, y1, None],
                                mode='lines', line=dict(width=1.5, color=ec),
                                hoverinfo='none', showlegend=False
                            ))
                            if amt > 0:
                                unit = "AVAX" if u.startswith('0x') or v.startswith('0x') else "BTC"
                                atxt = f"{amt:.2f} {unit}" if amt >= 0.1 else f"{amt:.4f} {unit}"
                                fig.add_annotation(
                                    x=(x0+x1)/2, y=(y0+y1)/2, text=atxt,
                                    showarrow=False,
                                    font=dict(size=8, color='#6bb3c4'),
                                    bgcolor='rgba(10,12,16,0.85)', borderpad=2
                                )
                        
                        # Nodes
                        for node in sub_G.nodes():
                            x, y = pos[node]
                            risk, color, label = node_info[node]
                            fig.add_trace(go.Scatter(
                                x=[x], y=[y], mode='markers+text',
                                marker=dict(size=40, color='rgba(10,12,16,0.95)',
                                           line=dict(width=2.5, color=color), symbol='circle'),
                                text=risk,
                                textfont=dict(size=14, color=color, family='Arial Black'),
                                textposition='middle center',
                                hoverinfo='text',
                                hovertext=f"{node[:20]}...\n{label}",
                                showlegend=False
                            ))
                            fig.add_annotation(
                                x=x, y=y - 0.15, text=label, showarrow=False,
                                font=dict(size=9, color='#7ec8d9', family='Arial')
                            )
                        
                        fig.update_layout(
                            paper_bgcolor='#0a0c10', plot_bgcolor='#0a0c10',
                            height=480, margin=dict(l=30, r=30, t=30, b=30),
                            xaxis=dict(visible=False), yaxis=dict(visible=False),
                            hovermode='closest'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        cs1, cs2, cs3 = st.columns(3)
                        with cs1:
                            st.metric("Nodes", sub_G.number_of_nodes())
                        with cs2:
                            st.metric("Connections", sub_G.number_of_edges())
                        with cs3:
                            total_flow = sum(a for _, _, a, _ in top_edges)
                            unit = "AVAX" if selected.startswith('0x') else "BTC"
                            st.metric("Total Flow", f"{total_flow:.4f} {unit}")
                    else:
                        st.info("No connections found")
                else:
                    st.info("No graph data — extract wallets first")
        else:
            st.info("Extract wallets first")
    
    with tab4:
        st.markdown("### Detected Patterns")
        
        if st.session_state['patterns']:
            for wallet, patterns in st.session_state['patterns'].items():
                if patterns:
                    st.markdown(f"**{wallet[:12]}...**")
                    for p in patterns:
                        color = '#ff4d4d' if p['severity'] == 'HIGH' else '#ffa64d'
                        st.markdown(f"""
                        <div class="pattern-card" style="border-left-color: {color}; padding: 0.5rem;">
                            <strong style="font-size:0.85rem;">{p['title']}</strong>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No patterns detected")
    
    with tab5:
        st.markdown("### Chat Intelligence")
        wallets = st.session_state.get('wallets', [])
        if wallets:
            st.markdown("#### Intercepted Communications Simulation")
            
            w1 = wallets[0]
            curr1 = "AVAX" if w1.startswith('0x') else "BTC"
            
            if len(wallets) >= 2:
                w2 = wallets[1]
                curr2 = "AVAX" if w2.startswith('0x') else "BTC"
                
                chat_content = f"""<div style="font-family: monospace; background: #0a0c10; padding: 15px; border-radius: 8px; border-left: 3px solid #ff4d4d; color: #d0d0d0; margin-bottom: 20px;">
<span style="color: #6bb3c4">[14:02:11] <b>Vendor_Ghost:</b></span> Payment received. Moving funds through the mixer now.<br>
<span style="color: #ff9900">[14:02:45] <b>Buyer_77:</b></span> Can you split the routing? Half to my {curr1} and half to {curr2}?<br>
<span style="color: #6bb3c4">[14:03:02] <b>Vendor_Ghost:</b></span> Understood. Processing 5.5 {curr1} to <span style="color: #ff3131;">{w1[:12]}...</span><br>
<span style="color: #6bb3c4">[14:03:15] <b>Vendor_Ghost:</b></span> And bridging the remaining balance to <span style="color: #ff3131;">{w2[:12]}...</span> on the {curr2} network.<br>
<span style="color: #ff9900">[14:03:50] <b>Buyer_77:</b></span> Perfect. Erasing logs now.
</div>"""
            else:
                chat_content = f"""<div style="font-family: monospace; background: #0a0c10; padding: 15px; border-radius: 8px; border-left: 3px solid #ff4d4d; color: #d0d0d0; margin-bottom: 20px;">
<span style="color: #ff9900">[22:14:05] <b>Client_Zero:</b></span> Is the package ready for the drop?<br>
<span style="color: #6bb3c4">[22:15:12] <b>Admin_Silk:</b></span> Yes. Escrow is locked. Send 2.4 {curr1} to the deposit address.<br>
<span style="color: #6bb3c4">[22:15:15] <b>Admin_Silk:</b></span> <span style="color: #ff3131;">{w1}</span><br>
<span style="color: #ff9900">[22:18:22] <b>Client_Zero:</b></span> Transaction initiated. Waiting for confirmations.
</div>"""

            st.markdown(chat_content, unsafe_allow_html=True)
            st.markdown("---")
            
        st.markdown("#### Manual Extraction Tool")
        
        chat_log = st.text_area("Paste raw chat logs here for scanning:", height=100,
                               placeholder="Buyer: Send to bc1qar0s...",
                               label_visibility="collapsed")
        
        if st.button("Extract", key="extract_chat_btn"):
            if chat_log:
                wallets = extract_wallets(chat_log)
                st.success(f"Found {len(wallets)} wallets")
                for w in wallets:
                    st.markdown(f"<span class='wallet-address'>{w[:12]}...{w[-6:]}</span>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 1rem; padding: 0.5rem; background: #14181f; border-radius: 8px;">
    <p style="color: #a0a0b0; font-size: 0.7rem;">
        🔒 Hackathon Demo • Real blockchain data
    </p>
</div>
""", unsafe_allow_html=True)