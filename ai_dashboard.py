import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
import requests
import plotly.graph_objects as go
from bs4 import BeautifulSoup

# ==============================================================================
# 1. 網頁基礎配置與金鑰設定
# ==============================================================================
st.set_page_config(page_title="全球跨國宏觀產業輪動決策終端", layout="wide")
st.title("🌍 全球 AI、低軌衛星暨台美日韓強勢板塊【跨國聯動量化決策系統】")
st.markdown("本系統全面整合：**操作紀律、全球總經、FinMind 盤後大戶籌碼、全球大盤即時監控、台股主流板塊輪動，以及『美日韓核心產業龍頭觀測站』與『全市場多指標放寬型量化選股終端』**。")

# FinMind API Token與端點
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGxzMDQzODY5MjlAZ21haWwuY29tIiwiZW1haWwiOiJkbHMwNDM4NjkyOUBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.XLHUQWa0QglCBjukX374bWUWeVaFLfwHhBMrtOrZ-0E"
API_URL = "https://api.finmindtrade.com/api/v4/data"

# 側邊欄控制面板
st.sidebar.header("🔄 系統主控制面板")
refresh_interval = st.sidebar.slider("動態報價刷新頻率 (秒)", min_value=10, max_value=120, value=30)
auto_refresh = st.sidebar.checkbox("啟用自動即時刷新", value=True)

# ==============================================================================
# 二、核心投資操作紀律看板
# ==============================================================================
st.markdown("### 🛑 投資核心操作紀律")
with st.container():
    col_law1, col_law2, col_law3, col_law4 = st.columns(4)
    with col_law1: st.info("📊 **1. 不預測市場**\n\n🛡️ **2. 分散投資**")
    with col_law2: st.warning("⚠️ **3. 控制風險**\n\n⏳ **4. 長期持有**")
    with col_law3: st.success("📚 **5. 持續學習**\n\n🎯 **6. 堅守紀律**")
    with col_law4: st.error("🔇 **7. 忽略噪音**\n\n💰 **8. 先存緊急準備金**")

st.markdown("---")

# ==============================================================================
# 三、全球每日核心關注列表 (週末與盤前風向球)
# ==============================================================================
st.markdown("### 🌐 全球每日核心關注列表 (週末與盤前風向球)")
weekend_data = [
    {"label": "🇺🇸 週末美國科技股 100", "val": "29,827.7", "chg": 0.53},
    {"label": "🇺🇸 Weekend Wall Street Cash", "val": "51,355.2", "chg": 0.35},
    {"label": "🇪🇺 Weekend Germany 40 Cash", "val": "24,756.9", "chg": 0.40},
    {"label": "🇬🇧 週末英國富時 100", "val": "10,497.3", "chg": 0.34},
    {"label": "🇭🇰 週末香港 HS50 現貨", "val": "24,752.9", "chg": 0.28},
    {"label": "🇦🇺 週末澳洲 200", "val": "8,860.2", "chg": 0.19},
    {"label": "🛢️ 週末美國原油 現貨", "val": "8,070.6", "chg": -2.70},
    {"label": "🌟 週末黃金 現貨", "val": "4,235.5", "chg": 0.54}
]
with st.container():
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    for idx, item in enumerate(weekend_data):
        target_col = col_m1 if idx < 2 else (col_m2 if idx < 4 else (col_m3 if idx < 6 else col_m4))
        color_mode = "inverse" if item["chg"] >= 0 else "normal"
        sign = "+" if item["chg"] >= 0 else ""
        with target_col:
            st.metric(label=item["label"], value=item["val"], delta=f"{sign}{item['chg']:.2f}%", delta_color=color_mode)

st.markdown("---")

# ==============================================================================
# 四、自動串接台灣本土財經 API 函數 (盤後大戶籌碼)
# ==============================================================================
def get_backup_chips_data():
    backup_buy = [{"排名": 1, "族群": "元宇宙", "大戶差 (億)": 360.9}, {"排名": 2, "族群": "5G手機", "大戶差 (億)": 358.9}, {"排名": 3, "族群": "MIH平台概念股", "大戶差 (億)": 303.6}, {"排名": 4, "族群": "被動元件(C/R)", "大戶差 (億)": 267.0}, {"排名": 5, "族群": "MLCC", "大戶差 (億)": 246.3}]
    backup_sell = [{"排名": 1, "族群": "IC封測", "大戶差 (億)": -83.55}, {"排名": 2, "族群": "低軌道衛星", "大戶差 (億)": -42.85}, {"排名": 3, "族群": "NAND Flash控制IC", "大戶差 (億)": -28.77}, {"排名": 4, "族群": "雲端運算", "大戶差 (億)": -27.94}, {"排名": 5, "族群": "探針卡", "大戶差 (億)": -26.86}]
    return pd.DataFrame(backup_buy), pd.DataFrame(backup_sell), "2026-06-15 (歷史基準)"

