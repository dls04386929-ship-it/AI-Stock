import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import requests
import plotly.graph_objects as go

# ==============================================================================
# 1. 網頁基礎配置與金鑰設定
# ==============================================================================
st.set_page_config(page_title="全球 AI & 衛星產業鏈五合一終極自動化看板", layout="wide")
st.title("🌍 全球 AI 與低軌衛星產業鏈【五合一終極全自動看盤系統】")
st.markdown("本系統全面整合：**操作紀律、全球總經風向、每日盤後籌碼(API全自動)、全球大盤即時監控、跨國關鍵產業鏈估值**。")

# 填入您提供的 FinMind API Token
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGxzMDQzODY5MjlAZ21haWwuY29tIiwiZW1haWwiOiJkbHMwNDM4NjkyOUBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.XLHUQWa0QglCBjukX374bWUWeVaFLfwHhBMrtOrZ-0E"

# 側邊欄控制面板
st.sidebar.header("🔄 系統主控制")
refresh_interval = st.sidebar.slider("動態資料重新整理頻率 (秒)", min_value=10, max_value=120, value=30)
auto_refresh = st.sidebar.checkbox("啟用自動即時刷新", value=True)

# ==============================================================================
# 一、核心投資操作紀律看板 (手寫心法轉化)
# ==============================================================================
st.markdown("### 🛑 投資核心操作紀律")
with st.container():
    col_law1, col_law2, col_law3, col_law4 = st.columns(4)
    with col_law1:
        st.info("📊 **1. 不預測市場**\n\n🛡️ **2. 分散投資**")
    with col_law2:
        st.warning("⚠️ **3. 控制風險**\n\n⏳ **4. 長期持有**")
    with col_law3:
        st.success("📚 **5. 持續學習**\n\n🎯 **6. 堅守紀律**")
    with col_law4:
        st.error("🔇 **7. 忽略噪音**\n\n💰 **8. 先存緊急準備金**")

st.markdown("---")

# ==============================================================================
# 二、全球每日核心關注列表 (總經與週末盤前風向球)
# ==============================================================================
st.markdown("### 🌐 全球每日核心關注列表 (週末與盤前風向球)")
with st.container():
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(label="🇺🇸 週末美國科技股 100", value="29,827.7", delta="+0.53%")
        st.metric(label="🇺🇸 Weekend Wall Street Cash", value="51,355.2", delta="+0.35%")
    with col_m2:
        st.metric(label="🇪🇺 Weekend Germany 40 Cash", value="24,756.9", delta="+0.40%")
        st.metric(label="🇬🇧 週末英國富時 100", value="10,497.3", delta="+0.34%")
    with col_m3:
        st.metric(label="🇭🇰 週末香港 HS50 現貨", value="24,752.9", delta="+0.28%")
        st.metric(label="🇦🇺 週末澳洲 200", value="8,860.2", delta="+0.19%")
    with col_m4:
        st.metric(label="🛢️ 週末美國原油 現貨", value="8,070.6", delta="-2.70%", delta_color="inverse")
        st.metric(label="🌟 週末黃金 現貨", value="4,235.5", delta="+0.54%")

st.markdown("---")

# ==============================================================================
# 三、自動串接台灣本土財經 API 函數 (籌碼面自動更新與清洗邏輯)
# ==============================================================================
def get_backup_chips_data():
    """ 容錯備用數據：當 API 異常或假日未開盤時啟動，維持系統正常顯示 """
    backup_buy = [
        {"排名": 1, "族群": "元宇宙", "大戶差 (億)": 360.9, "說明": "歷史基準資料"},
        {"排名": 2, "族群": "5G手機", "大戶差 (億)": 358.9, "說明": "歷史基準資料"},
        {"排名": 3, "族群": "MIH平台概念股", "大戶差 (億)": 303.6, "說明": "歷史基準資料"},
        {"排名": 4, "族群": "被動元件(C/R)", "大戶差 (億)": 267.0, "說明": "歷史基準資料"},
        {"排名": 5, "族群": "MLCC", "大戶差 (億)": 246.3, "說明": "歷史基準資料"},
    ]
    backup_sell = [
        {"排名": 1, "族群": "IC封測", "大戶差 (億)": -83.55, "說明": "歷史基準資料"},
        {"排名": 2, "族群": "低軌道衛星", "大戶差 (億)": -42.85, "說明": "歷史基準資料"},
        {"排名": 3, "族群": "NAND Flash控制IC", "大戶差 (億)": -28.77, "說明": "歷史基準資料"},
        {"排名": 4, "族群": "雲端運算", "大戶差 (億)": -27.94, "說明": "歷史基準資料"},
        {"排名": 5, "族群": "探針卡", "大戶差 (億)": -26.86, "說明": "歷史基準資料"},
    ]
    return pd.DataFrame(backup_buy), pd.DataFrame(backup_sell), "2026-06-15 (歷史基準)"

