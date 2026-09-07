import streamlit as st
import plotly.graph_objects as go
import time
import pandas as pd
import numpy as np

# 1. 页面基本配置 / Page Configuration
st.set_page_config(page_title="Liquidity Node Terminal", layout="wide")

# 语言文本映射字典 / Language Dictionary
TEXTS = {
    "CN": {
        "title": "🌐 动态结算节点 (Settlement Node) 实时博弈 Terminal",
        "subtitle": "基于行为金融与现金流折现（DCF）模型的轻量竞价沙盒",
        "pool": "公共资金池 (Pool)",
        "current_bid": "最高有效出价 (Current Bid)",
        "time_left": "剩余结算倒计时",
        "iv": "隐含波动率 (IV)",
        "chart_title": "📈 标的估值与竞价曲线 (Valuation Dynamics)",
        "order_title": "⚡ 交易指令面板",
        "bid_inc": "加价幅度 ($)",
        "yield_yield": "预估流动性抽成收益",
        "btn_bid": "提交出价 (Place Order)",
        "book_title": "📋 订单簿深度 (Order Book)",
        "time": "时间",
        "bid_price": "出价金额",
        "irr": "隐含年化收益率 (IRR)"
    },
    "EN": {
        "title": "🌐 Dynamic Settlement Node Game Terminal",
        "subtitle": "Lightweight Auction Sandbox based on Behavioral Finance & DCF Model",
        "pool": "Public Liquidity Pool",
        "current_bid": "Current Highest Bid",
        "time_left": "Settlement Countdown",
        "iv": "Implied Volatility (IV)",
        "chart_title": "📈 Valuation & Bidding Price Trajectory",
        "order_title": "⚡ Trading Desk",
        "bid_inc": "Bid Increment ($)",
        "yield_yield": "Est. Liquidity Yield (10%)",
        "btn_bid": "Place Order",
        "book_title": "📋 Order Book Depth",
        "time": "Time",
        "bid_price": "Bid Price",
        "irr": "Implied IRR"
    }
}

# 自定义现代 FinTech UI 样式 / Custom CSS
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 状态初始化 / Session State Initialization
if 'lang' not in st.session_state:
    st.session_state.lang = "CN"

if 'pool_value' not in st.session_state:
    st.session_state.pool_value = 500.0
    st.session_state.current_bid = 50.0
    st.session_state.history = pd.DataFrame({
        'Time': [time.strftime("%H:%M:%S", time.localtime(time.time() - i*10)) for i in range(5, 0, -1)],
        'Bid_Price': [30.0, 35.0, 40.0, 42.0, 50.0],
        'Implied_IRR': ["12.5%", "15.0%", "11.2%", "9.8%", "14.1%"]
    })

t = TEXTS[st.session_state.lang]

# 3. 顶部导航与语言切换 / Top Bar & Language Toggle
top_col1, top_col2 = st.columns([5, 1])
with top_col1:
    st.title(t["title"])
    st.caption(t["subtitle"])
with top_col2:
    selected_lang = st.radio("🌐 Language / 语言", ["CN", "EN"], horizontal=True)
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        # 兼容性重载 / Backward compatible rerun
        if hasattr(st, 'rerun'):
            st.rerun()
        else:
            st.experimental_rerun()

st.divider()

# 4. 指标卡片 / Key Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(t["pool"], f"${st.session_state.pool_value:,.2f}", "+5.2%")
with col2:
    st.metric(t["current_bid"], f"${st.session_state.current_bid:,.2f}", "+19.0%")
with col3:
    st.metric(t["time_left"], "00:12", "-3s", delta_color="inverse")
with col4:
    st.metric(t["iv"], "24.5%", "Normal")

st.divider()

# 5. 图表与操作面板 / Main Visual & Controls
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader(t["chart_title"])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=st.session_state.history['Time'], 
        y=st.session_state.history['Bid_Price'],
        mode='lines+markers',
        name='Bid Price',
        line=dict(color='#2563EB', width=3),
        marker=dict(size=8, color='#1D4ED8')
    ))
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
        yaxis=dict(showgrid=True, gridcolor='#E2E8F0', title="Price ($)")
    )
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    st.subheader(t["order_title"])
    
    bid_increment = st.number_input(t["bid_inc"], min_value=1.0, value=5.0, step=1.0)
    next_bid = st.session_state.current_bid + bid_increment
    
    st.write(f"{t['yield_yield']}: **${bid_increment * 0.1:.2f}**")
    
    if st.button(t["btn_bid"], type="primary", use_container_width=True):
        st.session_state.current_bid = next_bid
        st.session_state.pool_value += bid_increment * 0.9
        
        # 插入新订单记录 / Append order
        new_row = pd.DataFrame({
            'Time': [time.strftime("%H:%M:%S")],
            'Bid_Price': [next_bid],
            'Implied_IRR': [f"{np.random.uniform(8.0, 18.0):.1f}%"]
        })
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
        
        # 兼容性刷新 / Safe Rerun
        if hasattr(st, 'rerun'):
            st.rerun()
        else:
            st.experimental_rerun()

    st.write("---")
    st.subheader(t["book_title"])
    
    # 动态重命名订单簿表头
    df_display = st.session_state.history.tail(5).copy()
    df_display.columns = [t["time"], t["bid_price"], t["irr"]]
    st.dataframe(df_display, use_container_width=True, hide_index=True)