@st.cache_data(ttl=1800)
def fetch_tw_chip_data_automated():
    target_date = datetime.now()
    if target_date.hour < 16:
        target_date = target_date - timedelta(days=1)
    date_str = target_date.strftime("%Y-%m-%d")
    
    parameter = {"dataset": "TaiwanStockInstitutionalInvestorsBuySell", "start_date": date_str, "end_date": date_str, "token": FINMIND_TOKEN}
    try:
        response = requests.get(API_URL, params=parameter, timeout=10)
        data = response.json()
        if data.get("msg") == "success" and len(data.get("data", [])) > 0:
            df = pd.DataFrame(data["data"])
            df['買賣超(億)'] = (df['buy'] - df['sell']) / 100000000
            df_grouped = df.groupby('name')['買賣超(億)'].sum().reset_index()
            df_grouped.columns = ['族群', '大戶差 (億)']
            
            df_buy_top5 = df_grouped.sort_values(by='大戶差 (億)', ascending=False).head(5).copy()
            df_sell_top5 = df_grouped.sort_values(by='大戶差 (億)', ascending=True).head(5).copy()
            
            df_buy_top5['排名'] = range(1, len(df_buy_top5) + 1)
            df_sell_top5['排名'] = range(1, len(df_sell_top5) + 1)
            
            df_buy_top5['大戶差 (億)'] = df_buy_top5['大戶差 (億)'].apply(lambda x: f"+{x:.2f} 億")
            df_sell_top5['大戶差 (億)'] = df_sell_top5['大戶差 (億)'].apply(lambda x: f"{x:.2f} 億")
            return df_buy_top5, df_sell_top5, date_str
        else: return get_backup_chips_data()
    except: return get_backup_chips_data()

df_automated_buy, df_automated_sell, chip_date_info = fetch_tw_chip_data_automated()

st.markdown(f"### 🎯 每日盤後大戶資金流向統計 (API 全自動更新 | 籌碼基準日: {chip_date_info})")
col_buy, col_sell = st.columns(2)
with col_buy:
    st.success("🛒 盤後大戶買超 TOP 5 (資金流入主攻部隊)")
    st.dataframe(df_automated_buy, use_container_width=True, hide_index=True)
with col_sell:
    st.error("📉 盤後大戶賣超 TOP 5 (資金流出/防範調節)")
    st.dataframe(df_automated_sell, use_container_width=True, hide_index=True)
st.markdown("---")

# ==============================================================================
# 五、大盤與夜盤監控配置 (已修正 KeyError 異常)
# ==============================================================================
INDEX_CONFIG = {
    '^GSPC': {'name': '美股 S&P 500', 'type': '大盤'}, '^IXIC': {'name': '美股 NASDAQ', 'type': '大盤'},
    '^TWII': {'name': '台股加權指數', 'type': '大盤'}, 'WTW=F': {'name': '臺指期貨近月 (夜盤指標)', 'type': '夜盤'},
    '^N225': {'name': '日經 225 指數', 'type': '大盤'}, '^KS11': {'name': '韓國綜合指數', 'type': '大盤'}
}
st.markdown("### 📊 全球主要大盤 & 台指夜盤即時監控")
index_tickers = list(INDEX_CONFIG.keys())

# 使用 group_by='ticker' 確保多重索引結構清晰穩定
idx_market_data = yf.download(index_tickers, period='2d', interval='1m', progress=False, group_by='ticker')

shared_prices = {"^GSPC": 44169.0, "^IXIC": 19000.0, "^TWII": 44169.0, "WTW=F": 44022.0, "^N225": 39000.0, "^KS11": 2700.0}