@st.cache_data(ttl=1800) # 籌碼面資料半小時更新一次即可，避免頻繁呼叫浪費 API 額度
def fetch_tw_chip_data_automated():
    url = "https://api.finmindtrade.com/api/v4/data"
    
    # 判斷時間：下午 4 點前看盤，自動抓取前一天的籌碼狀況；4 點後抓當天最新資料
    target_date = datetime.now()
    if target_date.hour < 16:
        target_date = target_date - timedelta(days=1)
        
    date_str = target_date.strftime("%Y-%m-%d")
    
    parameter = {
        "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
        "data_id": "", 
        "start_date": date_str,
        "end_date": date_str,
        "token": FINMIND_TOKEN
    }
    
    try:
        response = requests.get(url, params=parameter, timeout=10)
        data = response.json()
        
        if data.get("msg") == "success" and len(data.get("data", [])) > 0:
            df = pd.DataFrame(data["data"])
            
            # 籌碼清洗：買賣超差額 (買進金額 - 賣出金額) 並換算為億元
            df['買賣超(億)'] = (df['buy'] - df['sell']) / 100000000
            
            # 依照族群名稱(name)進行三大法人加總
            df_grouped = df.groupby('name')['買賣超(億)'].sum().reset_index()
            df_grouped.columns = ['族群', '大戶差 (億)']
            
            # 篩選買超、賣超前 5 名
            df_buy_top5 = df_grouped.sort_values(by='大戶差 (億)', ascending=False).head(5).copy()
            df_sell_top5 = df_grouped.sort_values(by='大戶差 (億)', ascending=True).head(5).copy()
            
            # 建立排名
            df_buy_top5['排名'] = range(1, len(df_buy_top5) + 1)
            df_sell_top5['排名'] = range(1, len(df_sell_top5) + 1)
            
            df_buy_top5 = df_buy_top5[['排名', '族群', '大戶差 (億)']]
            df_sell_top5 = df_sell_top5[['排名', '族群', '大戶差 (億)']]
            
            # 美化數字輸出格式
            df_buy_top5['大戶差 (億)'] = df_buy_top5['大戶差 (億)'].apply(lambda x: f"+{x:.2f} 億")
            df_sell_top5['大戶差 (億)'] = df_sell_top5['大戶差 (億)'].apply(lambda x: f"{x:.2f} 億")
            
            return df_buy_top5, df_sell_top5, date_str
        else:
            return get_backup_chips_data()
    except:
        return get_backup_chips_data()

# 呼叫自動化籌碼抓取
df_automated_buy, df_automated_sell, chip_date_info = fetch_tw_chip_data_automated()

# 籌碼面介面呈現
st.markdown(f"### 🎯 每日盤後大戶資金流向統計 (API 自動即時更新 | 籌碼數據基準日: {chip_date_info})")
col_buy, col_sell = st.columns(2)
with col_buy:
    st.success("🛒 盤後大戶買超 TOP 5 (資金流入主攻部隊)")
    st.dataframe(df_automated_buy, use_container_width=True, hide_index=True)
with col_sell:
    st.error("📉 盤後大戶賣超 TOP 5 (資金流出/防範調節)")
    st.dataframe(df_automated_sell, use_container_width=True, hide_index=True)

st.markdown("> 💡 **籌碼焦點筆記：** 資金持續流向電子主流族群，AI、車用電子與被動元件成市場焦點。部分大戶賣超族群出現『股價逆勢上漲』之背離現象時，應嚴守風險纪律，切勿過度追高。")
st.markdown("---")


# ==============================================================================
# 四、全球大盤、夜盤與個股設定
# ==============================================================================
INDEX_CONFIG = {
    '^GSPC': {'name': '美股 S&P 500', 'type': '大盤'},
    '^IXIC': {'name': '美股 NASDAQ', 'type': '大盤'},
    '^TWII': {'name': '台股加權指數', 'type': '大盤'},
    'WTW=F': {'name': '臺指期貨近月 (夜盤指標)', 'type': '夜盤'},
    '^N225': {'name': '日經 225 指數', 'type': '大盤'},
    '^KS11': {'name': '韓國綜合指數', 'type': '大盤'}
}

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

