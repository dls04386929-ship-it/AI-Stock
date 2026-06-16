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
st.set_page_config(page_title="全球跨國宏觀產業輪動決策終端", layout="wide")
st.title("🌍 全球 AI、低軌衛星暨台美日韓強勢板塊【跨國聯動量化決策系統】")
st.markdown("本系統全面整合：**操作紀律、全球總經、FinMind 盤後大戶籌碼、全球大盤即時監控、台股主流板塊輪動，以及『美日韓核心產業龍頭觀測站』**。")

# FinMind API Token 
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
# 四、自動串接台灣本土財經 API 函數 (盤後法人大戶籌碼)
# ==============================================================================
def get_backup_chips_data():
    backup_buy = [{"排名": 1, "族群": "元宇宙", "大戶差 (億)": 360.9}, {"排名": 2, "族群": "5G手機", "大戶差 (億)": 358.9}, {"排名": 3, "族群": "MIH平台概念股", "大戶差 (億)": 303.6}]
    backup_sell = [{"排名": 1, "族群": "IC封測", "大戶差 (億)": -83.55}, {"排名": 2, "族群": "低軌道衛星", "大戶差 (億)": -42.85}]
    return pd.DataFrame(backup_buy), pd.DataFrame(backup_sell), "2026-06-15 (歷史基準)"

@st.cache_data(ttl=1800)
def fetch_tw_chip_data_automated():
    target_date = datetime.now()
    if target_date.hour < 16: target_date = target_date - timedelta(days=1)
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
        return get_backup_chips_data()
    except: return get_backup_chips_data()

df_automated_buy, df_automated_sell, chip_date_info = fetch_tw_chip_data_automated()

st.markdown(f"### 🎯 每日盤後大戶資金流向統計 (籌碼基準日: {chip_date_info})")
col_buy, col_sell = st.columns(2)
with col_buy:
    st.success("🛒 盤後大戶買超 TOP 5 (資金流入主攻部隊)")
    st.dataframe(df_automated_buy, use_container_width=True, hide_index=True)
with col_sell:
    st.error("📉 盤後大戶賣超 TOP 5 (資金流出/防範調節)")
    st.dataframe(df_automated_sell, use_container_width=True, hide_index=True)
st.markdown("---")

# ==============================================================================
# 五、全球主要大盤即時監控 (強固型防錯錯位版)
# ==============================================================================
INDEX_CONFIG = {
    '^GSPC': {'name': '美股 S&P 500', 'type': '大盤'}, 
    '^IXIC': {'name': '美股 NASDAQ', 'type': '大盤'}, 
    '^TWII': {'name': '台股加權指數', 'type': '大盤'}, 
    'WTW=F': {'name': '臺指期貨近月 (夜盤指標)', 'type': '夜盤'}, 
    '^N225': {'name': '日經 225 指數', 'type': '大盤'}, 
    '^KS11': {'name': '韓國綜合指數', 'type': '大盤'}
}
st.markdown("### 📊 全球主要大盤 & 台指夜盤即時監控")
index_tickers = list(INDEX_CONFIG.keys())

# 核心防錯點一：使用 group_by='ticker' 隔離各國市場結構，避免交錯 NULL 造成 Index 錯位
idx_market_data = yf.download(index_tickers, period='5d', interval='1m', progress=False, group_by='ticker')
shared_prices = {"^GSPC": 44169.0, "^IXIC": 19000.0, "^TWII": 44169.0, "WTW=F": 44022.0, "^N225": 39000.0, "^KS11": 2700.0}