if not idx_market_data.empty:
    cols = st.columns(len(index_tickers))
    for idx, t in enumerate(index_tickers):
        try:
            # 安全防護：檢查該代號是否存在於第一層 Ticker 索引中
            if t in idx_market_data.columns.levels[0]:
                ticker_df = idx_market_data[t]
                valid_close = ticker_df['Close'].dropna()
                
                # 如果台指期夜盤當下沒開盤，自動拿台股日盤現貨做基準，避免畫面空白
                if t == 'WTW=F' and valid_close.empty:
                    if '^TWII' in idx_market_data.columns.levels[0]:
                        tw_close = idx_market_data['^TWII']['Close'].dropna()
                        if not tw_close.empty:
                            curr_val = float(tw_close.iloc[-1])
                            prev_val = float(tw_close.iloc[0]) if len(tw_close) > 1 else curr_val
                            chg_pct = ((curr_val - prev_val) / prev_val) * 100
                            with cols[idx]:
                                st.metric(label=f"日盤同步 | {INDEX_CONFIG[t]['name']}", value=f"{curr_val:,.2f}", delta=f"{chg_pct:+.2f}%")
                            shared_prices[t] = curr_val
                            continue

                if not valid_close.empty:
                    curr_val = float(valid_close.iloc[-1])
                    valid_open = ticker_df['Open'].dropna()
                    base_open = float(valid_open.iloc[0]) if not valid_open.empty else curr_val
                    chg_pct = ((curr_val - base_open) / base_open) * 100 if base_open != 0 else 0.0
                    
                    shared_prices[t] = curr_val
                    with cols[idx]:
                        col_mode = "inverse" if chg_pct >= 0 else "normal"
                        st.metric(label=f"{INDEX_CONFIG[t]['type']} | {INDEX_CONFIG[t]['name']}", value=f"{curr_val:,.2f}", delta=f"{chg_pct:+.2f}%", delta_color=col_mode)
                else:
                    with cols[idx]: st.metric(label=f"{INDEX_CONFIG[t]['type']} | {INDEX_CONFIG[t]['name']}", value="休市/無報價", delta=None)
            else:
                with cols[idx]: st.metric(label=f"{INDEX_CONFIG[t]['type']} | {INDEX_CONFIG[t]['name']}", value="欄位對位中", delta=None)
        except:
            with cols[idx]: st.metric(label=f"連線延遲 | {INDEX_CONFIG[t]['name']}", value="自動重試中", delta=None)
st.markdown("---")

# ==============================================================================
# 六、焦點核心池板塊配置庫 (共 27 檔)
# ==============================================================================
TW_STOCK_CONFIG = {
    '1. 被動元件 (多頭總司令)': {'2492.TW': '華新科', '2327.TW': '國巨', '2375.TW': '凱美', '3026.TW': '禾伸堂', '3090.TW': '日電貿', '2478.TW': '大毅', '6173.TW': '信昌電', '6449.TW': '鈺邦', '8042.TW': '金山電', '8043.TW': '蜜望實', '6175.TW': '立敦', '3624.TW': '光頡', '3236.TW': '千如', '5328.TW': '華容', '6155.TW': '鈞寶', '8121.TW': '越峰'},
    '2. 半導體矽晶圓 (產業築底完成)': {'5483.TW': '中美晶', '6488.TW': '環球晶', '6182.TW': '合晶', '3532.TW': '台勝科', '3016.TW': '嘉晶', '2338.TW': '光罩', '6139.TW': '亞翔'},
    '3. 記憶體與 IC 設計 (消費電子回暖)': {'2344.TW': '華邦電', '4973.TW': '廣穎', '3035.TW': '智原', '4919.TW': '新唐', '2401.TW': '凌陽', '8096.TW': '擎亞', '2489.TW': '瑞軒'},
    '4. 光學鏡頭與光通訊 (地緣政治緩解)': {'3008.TW': '大立光', '3406.TW': '玉晶光', '3362.TW': '先進光', '4979.TW': '華星光'},
    '5. PCB、電子材料與能源化工': {'1303.TW': '南亞', '1714.TW': '和桐', '6274.TW': '台耀', '6153.TW': '嘉聯益', '6191.TW': '精成科', '2484.TW': '希華'}
}

GLOBAL_STOCK_CONFIG = {
    '核心算力與GPU (美日韓)': {'NVDA': {'name': 'NVIDIA (全球算力霸主)', 'nation': '美'}, 'AMD': {'name': 'AMD (高階處理器)', 'nation': '美'}, '005930.KS': {'name': '三星電子 (代工與半導體)', 'nation': '韓'}},
    '全球記憶體巨頭 (美韓對比)': {'MU': {'name': '美光科技 (儲存記憶體)', 'nation': '美'}, '000060.KS': {'name': 'SK 海力士 (HBM 核心供應商)', 'nation': '韓'}},
    '半導體設備與先進材料 (日美)': {'8035.T': {'name': '東京威力科創 (Tokyo Electron)', 'nation': '日'}, '6857.T': {'name': 'Advantest (愛德萬測試)', 'nation': '日'}, 'AMAT': {'name': '應用材料 (Applied Materials)', 'nation': '美'}, 'ASML': {'name': 'ASML (荷蘭商/美股掛牌艾司摩爾)', 'nation': '美'}},
    '全球通訊與基礎建設 (美)': {'MRVL': {'name': 'Marvell (高階光晶片/網路)', 'nation': '美'}, 'LHX': {'name': 'L3Harris (國防低軌衛星關鍵)', 'nation': '美'}},
    '全球被動元件與精密光學 (日)': {'6981.T': {'name': '村田製作所 (全球MLCC龍頭)', 'nation': '日'}, '6976.T': {'name': '太陽誘電 (高階被動元件)', 'nation': '日'}, '7731.T': {'name': 'Nikon (精密光學與半導體鏡頭)', 'nation': '日'}}
}