# ==============================================================================
# 五、動態即時報價與估值抓取邏輯 (Yahoo Finance)
# ==============================================================================
@st.cache_data(ttl=10)
def fetch_financial_dashboard_data():
    # --- A. 抓取全球大盤/夜盤數據 ---
    index_tickers = list(INDEX_CONFIG.keys())
    idx_data = yf.download(index_tickers, period='2d', interval='1m', progress=False)
    
    index_results = []
    for ticker in index_tickers:
        try:
            close_series = idx_data['Close'][ticker].dropna()
            if not close_series.empty:
                current_val = close_series.iloc[-1]
                prev_close = close_series.iloc[0]
                change_pct = ((current_val - prev_close) / prev_close) * 100
                index_results.append({
                    '項目': INDEX_CONFIG[ticker]['name'],
                    '型態': INDEX_CONFIG[ticker]['type'],
                    '當前點數': f"{current_val:,.2f}",
                    '今日漲跌幅': change_pct
                })
        except:
            pass

    # --- B. 抓取個股基本面與動態估值 ---
    all_stock_tickers = []
    for group, stocks in STOCK_CONFIG.items():
        all_stock_tickers.extend(stocks.keys())
        
    stock_market_data = yf.download(all_stock_tickers, period='1d', interval='1m', progress=False)
    
    stock_results = []
    for group, stocks in STOCK_CONFIG.items():
        for ticker, info in stocks.items():
            try:
                close_series = stock_market_data['Close'][ticker].dropna()
                open_series = stock_market_data['Open'][ticker].dropna()
                
                current_price = close_series.iloc[-1] if not close_series.empty else 0.0
                open_price = open_series.iloc[0] if not open_series.empty else current_price
                change_pct = ((current_price - open_price) / open_price) * 100 if open_price != 0 else 0.0
                
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
                    '當前股價': current_price,
                    '幣別': currency,
                    '今日漲跌幅': change_pct,
                    '法人預估本益比 (Forward PE)': forward_pe,
                    '法人預估明年 EPS': forward_eps
                })
            except:
                pass
                
    return pd.DataFrame(index_results), pd.DataFrame(stock_results)

# 執行即時報價同步
with st.spinner('正在與全球證券交易所同步最新即時行情、期貨與法人估值...'):
    df_index, df_stocks = fetch_financial_dashboard_data()

# ==============================================================================
# 六、全球大盤與個股分頁呈現
# ==============================================================================
st.markdown("### 📊 全球主要大盤 & 台指夜盤即時監控")
if not df_index.empty:
    cols = st.columns(len(df_index))
    for idx, row in df_index.iterrows():
        with cols[idx]:
            delta_str = f"{row['今日漲跌幅']:+.2f}%"
            st.metric(
                label=f"{row['型態']} | {row['項目']}", 
                value=row['當前點數'], 
                delta=delta_str
            )
else:
    st.warning("暫時無法取得指數資料。")

st.markdown("---")

st.markdown(f"### 🚀 AI & 低軌衛星全球產業鏈觀測站 (系統刷新時間: {datetime.now().strftime('%H:%M:%S')})")

if not df_stocks.empty:
    categories = list(STOCK_CONFIG.keys())
    tabs = st.tabs(categories)
    
    for i, cat in enumerate(categories):
        with tabs[i]:
            st.markdown(f"#### 🎯 核心聚落：{cat}")
            
            df_sub = df_stocks[df_stocks['產業分組'] == cat].copy()
            
            # 建立獨立的前台展示表（數據隔離，防止 Plotly 繪圖報錯）
            df_display = df_sub.copy()
            df_display['當前股價'] = df_display.apply(lambda r: f"{r['當前股價']:,.2f} {r['幣別']}" if r['當前股價'] > 0 else "未開盤", axis=1)
            df_display['今日漲跌幅'] = df_display['今日漲跌幅'].apply(lambda x: f"{x:+.2f}%")
            df_display['法人預估本益比 (Forward PE)'] = df_display['法人預估本益比 (Forward PE)'].apply(lambda x: f"{x:.2f} 倍" if pd.notnull(x) else "無資料")
            df_display['法人預估明年 EPS'] = df_display['法人預估明年 EPS'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "無資料")
            
            df_display = df_display.drop(columns=['產業分組', '幣別'])
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # 繪圖：直接使用純數字型態的 df_sub 序列
            fig = go.Figure(go.Bar(
                x=df_sub['公司名稱'] + " (" + df_sub['國家'] + ")",
                y=df_sub['今日漲跌幅'],
                marker_color=['#ff4b4b' if x < 0 else '#00f574' for x in df_sub['今日漲跌幅']]
            ))
            fig.update_layout(
                yaxis_title="今日漲跌幅 (%)",
                xaxis_title="龍頭企業",
                height=300,
                margin=dict(l=20, r=20, t=15, b=15)
            )
            st.plotly_chart(fig, use_container_width=True, key=f"chart_final_group_{i}")
else:
    st.info("尚無個股與估值資料。")

# ==============================================================================
# 七、網頁定時自動循環刷新機制
# ==============================================================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