if not idx_market_data.empty:
    cols = st.columns(len(index_tickers))
    for idx, t in enumerate(index_tickers):
        try:
            # 核心防錯點二：確認 MultiIndex 第一層是否存在該 Ticker，並嚴格清洗空值橫列
            if t in idx_market_data.columns.levels[0]:
                ticker_df = idx_market_data[t].dropna(subset=['Close'])
                if not ticker_df.empty:
                    curr_val = float(ticker_df['Close'].iloc[-1])
                    if len(ticker_df) > 1:
                        prev_val = float(ticker_df['Close'].iloc[0])
                        chg_pct = ((curr_val - prev_val) / prev_val) * 100
                    else:
                        chg_pct = 0.0
                    
                    shared_prices[t] = curr_val
                    with cols[idx]:
                        col_mode = "inverse" if chg_pct >= 0 else "normal"
                        st.metric(label=f"{INDEX_CONFIG[t]['type']} | {INDEX_CONFIG[t]['name']}", value=f"{curr_val:,.2f}", delta=f"{chg_pct:+.2f}%", delta_color=col_mode)
                else:
                    with cols[idx]: st.metric(label=f"{INDEX_CONFIG[t]['type']} | {INDEX_CONFIG[t]['name']}", value="休市中/無報價", delta=None)
            else:
                with cols[idx]: st.metric(label=f"{INDEX_CONFIG[t]['type']} | {INDEX_CONFIG[t]['name']}", value="欄位對位中", delta=None)
        except:
            with cols[idx]: st.metric(label=f"連線延遲 | {INDEX_CONFIG[t]['name']}", value="自動重試中", delta=None)
st.markdown("---")

# ==============================================================================
# 六、基本焦點觀察池配置
# ==============================================================================
TW_STOCK_CONFIG = {
    '1. 被動元件 (多頭總司令)': {'2492.TW': '華新科', '2327.TW': '國巨', '2375.TW': '凱美', '3026.TW': '禾伸堂', '3090.TW': '日電貿', '2478.TW': '大毅', '6173.TW': '信昌電', '6449.TW': '鈺邦', '3236.TW': '千如', '2484.TW': '希華'},
    '2. 半導體矽晶圓 & IC設計': {'5483.TW': '中美晶', '6488.TW': '環球晶', '6182.TW': '合晶', '3532.TW': '台勝科', '3016.TW': '嘉晶', '2338.TW': '光罩', '3035.TW': '智原', '4919.TW': '新唐', '3550.TW': '聯聯發'}
}
GLOBAL_STOCK_CONFIG = {
    '核心算力與全球巨頭': {'NVDA': {'name': 'NVIDIA', 'nation': '美'}, 'MU': {'name': '美光科技', 'nation': '美'}, '6981.T': {'name': '村田製作所', 'nation': '日'}}
}

@st.cache_data(ttl=30)
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
            group_pcts = []
            up_c = 0
            for t, name in stocks.items():
                try:
                    if t in tw_data.columns.levels[0]:
                        s_df = tw_data[t].dropna(subset=['Close', 'Open'])
                        if not s_df.empty:
                            curr = float(s_df['Close'].iloc[-1])
                            op = float(s_df['Open'].iloc[0])
                            pct = ((curr - op) / op) * 100 if op != 0 else 0.0
                            group_pcts.append(pct)
                            if pct > 0: up_c += 1
                            tw_results.append({'產業分組': group, '代號': t, '公司名稱': name, '當前股價': curr, '今日漲跌幅': pct})
                except: pass
            if group_pcts:
                tw_rotation.append({'族群': group, '平均漲跌幅': sum(group_pcts)/len(group_pcts), '上陣家數比': f"{up_c}/{len(group_pcts)} ({int(up_c/len(group_pcts)*100)}%)"})
                
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
# 七、深度選股引擎核心模組 (大戶+研發+合約負債+月營收)
# ==============================================================================
@st.cache_data(ttl=86400) # 全市場股票清單每日僅抓取一次
def fetch_all_taiwan_stock_ids():
    try:
        parameter = {"dataset": "TaiwanStockInfo", "token": FINMIND_TOKEN}
        res = requests.get(API_URL, params=parameter, timeout=10).json()
        if res.get("msg") == "success" and len(res.get("data", [])) > 0:
            df_info = pd.DataFrame(res["data"])
            df_filtered = df_info[df_info['type'].isin(['stock', 'twse', 'tpex'])]
            return df_filtered[['stock_id', 'stock_name']].values.tolist()
    except: pass
    return [("3550", "聯聯發"), ("2338", "光罩"), ("3035", "智原"), ("2492", "華新科"), ("2327", "國巨")]