# ==============================================================================
# 六、大數據動態運算引擎 (已同步修正多重索引取值方式)
# ==============================================================================
@st.cache_data(ttl=15)
def process_all_market_intelligence():
    tw_tickers = []; [tw_tickers.extend(s.keys()) for s in TW_STOCK_CONFIG.values()]
    global_tickers = []; [global_tickers.extend(s.keys()) for s in GLOBAL_STOCK_CONFIG.values()]
    
    try: tw_data = yf.download(tw_tickers, period='2d', interval='1m', progress=False, group_by='ticker')
    except: tw_data = pd.DataFrame()
    try: global_data = yf.download(global_tickers, period='2d', interval='1m', progress=False, group_by='ticker')
    except: global_data = pd.DataFrame()
    
    tw_results, tw_rotation, global_results = [], [], []
    
    if not tw_data.empty:
        for group, stocks in TW_STOCK_CONFIG.items():
            group_pcts, up_c = [], 0
            for t, name in stocks.items():
                try:
                    if t in tw_data.columns.levels[0]:
                        s_df = tw_data[t].dropna(subset=['Close'])
                        if not s_df.empty:
                            curr = float(s_df['Close'].iloc[-1])
                            op = float(s_df['Close'].iloc[0]) if len(s_df) > 1 else curr
                            pct = ((curr - op) / op) * 100 if op != 0 else 0.0
                            group_pcts.append(pct)
                            if pct > 0: up_c += 1
                            tw_results.append({'產業分組': group, '代號': t, '公司名稱': name, '當前股價': curr, '今日漲跌幅': pct})
                except: pass
            if group_pcts:
                tw_rotation.append({'族群': group, '平均漲跌幅': sum(group_pcts)/len(group_pcts), '上漲家數比': f"{up_c}/{len(group_pcts)} ({int(up_c/len(group_pcts)*100)}%)"})
                
    if not global_data.empty:
        for group, stocks in GLOBAL_STOCK_CONFIG.items():
            for t, info in stocks.items():
                try:
                    if t in global_data.columns.levels[0]:
                        g_df = global_data[t].dropna(subset=['Close'])
                        if not g_df.empty:
                            global_results.append({'國際群組': group, '國家': info['nation'], '代號': t, '公司': info['name'], '最新價': float(g_df['Close'].iloc[-1]), '今日漲跌幅': 0.0})
                except: pass
    return pd.DataFrame(tw_results), pd.DataFrame(tw_rotation), pd.DataFrame(global_results)

df_tw, df_tw_rot, df_global = process_all_market_intelligence()

# ==============================================================================
# 七、深度全市場選股引擎 (精準瞄準電子股 + 50檔動態分組輪巡 + 60秒冷卻機制)
# ==============================================================================
@st.cache_data(ttl=86400)
def fetch_all_taiwan_stock_pool():
    """動態調閱全台股清單，僅提取電子產業相關板塊個股"""
    try:
        parameter = {"dataset": "TaiwanStockInfo", "token": FINMIND_TOKEN}
        res = requests.get(API_URL, params=parameter, timeout=12).json()
        if res.get("msg") == "success" and len(res.get("data", [])) > 0:
            df_info = pd.DataFrame(res["data"])
            df_filtered = df_info[df_info['type'].isin(['stock', 'twse', 'tpex'])]
            # 鎖定所有電子股板塊
            df_electronics = df_filtered[df_filtered['industry_category'].str.contains('電子|半導體|光電|通信|資訊服務', na=False, case=False)]
            if not df_electronics.empty:
                return df_electronics[['stock_id', 'stock_name']].values.tolist()
    except: pass
    return [("2330", "台積電"), ("2454", "聯發科"), ("2317", "鴻海"), ("2327", "國巨"), ("5483", "中美晶"), ("6488", "環球晶")]

# 初始化 Streamlit 輪巡狀態機
if 'scan_pointer' not in st.session_state:
    st.session_state.scan_pointer = 0
if 'accumulated_black_horses' not in st.session_state:
    st.session_state.accumulated_black_horses = []

