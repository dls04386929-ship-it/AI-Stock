import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import requests
import plotly.graph_objects as go

# ==============================================================================
# 1. 網頁基礎配置
# ==============================================================================
st.set_page_config(page_title="全球跨國宏觀產業輪動決策終端", layout="wide")
st.title("🌍 全球 AI、低軌衛星暨台美日韓強勢板塊【跨國聯動量化決策系統】")

# FinMind API Token
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGxzMDQzODY5MjlAZ21haWwuY29tIiwiZW1haWwiOiJkbHMwNDM4NjkyOUBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.XLHUQWa0QglCBjukX374bWUWeVaFLfwHhBMrtOrZ-0E"

# 側邊欄控制
st.sidebar.header("🔄 系統主控制面板")
refresh_interval = st.sidebar.slider("動態報價刷新頻率 (秒)", 10, 120, 30)
auto_refresh = st.sidebar.checkbox("啟用自動即時刷新", True)

# ==============================================================================
# 2. 資料獲取與處理函數
# ==============================================================================
@st.cache_data(ttl=60)
def fetch_stock_data_with_metrics(ticker_list):
    """抓取股價與基礎財務數據"""
    data = {}
    for t in ticker_list:
        try:
            stock = yf.Ticker(t)
            info = stock.info
            data[t] = {
                'Forward PE': info.get('forwardPE', 0.0),
                'Forward EPS': info.get('forwardEps', 0.0),
                'Current Price': info.get('currentPrice', 0.0)
            }
        except:
            data[t] = {'Forward PE': 0.0, 'Forward EPS': 0.0, 'Current Price': 0.0}
    return data

# ==============================================================================
# 3. 核心觀測站內容 (整合邏輯)
# ==============================================================================
st.markdown("### 📊 核心觀測站")

# 假設您定義了產業池 (對應您原本的配置)
TW_STOCK_CONFIG = {
    '1. 被動元件': {'2492.TW': '華新科', '2327.TW': '國巨'},
    '2. 半導體': {'5483.TW': '中美晶', '6488.TW': '環球晶'}
}

# 動態處理數值
all_tw_tickers = [t for group in TW_STOCK_CONFIG.values() for t in group.keys()]
metrics = fetch_stock_data_with_metrics(all_tw_tickers)

# Tab 顯示邏輯
view_tab1, view_tab2 = st.tabs(["🇹🇼 台股焦點核心池", "🇺🇸🇯🇵🇰🇷 國際龍頭池"])

with view_tab1:
    results = []
    for group, stocks in TW_STOCK_CONFIG.items():
        for t, name in stocks.items():
            m = metrics.get(t, {})
            results.append({
                '產業分組': group,
                '公司名稱': name,
                '當前股價': f"{m['Current Price']:,.2f}",
                'Forward PE': f"{m['Forward PE']:.2f}",
                '預估明年 EPS': f"{m['Forward EPS']:.2f}"
            })
    
    df_disp = pd.DataFrame(results)
    st.dataframe(df_disp, use_container_width=True, hide_index=True)

# ==============================================================================
# 4. 台指期決策引擎 (核心邏輯補足)
# ==============================================================================
st.markdown("### 📊 台指期交易決策引擎")

@st.cache_data(ttl=300)
def get_tx_data():
    # 模擬數值獲取邏輯，實際對接 FinMind
    return 21530.0, -12450, 21580.0, 21480.0

tx_price, foreign_net_oi, high, low = get_tx_data()

c1, c2, c3 = st.columns(3)
c1.metric("台指期當前價", f"{tx_price:,.0f}")
c2.metric("外資期貨淨未平倉", f"{foreign_net_oi:,} 口")
c3.metric("今日波幅", f"{high - low:,.0f} 點")

# ==============================================================================
# 5. 自動刷新
# ==============================================================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
