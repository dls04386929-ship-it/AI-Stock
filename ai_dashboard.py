import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import plotly.graph_objects as go

# 1. 網頁基本配置
st.set_page_config(page_title="全球 AI & 衛星產業鏈即時看板", layout="wide")
st.title("🌍 全球 AI 與低軌衛星產業鏈動態估值儀表板")
st.markdown("本系統即時監控全球核心指數、夜盤期貨，並針對 AI 與衛星通訊四大關鍵產業鏈進行法人估值（PE/EPS）交叉比對。")

# 2. 側邊欄控制面板
st.sidebar.header("🔄 系統控制")
refresh_interval = st.sidebar.slider("自動重新整理頻率 (秒)", min_value=10, max_value=120, value=30)
auto_refresh = st.sidebar.checkbox("啟用自動即時刷新", value=True)

# 3. 定義大盤與夜盤指數配置
INDEX_CONFIG = {
    '^GSPC': {'name': '美股 S&P 500', 'type': '大盤'},
    '^IXIC': {'name': '美股 NASDAQ', 'type': '大盤'},
    '^TWII': {'name': '台股加權指數', 'type': '大盤'},
    'WTW=F': {'name': '臺指期貨近月 (夜盤指標)', 'type': '夜盤'},
    '^N225': {'name': '日經 225 指數', 'type': '大盤'},
    '^KS11': {'name': '韓國綜合指數', 'type': '大盤'}
}

# 4. 定義 AI 與衛星產業鏈分組清單 (跨美、日、韓、台)
STOCK_CONFIG = {
    '核心晶片與算力': {
        'NVDA': {'name': 'NVIDIA', 'nation': '美'},
        'AMD': {'name': 'AMD', 'nation': '美'},
        '2330.TW': {'name': '台積電', 'nation': '台'},
        '005930.KS': {'name': '三星電子', 'nation': '韓'}
    },
    '光通訊與基礎建設': {
        'MRVL': {'name': 'Marvell', 'nation': '美'},
        '8035.T': {'name': '東京威力科創', 'nation': '日'},
        '2454.TW': {'name': '聯發科', 'nation': '台'},
        '4977.TW': {'name': '眾達-KY', 'nation': '台'}
    },
    '先進封測與記憶體': {
        '000660.KS': {'name': 'SK 海力士', 'nation': '韓'},
        '3711.TW': {'name': '日月光投控', 'nation': '台'},
        '6857.T': {'name': 'Advantest', 'nation': '日'},
        'MU': {'name': '美光科技', 'nation': '美'}
    },
    '低軌衛星設備': {
        'LHX': {'name': 'L3Harris (白沙供應鏈)', 'nation': '美'},
        '6285.TW': {'name': '啟碁科技', 'nation': '台'},
        '2314.TW': {'name': '台揚科技', 'nation': '台'},
        '3491.TW': {'name': '昇達科', 'nation': '台'}
    }
}