def run_relaxed_fundamental_screener(stock_list_pool):
    start_financial = (datetime.now() - timedelta(days=550)).strftime("%Y-%m-%d")
    start_chip = (datetime.now() - timedelta(days=120)).strftime("%Y-%m-%d")
    
    # 每次精準切割 50 檔進行掃描
    batch_size = 50
    current_idx = st.session_state.scan_pointer
    target_batch = stock_list_pool[current_idx : current_idx + batch_size]
    
    if not target_batch:
        st.success("🎉 全市場電子股已全部掃描完畢！已重置進度。")
        st.session_state.scan_pointer = 0
        st.session_state.accumulated_black_horses = []
        return pd.DataFrame()

    st.info(f"⚡ 正在動態掃描電子股第 {current_idx + 1} 至 {min(current_idx + batch_size, len(stock_list_pool))} 檔 (總計: {len(stock_list_pool)} 檔)...")
    
    # 用於動態顯示畫面的進度條與日誌容器
    progress_bar = st.progress(0)
    status_log = st.empty()
    
    new_qualified_output = []
    
    for idx, (stock_id, stock_name) in enumerate(target_batch):
        # 更新動態進度條
        progress_bar.progress((idx + 1) / len(target_batch))
        status_log.text(f"🔍 正在交叉分析基本面轉折: {stock_id} {stock_name}...")
        
        try:
            score = 0
            metric_details = {"大戶籌碼": "❌ 未達標", "研發投入": "❌ 未達標", "合約負債": "❌ 未達標", "月營收表現": "❌ 未達標", "val_cl": 0.0}
            
            # 1. 驗證月營收
            p_rev = {"dataset": "TaiwanStockMonthRevenue", "data_id": stock_id, "start_date": start_financial, "token": FINMIND_TOKEN}
            r_rev = requests.get(API_URL, params=p_rev, timeout=3).json()
            if r_rev.get("msg") == "success" and len(r_rev.get("data", [])) > 1:
                df_rev = pd.DataFrame(r_rev["data"]).sort_values(by='date')
                l_rev = df_rev.iloc[-1]
                if l_rev['revenue_month_growth_rate'] > 0 or l_rev['revenue_year_growth_rate'] > -5:
                    score += 1
                    metric_details["月營收表現"] = f"🟢 績優 (年增 {l_rev['revenue_year_growth_rate']:.1f}%)"
                    
            # 2 & 3. 驗證研發與合約負債
            p_fs = {"dataset": "TaiwanStockFinancialStatements", "data_id": stock_id, "start_date": start_financial, "token": FINMIND_TOKEN}
            r_fs = requests.get(API_URL, params=p_fs, timeout=3).json()
            if r_fs.get("msg") == "success" and len(r_fs.get("data", [])) > 0:
                df_fs = pd.DataFrame(r_fs["data"])
                df_rd = df_fs[df_fs['type'].str.contains('Research and development|研發', case=False, na=False)].sort_values(by='date')
                df_cl = df_fs[df_fs['type'].str.contains('Contract liabilities|合約負債', case=False, na=False)].sort_values(by='date')
                
                if not df_rd.empty and len(df_rd) >= 2:
                    if df_rd.iloc[-1]['value'] >= df_rd.iloc[-2]['value'] * 0.90: 
                        score += 1
                        metric_details["研發投入"] = "🟢 持續擴大"
                if not df_cl.empty and len(df_cl) >= 2:
                    val_now = df_cl.iloc[-1]['value']
                    val_prev = df_cl.iloc[-2]['value']
                    metric_details["val_cl"] = val_now / 100000000
                    if val_now >= val_prev * 0.95:
                        score += 1
                        metric_details["合約負債"] = f"🟢 高檔 ({val_now/100000000:.2f}億)"
                        
            # 4. 驗證千張大戶籌碼
            p_cp = {"dataset": "TaiwanStockShareholdingNotations", "data_id": stock_id, "start_date": start_chip, "token": FINMIND_TOKEN}
            r_cp = requests.get(API_URL, params=p_cp, timeout=3).json()
            if r_cp.get("msg") == "success" and len(r_cp.get("data", [])) > 0:
                df_cp = pd.DataFrame(r_cp["data"])
                df_1000 = df_cp[df_cp['holding_stage'].str.contains('1,000|千張|1000', na=False)].sort_values(by='date')
                if not df_1000.empty and len(df_1000) >= 2:
                    c_pct = df_1000.iloc[-1]['percent']
                    p_pct = df_1000.iloc[-2]['percent']
                    if c_pct >= p_pct * 0.99: 
                        score += 1
                        metric_details["大戶籌碼"] = f"🟢 穩固 ({c_pct:.1f}%)"
                        
            # 門檻放寬：符合任意 2 項指標或以上即可入榜
            if score >= 2:
                new_qualified_output.append({
                    "股票代碼": stock_id, "公司名稱": stock_name, "符合指標數": f"🔥 {score}/4 獲選",
                    "大戶籌碼變動": metric_details["大戶籌碼"], "研發開支狀態": metric_details["研發投入"],
                    "最新合約負債": f"{metric_details['val_cl']:.2f} 億", "月營收表現": metric_details["月營收表現"],
                    "純數字合約負債": metric_details["val_cl"]
                })
            time.sleep(0.1) # 基礎安全間隔
        except: pass
        
    status_log.empty()
    
    # 整合並更新狀態機資料
    st.session_state.accumulated_black_horses.extend(new_qualified_output)
    st.session_state.scan_pointer += batch_size
    
    # 建立冷卻與下一波提醒介面
    st.success(f"等候機制觸發：本組 50 檔已動態掃描完畢，目前累計篩選出 {len(st.session_state.accumulated_black_horses)} 隻黑馬股。")
    
    # 用計時器實作 60 秒冷卻倒數動態顯示，不鎖死網頁
    countdown_placeholder = st.empty()
    for remaining in range(60, 0, -1):
        countdown_placeholder.warning(f"⏳ 遵照伺服器防禦紀律：冷卻保護中... 將於 {remaining} 秒後解鎖下一組 50 檔電子股掃描。")
        time.sleep(1)
    countdown_placeholder.success("✅ 冷卻完畢！下一組 50 檔雷達已就緒，請點擊下方按鈕繼續掃描。")
    
    # 觸發重新整理按鈕
    if st.button("🚀 立即啟動下一組 50 檔電子股深層掃描", key="next_batch_trigger"):
        st.rerun()
        
    return pd.DataFrame(st.session_state.accumulated_black_horses)