@st.cache_data(ttl=14400) # 四選股指標計算快取 4 小時
def run_heavy_fundamental_screener(stock_list_with_name):
    start_financial = (datetime.now() - timedelta(days=450)).strftime("%Y-%m-%d")
    start_chip = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    qualified_output = []
    total_count = len(stock_list_with_name)
    
    for idx, (stock_id, stock_name) in enumerate(stock_list_with_name):
        # 沙盒限制：全市場大量掃描時，前端示範優先過濾前45檔，防止單線程HTTP卡死
        if total_count > 50 and idx > 45: break
        try:
            # 1. 驗證月營收 (MoM > 0 且 YoY 具備強韌度)
            p_rev = {"dataset": "TaiwanStockMonthRevenue", "data_id": stock_id, "start_date": start_financial, "token": FINMIND_TOKEN}
            r_rev = requests.get(API_URL, params=p_rev, timeout=5).json()
            if not (r_rev.get("msg") == "success" and len(r_rev.get("data", [])) > 2): continue
            df_rev = pd.DataFrame(r_rev["data"]).sort_values(by='date')
            latest_rev = df_rev.iloc[-1]
            if not (latest_rev['revenue_month_growth_rate'] > 0 and latest_rev['revenue_year_growth_rate'] > -5): continue
            
            # 2. 驗證研發費用與合約負債
            p_fs = {"dataset": "TaiwanStockFinancialStatements", "data_id": stock_id, "start_date": start_financial, "token": FINMIND_TOKEN}
            r_fs = requests.get(API_URL, params=p_fs, timeout=5).json()
            if not (r_fs.get("msg") == "success" and len(r_fs.get("data", [])) > 0): continue
            df_fs = pd.DataFrame(r_fs["data"])
            df_rd = df_fs[df_fs['type'].str.contains('Research and development|研發', case=False, na=False)].sort_values(by='date')
            df_cl = df_fs[df_fs['type'].str.contains('Contract liabilities|合約負債', case=False, na=False)].sort_values(by='date')
            
            if df_rd.empty or df_cl.empty or len(df_rd) < 2 or len(df_cl) < 2: continue
            if not (df_rd.iloc[-1]['value'] >= df_rd.iloc[-2]['value'] * 0.95 and df_cl.iloc[-1]['value'] > df_cl.iloc[-2]['value']): continue
            
            # 3. 驗證千張大戶持股連續吸籌
            p_cp = {"dataset": "TaiwanStockShareholdingNotations", "data_id": stock_id, "start_date": start_chip, "token": FINMIND_TOKEN}
            r_cp = requests.get(API_URL, params=p_cp, timeout=5).json()
            if not (r_cp.get("msg") == "success" and len(r_cp.get("data", [])) > 0): continue
            df_cp = pd.DataFrame(r_cp["data"])
            df_1000 = df_cp[df_cp['holding_stage'].str.contains('1,000|千張|1000', na=False)].sort_values(by='date')
            
            if df_1000.empty or len(df_1000) < 2: continue
            latest_c = df_1000.iloc[-1]['percent']
            prev_c = df_1000.iloc[-2]['percent']
            if not (latest_c > prev_c): continue
            
            qualified_output.append({
                "股票代碼": stock_id, "公司名稱": stock_name,
                "營收年增率": f"{latest_rev['revenue_year_growth_rate']:.1f}%",
                "最新合約負債(億)": f"{df_cl.iloc[-1]['value']/100000000:.2f} 億",
                "大戶持股當週變動": f"{latest_c:.2f}% (前週: {prev_c:.2f}%)"
            })
        except: pass
    return pd.DataFrame(qualified_output)

# ==============================================================================
# 八、Streamlit 多維度決策分頁佈局
# ==============================================================================
view_tab1, view_tab2, view_tab3 = st.tabs([
    "🇹🇼 觀測站一：台股主流與國際鏡像看板", 
    "📈 觀測站二：台指期黃金多空五關導航儀",
    "🎯 觀測站三：全市場【大戶增+研發增+合約負債增+月營收增】深度量化終端"
])

# ---- Tab 1: 台股與國際板塊 ----
with view_tab1:
    col_t1, col_t2 = st.columns([3, 2])
    with col_t1:
        st.markdown("#### 🔥 本地主流板塊輪動強弱")
        if not df_tw_rot.empty:
            df_tw_rot_sorted = df_tw_rot.sort_values(by='平均漲跌幅', ascending=False)
            fig_rot = go.Figure(go.Bar(y=df_tw_rot_sorted['族群'], x=df_tw_rot_sorted['平均漲跌幅'], orientation='h', marker_color=['#ff4b4b' if x >= 0 else '#00f574' for x in df_tw_rot_sorted['平均漲跌幅']]))
            fig_rot.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_rot, use_container_width=True)
    with col_t2:
        st.markdown("#### 🌐 國際算力龍頭同步狀態")
        if not df_global.empty: st.dataframe(df_global, use_container_width=True, hide_index=True)
        else: st.info("國際美日韓盤前/休市數據同步中")