# 5. 資料抓取核心邏輯
@st.cache_data(ttl=10) # 快取 10 秒避免頻繁對 Yahoo 發送請求被鎖
def fetch_all_data():
    # --- A. 抓取指數資料 ---
    index_tickers = list(INDEX_CONFIG.keys())
    idx_data = yf.download(index_tickers, period='2d', interval='1m', progress=False)
    
    index_results = []
    for ticker in index_tickers:
        try:
            close_series = idx_data['Close'][ticker].dropna()
            if not close_series.empty:
                current_val = close_series.iloc[-1]
                prev_close = close_series.iloc[0] # 取得基準點計算漲跌
                change_pct = ((current_val - prev_close) / prev_close) * 100
                index_results.append({
                    '項目': INDEX_CONFIG[ticker]['name'],
                    '型態': INDEX_CONFIG[ticker]['type'],
                    '當前點數': f"{current_val:,.2f}",
                    '今日漲跌幅': change_pct
                })
        except:
            pass
    
    # --- B. 抓取產業鏈個股與基本面估值 ---
    all_stock_tickers = []
    for group, stocks in STOCK_CONFIG.items():
        all_stock_tickers.extend(stocks.keys())
        
    # 批量抓取個股今日即時 K 線
    stock_market_data = yf.download(all_stock_tickers, period='1d', interval='1m', progress=False)
    
    stock_results = []
    for group, stocks in STOCK_CONFIG.items():
        for ticker, info in stocks.items():
            try:
                # 撈取即時價與漲跌幅
                close_series = stock_market_data['Close'][ticker].dropna()
                open_series = stock_market_data['Open'][ticker].dropna()
                
                current_price = close_series.iloc[-1] if not close_series.empty else 0.0
                open_price = open_series.iloc[0] if not open_series.empty else current_price
                change_pct = ((current_price - open_price) / open_price) * 100 if open_price != 0 else 0.0
                
                # 獲取 Ticker Info (財務基本面：法人預估 PE 與 EPS)
                # 注意：yf.Ticker().info 請求較慢，若遇到網路延遲會使用預設值
                t_obj = yf.Ticker(ticker)
                t_info = t_obj.info
                
                forward_pe = t_info.get('forwardPE', None)
                forward_eps = t_info.get('forwardEps', None)
                currency = t_info.get('currency', '')

                stock_results.append({
                    '產業分組': group,
                    '國家': info['nation'],
                    '代號': ticker,
                    '公司名稱': info['name'],
                    '當前股價': f"{current_price:,.2f} {currency}" if current_price else "未開盤",
                    '今日漲跌幅': change_pct,
                    '法人預估本益比 (Forward PE)': f"{forward_pe:.2f} 倍" if forward_pe else "無資料",
                    '法人預估明年 EPS': f"{forward_eps:.2f}" if forward_eps else "無資料"
                })
            except Exception as e:
                pass
                
    return pd.DataFrame(index_results), pd.DataFrame(stock_results)

# 執行資料抓取
with st.spinner('正在從全球交易所同步最新大盤、夜盤及產業鏈估值數據...'):
    df_index, df_stocks = fetch_all_data()

# 6. 網頁前端排版與呈現
# --- 區塊一：全球大盤與夜盤監控 ---
st.markdown("## 📊 全球主要大盤 & 台指夜盤監控")
if not df_index.empty:
    cols = st.columns(len(df_index))
    for idx, row in df_index.iterrows():
        with cols[idx]:
            # 根據漲跌決定 delta 顏色符號
            delta_str = f"{row['今日漲跌幅']:+.2f}%"
            st.metric(
                label=f"{row['型態']} | {row['項目']}", 
                value=row['當前點數'], 
                delta=delta_str,
                delta_color="normal"
            )
else:
    st.warning("暫時無法取得指數資料，請確認網路連線。")

st.markdown("---")

# --- 區塊二：產業鏈分組看板 ---
st.markdown(f"## 🚀 AI & 低軌衛星全球產業鏈觀測站 (更新時間: {datetime.now().strftime('%H:%M:%S')})")

if not df_stocks.empty:
    # 建立頁籤分門別類顯示
    categories = list(STOCK_CONFIG.keys())
    tabs = st.tabs(categories)
    
    for i, cat in enumerate(categories):
        with tabs[i]:
            st.markdown(f"### 🎯 群組：{cat}")
            
            # 篩選出該產業別的資料
            df_sub = df_stocks[df_stocks['產業分組'] == cat].copy()
            
            # 美化漲跌幅欄位顯示
            df_sub['今日漲跌幅'] = df_sub['今日漲跌幅'].apply(lambda x: f"{x:+.2f}%")
            
            # 整理輸出表格
            df_display = df_sub.drop(columns=['產業分組'])
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # 畫出該分組的即時漲跌幅圖表
            fig = go.Figure(go.Bar(
                x=df_sub['公司名稱'] + " (" + df_sub['國家'] + ")",
                y=df_sub['今日漲跌幅'].str.replace('%','').astype(float),
                marker_color=['#ff4b4b' if float(x.replace('%','')) < 0 else '#00f574' for x in df_sub['今日漲跌幅']]
            ))
            fig.update_layout(
                yaxis_title="今日漲跌幅 (%)",
                xaxis_title="企業龍頭",
                height=300,
                margin=dict(l=20, r=20, t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{i}")
else:
    st.info("尚無個股與估值資料。")

# 7. 自動重新整理邏輯
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()