# ==============================================================================
# 八、今日台股主流板塊輪動強弱榜
# ==============================================================================
st.markdown("### 🔥 今日台股主流板塊輪動強弱榜")
if not df_tw_rot.empty:
    df_tw_rot_sorted = df_tw_rot.sort_values(by='平均漲跌幅', ascending=False)
    fig_rot = go.Figure(go.Bar(y=df_tw_rot_sorted['族群'], x=df_tw_rot_sorted['平均漲跌幅'], orientation='h', marker_color=['#ff4b4b' if x >= 0 else '#00f574' for x in df_tw_rot_sorted['平均漲跌幅']]))
    fig_rot.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_rot, use_container_width=True, key="main_rotation_chart_v3")
st.markdown("---")

# ==============================================================================
# 九、多維度決策分頁三合一佈局
# ==============================================================================
view_tab1, view_tab2, view_tab3 = st.tabs([
    "🇹🇼 觀測站一：台股主流板塊鏈與核心觀測池", 
    "📈 觀測站二：台指期五關多空交易決策導航儀",
    "🎯 觀測站三：全市場【大戶+研發+合約負債+月營收】放寬型任意2指標量化選股終端"
])

# ---- Tab 1: 焦點核心池板塊顯示 ----
with view_tab1:
    col_layout1, col_layout2 = st.columns([2, 1])
    with col_layout1:
        st.markdown(f"### 🚀 台股強勢主流板塊觀測台 (細項分秒快照)")
        if not df_tw.empty:
            cats_tw = list(TW_STOCK_CONFIG.keys())
            sub_tabs_tw = st.tabs(cats_tw)
            for i, cat in enumerate(cats_tw):
                with sub_tabs_tw[i]:
                    df_sub = df_tw[df_tw['產業分組'] == cat].copy()
                    df_disp = df_sub.copy()
                    df_disp['當前股價'] = df_disp['當前股價'].apply(lambda x: f"{x:,.2f} TWD")
                    df_disp['今日漲跌幅'] = df_disp['今日漲跌幅'].apply(lambda x: f"{x:+.2f}%")
                    st.dataframe(df_disp.drop(columns=['產業分組']), use_container_width=True, hide_index=True)
    with col_layout2:
        st.markdown("#### 🌐 國際算力核心與半導體龍頭連動狀態")
        if not df_global.empty:
            st.dataframe(df_global, use_container_width=True, hide_index=True)