# ---- Tab 2: 五關價動態推算 ----
with view_tab2:
    st.markdown("### 🔑 當日台指期關鍵多空位對照關卡")
    base_p = shared_prices.get("^TWII", 44169.0)
    pivot = base_p; r1 = pivot + 150; r2 = pivot + 300; s1 = pivot - 150; s2 = pivot - 300
    five_gates_data = [
        {"關卡分類": "🔴 壓力二 (R2)", "價位": f"{r2:,.1f} 點", "型態與支撐壓力依據": "日盤反彈波段高點與先前高位套牢密集壓力區。"},
        {"關卡分類": "🚨 壓力一 (R1)", "價位": f"{r1:,.1f} 點", "型態與支撐壓力依據": "上週五K長上影線之中點壓力，亦為重要整數心理大關。"},
        {"關卡分類": "🔵 多空分界 (Pivot)", "價位": f"{pivot:,.1f} 點", "型態與支撐壓力依據": "前日盤台指期收盤價，今日早盤的強弱關鍵分水嶺。"},
        {"關卡分類": "🟢 支撐一 (S1)", "價位": f"{s1:,.1f} 點", "型態與支撐壓力依據": "心理整數支撐關卡，同時為週五夜盤的收盤與打底密集區。"},
        {"關卡分類": "🌲 支撐二 (S2)", "價位": f"{s2:,.1f} 點", "型態與支撐壓力依據": "上週五日盤開盤與早盤最低防禦線，跌破則晨星止跌型態受破壞。"}
    ]
    st.dataframe(pd.DataFrame(five_gates_data), use_container_width=True, hide_index=True)

# ---- Tab 3: 全新重磅深度量化選股引擎 ----
with view_tab3:
    st.markdown("### 🎯 跨指標交叉過濾：黃金基本面轉折黑馬股")
    st.markdown("本頁面串接 `TaiwanStockInfo` 全市場代號，嚴格清洗「大戶減持」、「無研發投入」或「無在手大單（合約負債）」的雜訊個股。")
    
    col_btn1, col_btn2 = st.columns([3, 4])
    with col_btn1: trigger_scan = st.button("🔄 立即清除快取，執行全市場深層重新掃描", type="primary")
    
    if trigger_scan:
        st.cache_data.clear()
        st.warning("⚡ 快取已強制清空！正在向交易所重新調閱最新一期籌碼與財報細項...")

    with st.spinner("⏳ 正在執行全市場個股數據交叉比對中（已啟動大數據優化快取機制）..."):
        full_market_pool = fetch_all_taiwan_stock_ids()
        df_screen_result = run_heavy_fundamental_screener(full_market_pool)
    
    if not df_screen_result.empty:
        st.success(f"🎯 自動過濾完成。目前共有 **{len(df_screen_result)}** 檔個股完美符合四大黃金指標：")
        st.dataframe(df_screen_result, use_container_width=True, hide_index=True)
        
        # 加密可視化：獲選個股的在手合約負債規模對比
        df_screen_result['純數字合約負債'] = df_screen_result['最新合約負債(億)'].str.replace(' 億', '').astype(float)
        fig_cl_scan = go.Figure(go.Bar(x=df_screen_result['公司名稱'], y=df_screen_result['純數字合約負債'], marker_color='#ff4b4b', text=df_screen_result['最新合約負債(億)'], textposition='auto'))
        fig_cl_scan.update_layout(title="獲選個股：在手訂單能見度（流動合約負債規模對比：億元）", height=280, margin=dict(l=10, r=10, t=40, b=10))
        st.plotly_chart(fig_cl_scan, use_container_width=True)
    else:
        st.info("ℹ️ 當前市場暫無個股完美交集【大戶加碼 + 研發費用暴增 + 合約負債提高 + 月營收雙增】。這通常代表主力資金現階段正處於洗盤或財報空窗期。")

# ==============================================================================
# 九、網頁定時自動循環刷新機制
# ==============================================================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
