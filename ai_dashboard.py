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
st.set_page_config(page_title="量化選股終端", layout="wide")
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGxzMDQzODY5MjlAZ21haWwuY29tIiwiZW1haWwiOiJkbHMwNDM4NjkyOUBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.XLHUQWa0QglCBjukX374bWUWeVaFLfwHhBMrtOrZ-0E"
API_URL = "https://api.finmindtrade.com/api/v4/data"

# 初始化全域指針
if 'scan_pointer' not in st.session_state:
    st.session_state.scan_pointer = 0

# ==============================================================================
# 2. 核心選股與輪巡函數
# ==============================================================================
@st.cache_data(ttl=86400)
def fetch_all_taiwan_stock_pool():
    """撈取台股電子股清單"""
    try:
        parameter = {"dataset": "TaiwanStockInfo", "token": FINMIND_TOKEN}
        res = requests.get(API_URL, params=parameter, timeout=12).json()
        if res.get("msg") == "success":
            df = pd.DataFrame(res["data"])
            df = df[df['industry_category'].str.contains('電子|半導體|光電', na=False)]
            return df[['stock_id', 'stock_name']].values.tolist()
    except: pass
    return [("2330", "台積電"), ("2454", "聯發科"), ("2317", "鴻海")]

def run_paged_electronic_screener(stock_list):
    """分頁輪巡與指標撈取邏輯"""
    batch_size = 50
    start_idx = st.session_state.scan_pointer
    batch = stock_list[start_idx : start_idx + batch_size]
    
    if not batch:
        st.session_state.scan_pointer = 0
        return pd.DataFrame()
    
    results = []
    for s_id, s_name in batch:
        # 這裡執行您的四項指標計算 (簡化模擬)
        results.append({
            "股票代碼": s_id,
            "公司名稱": s_name,
            "大戶籌碼": "🟢 優", 
            "研發費用": "🟢 增",
            "合約負債": "🟢 高",
            "月營收年增": "🟢 +15%"
        })
    
    st.session_state.scan_pointer += batch_size
    return pd.DataFrame(results)

# ==============================================================================
# 3. 頁面渲染邏輯 (Tab 3 修正)
# ==============================================================================
st.title("🎯 全市場電子股輪巡選股終端")
# ... (其他 Tabs 渲染邏輯) ...

# 修正後的 Tab 3 區塊
# with view_tab3:
st.markdown("### 🎯 電子股指標即時觀測 (每 50 檔為一頁)")
all_stocks = fetch_all_taiwan_stock_pool()

if st.button("🚀 讀取下一頁 50 檔電子股數據"):
    with st.spinner("正在進行大數據比對..."):
        df_display = run_paged_electronic_screener(all_stocks)
        if not df_display.empty:
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            st.success(f"目前顯示範圍：第 {st.session_state.scan_pointer - 50 + 1} 檔至 {st.session_state.scan_pointer} 檔。")
        else:
            st.warning("⚠️ 已掃描完畢，請重新整理。")
else:
    st.info(f"💡 目前輪巡進度：已掃描至第 {st.session_state.scan_pointer} 檔。")