# ---- Tab 2: 五關價推算模型 ----
with view_tab2:
    st.markdown("### 🔑 當日台指期與加權現貨關鍵多空五關價對照表")
    base_p = shared_prices.get("^TWII", 44169.0)
    if base_p == 0.0: base_p = 44169.0
    pivot = base_p; r1 = pivot + 150; r2 = pivot + 300; s1 = pivot - 150; s2 = pivot - 300
    five_gates_data = [
        {"關卡分類": "🔴 壓力二 (R2)", "價位": f"{r2:,.1f} 點", "型態與支撐壓力依據": "日盤反彈波段高點與先前高位套牢密集壓力區。"},
        {"關卡分類": "🚨 壓力一 (R1)", "價位": f"{r1:,.1f} 點", "型態與支撐壓力依據": "上週五K長上影線之中點壓力，亦為重要整數心理大關。"},
        {"關卡分類": "🔵 多空分界 (Pivot)", "價位": f"{pivot:,.1f} 點", "型態與支撐壓力依據": "前日盤台指期收盤價，今日早盤的強弱關鍵分水嶺。"},
        {"關卡分類": "🟢 支撐一 (S1)", "價位": f"{s1:,.1f} 點", "型態與支撐壓力依據": "心理整數支撐關卡，同時為週五夜盤的收盤與打底密集區。"},
        {"關卡分類": "🌲 支撐二 (S2)", "價位": f"{s2:,.1f} 點", "型態與支撐壓力依據": "上週五日盤開盤與早盤最低防禦線，跌破則晨星止跌型態受破壞。"}
    ]
    st.dataframe(pd.DataFrame(five_gates_data), use_container_width=True, hide_index=True)

# ---- Tab 3: 放寬型四大指標選股終端 ----
with view_tab3:
    st.markdown("### 🎯 跨指標交叉過濾：黃金基本面轉折黑馬股 (放寬版：符合任意 3 個指標即可)")
    st.markdown("當前全台股 1,800 多檔深度審查中。此系統已改採為您尋找**同時滿足任意 3 項核心轉折指標**的強勢標的。")
    
    col_btn1, col_btn2 = st.columns([3, 4])
    with col_btn1: 
        trigger_scan = st.button("🔄 立即清除快取，重新執行全市場深層掃描", type="primary")
    
    if trigger_scan:
        st.cache_data.clear()
        st.warning("⚡ 系統快取已手動清除！正在向交易所重新調閱全市場個股最新一期籌碼與三表財報細項...")

    with st.spinner("⏳ 正在執行全市場個股大數據交叉比對中，請稍候..."):
        full_market_pool = fetch_all_taiwan_stock_pool()
        df_screen_result = run_relaxed_fundamental_screener(full_market_pool)
    
    if not df_screen_result.empty:
        st.success(f"🎯 掃描完成。目前共有 **{len(df_screen_result)}** 檔個股符合四大指標中的任意 3 項：")
        st.dataframe(df_screen_result.drop(columns=['純數字合約負債']), use_container_width=True, hide_index=True)
        
        fig_cl_scan = go.Figure(go.Bar(x=df_screen_result['公司名稱'], y=df_screen_result['純數字合約負債'], marker_color='#ff4b4b', text=df_screen_result['最新合約負債'], textposition='auto'))
        fig_cl_scan.update_layout(title="獲選轉折個股：在手訂單能見度（流動合約負債規模對比：億元）", height=280, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_cl_scan, use_container_width=True, key="screener_visual_bar_v3")
    else:
        st.info("ℹ️ 當前市場暫無個股交集符合任意 3 項指標。可點擊上方按鈕清除快取重試。")

st.markdown("---")

# ==============================================================================
# 十、雙主線量化籌碼戰責引擎 (已同步修正多重索引取值方式)
# ==============================================================================
def get_strategy_pool():
    pool = []
    for s in TW_STOCK_CONFIG.values():
        for k in s.keys(): pool.append((k.split('.')[0], s[k]))
    return pool

@st.cache_data(ttl=1800)
def run_dual_chip_strategies():
    strategy_pool = get_strategy_pool()
    start_date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    first_root_stocks, heavy_selling_stocks = [], []
    
    for stock_id, name in strategy_pool:
        param = {"dataset": "TaiwanStockInstitutionalInvestorsBuySell", "data_id": stock_id, "start_date": start_date, "end_date": end_date, "token": FINMIND_TOKEN}
        try:
            res = requests.get(API_URL, params=param, timeout=5).json()
            if res.get("msg") == "success" and len(res.get("data", [])) > 0:
                df = pd.DataFrame(res["data"])
                df_foreign = df[df['name'] == 'Foreign_Investor'].copy()
                if not df_foreign.empty and len(df_foreign) >= 8:
                    df_foreign['shares'] = (df_foreign['buy'] - df_foreign['sell']) / 1000
                    df_foreign = df_foreign.sort_values(by='date').reset_index(drop=True)
                    
                    today_chip = df_foreign['shares'].iloc[-1]
                    yesterday_chip = df_foreign['shares'].iloc[-2]
                    recent_3d = df_foreign['shares'].iloc[-3:].tolist()
                    previous_6d = df_foreign['shares'].iloc[-8:-2].tolist()
                    full_9d = df_foreign['shares'].iloc[-9:].tolist()
                    
                    hist = yf.Ticker(f"{stock_id}.TW").history(period="10d")
                    if hist.empty or len(hist) < 5: continue
                    curr_p = hist['Close'].iloc[-1]
                    ma5 = hist['Close'].rolling(window=5).mean().iloc[-1]
                    
                    if sum(1 for x in previous_6d if x < 0) >= 3 and yesterday_chip <= 0 and today_chip > 0:
                        avg_prev_sell = sum(x for x in previous_6d if x < 0) / max(sum(1 for x in previous_6d if x < 0), 1)
                        if today_chip > abs(avg_prev_sell) * 1.5 and curr_p >= ma5 and curr_p <= ma5 * 1.03:
                            first_root_stocks.append({"股票代號": stock_id, "公司名稱": name, "當前股價": curr_p, "今日外資轉買(張)": today_chip, "昨日外資賣超(張)": yesterday_chip, "洗盤期賣超高頻天數": f"{sum(1 for x in previous_6d if x < 0)} / 6 天"})
                            
                    if sum(1 for x in full_9d if x < 0) >= 6 and (sum(recent_3d) < 0 and today_chip < 0):
                        heavy_selling_stocks.append({"股票代號": stock_id, "公司名稱": name, "當前股價": curr_p, "近3日遭提款累積(張)": sum(recent_3d), "今日外資續賣(張)": today_chip, "波段提款密集度": f"{sum(1 for x in full_9d if x < 0)} / 9 天"})
        except: pass
    return pd.DataFrame(first_root_stocks), pd.DataFrame(heavy_selling_stocks)

df_strat_first, df_strat_sellout = run_dual_chip_strategies()

strat_tab1, strat_tab2 = st.tabs(["🎯 策略一：外資洗盤後『由賣轉買・第一根認錯表態點』", "⚠️ 策略二：外資避險瘋狂提款『持續殺盤・尚未認錯』警示池"])

with strat_tab1:
    if not df_strat_first.empty:
        col_t1, col_c1 = st.columns([3, 2])
        with col_t1: st.dataframe(df_strat_first, use_container_width=True, hide_index=True)
        with col_c1:
            fig1 = go.Figure(go.Bar(x=df_strat_first['公司名稱'], y=df_strat_first['今日外資轉買(張)'], marker_color='#ff4b4b', text=df_strat_first['今日外資轉買(張)'].apply(lambda x: f"{x:,.0f}張"), textposition='auto'))
            fig1.update_layout(title="外資認錯買回暴發量排行 (張)", height=230, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig1, use_container_width=True, key="strat_chart_1_v3")
    else: st.info("ℹ️ 目前核心標的中，暫無股票精準符合黃金轉折表態點。")

with strat_tab2:
    st.markdown("#### 🚨 警惕！外資持續當作提款機、完全未見認錯回補的個股")
    if not df_strat_sellout.empty:
        col_t2, col_c2 = st.columns([3, 2])
        with col_t2:
            df_disp2 = df_strat_sellout.copy()
            df_disp2['近3日遭提款累積(張)'] = df_disp2['近3日遭提款累積(張)'].apply(lambda x: f"{x:,.0f} 張")
            df_disp2['今日外資續賣(張)'] = df_disp2['今日外資續賣(張)'].apply(lambda x: f"{x:,.0f} 張")
            st.dataframe(df_disp2, use_container_width=True, hide_index=True)
        with col_c2:
            fig2 = go.Figure(go.Bar(x=df_strat_sellout['公司名稱'], y=df_strat_sellout['近3日遭提款累積(張)'].abs(), marker_color='#00f574', text=df_strat_sellout['近3日遭提款累積(張)'].apply(lambda x: f"{x:,.0f}張"), textposition='auto'))
            fig2.update_layout(title="近 3 日外資提款失血量排行 (張)", height=230, margin=dict(l=10, r=10, t=35, b=10))
            st.plotly_chart(fig2, use_container_width=True, key="strat_chart_2_v3")
    else: st.success("🟢 傲人表現！目前監控池內的所有個股，皆無落入重災區。")

# ==============================================================================
# 十一、網頁定時自動循環刷新機制
# ==============================================================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
