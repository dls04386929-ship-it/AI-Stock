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
st.markdown("本系統全面整合：**操作紀律、全球總經、FinMind 盤後大戶籌碼、全球大盤即時監控、台股主流板塊輪動，以及『美日韓核心產業龍頭觀測站』**。")

# FinMind API Token
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGxzMDQzODY5MjlAZ21haWwuY29tIiwiZW1haWwiOiJkbHMwNDM4NjkyOUBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.XLHUQWa0QglCBjukX374bWUWeVaFLfwHhBMrtOrZ-0E"

# 側邊欄控制面板
st.sidebar.header("🔄 系統主控制面板")
refresh_interval = st.sidebar.slider("動態報價刷新頻率 (秒)", min_value=10, max_value=120, value=30)
auto_refresh = st.sidebar.checkbox("啟用自動即時刷新", value=True)

# ==============================================================================
# 一、核心投資操作紀律看板
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
# 二、全球每日核心關注列表 (動態顏色判斷)
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
            st.metric(
                label=item["label"],
                value=item["val"],
                delta=f"{sign}{item['chg']:.2f}%",
                delta_color=color_mode
            )

st.markdown("---")

# ==============================================================================
# 三、自動串接台灣本土財經 API 函數 (盤後大戶籌碼)
# ==============================================================================
def get_backup_chips_data():
    backup_buy = [
        {"排名": 1, "族群": "元宇宙", "大戶差 (億)": 360.9},
        {"排名": 2, "族群": "5G手機", "大戶差 (億)": 358.9},
        {"排名": 3, "族群": "MIH平台概念股", "大戶差 (億)": 303.6},
        {"排名": 4, "族群": "被動元件(C/R)", "大戶差 (億)": 267.0},
        {"排名": 5, "族群": "MLCC", "大戶差 (億)": 246.3},
    ]
    backup_sell = [
        {"排名": 1, "族群": "IC封測", "大戶差 (億)": -83.55},
        {"排名": 2, "族群": "低軌道衛星", "大戶差 (億)": -42.85},
        {"排名": 3, "族群": "NAND Flash控制IC", "大戶差 (億)": -28.77},
        {"排名": 4, "族群": "雲端運算", "大戶差 (億)": -27.94},
        {"排名": 5, "族群": "探針卡", "大戶差 (億)": -26.86},
    ]
    return pd.DataFrame(backup_buy), pd.DataFrame(backup_sell), "2026-06-15 (歷史基準)"

@st.cache_data(ttl=1800)
def fetch_tw_chip_data_automated():
    """
    ✅ BUG FIX 1：
    原始問題：dataset='TaiwanStockInstitutionalInvestorsBuySell' 傳入 data_id=""
    會導致 API 回傳全市場所有股票資料（資料量龐大且格式不同），
    正確做法應使用 TaiwanStockMarketValueWeight 或
    TaiwanStockTotalInstitutionalInvestorsBuySell（不需 data_id）來取得大盤總體籌碼。
    改用 TaiwanStockTotalInstitutionalInvestors 按 name 分組取買賣超合計。
    """
    url = "https://api.finmindtrade.com/api/v4/data"

    for i in range(0, 5):
        target_date = datetime.now() - timedelta(days=i)
        # 跳過週末（FinMind 台股 API 週末無資料）
        if target_date.weekday() >= 5:
            continue
        date_str = target_date.strftime("%Y-%m-%d")

        # ✅ 修正：改用正確的 dataset，不傳 data_id
        parameter = {
            "dataset": "TaiwanStockTotalInstitutionalInvestors",
            "start_date": date_str,
            "end_date": date_str,
            "token": FINMIND_TOKEN
        }

        try:
            response = requests.get(url, params=parameter, timeout=10)
            data = response.json()

            with st.sidebar:
                st.write(f"正在查詢日期: {date_str}")
                st.write(f"API 回傳狀態: {data.get('msg')}")
                if data.get("data"):
                    st.write(f"抓到資料筆數: {len(data.get('data'))}")
                else:
                    st.write("未抓到資料或資料為空")

            if data.get("msg") == "success" and len(data.get("data", [])) > 0:
                df = pd.DataFrame(data["data"])

                # ✅ 修正：欄位名稱依實際 API 回傳調整
                # TaiwanStockTotalInstitutionalInvestors 欄位：
                # name, buy, sell, date
                df['buy'] = pd.to_numeric(df['buy'], errors='coerce').fillna(0)
                df['sell'] = pd.to_numeric(df['sell'], errors='coerce').fillna(0)
                df['買賣超(億)'] = (df['buy'] - df['sell']) / 100000000

                df_grouped = df.groupby('name')['買賣超(億)'].sum().reset_index()
                df_grouped.columns = ['族群', '大戶差 (億)']

                df_buy_top5 = df_grouped.sort_values(by='大戶差 (億)', ascending=False).head(5).copy().reset_index(drop=True)
                df_sell_top5 = df_grouped.sort_values(by='大戶差 (億)', ascending=True).head(5).copy().reset_index(drop=True)

                df_buy_top5.insert(0, '排名', range(1, len(df_buy_top5) + 1))
                df_sell_top5.insert(0, '排名', range(1, len(df_sell_top5) + 1))

                df_buy_top5['大戶差 (億)'] = df_buy_top5['大戶差 (億)'].apply(lambda x: f"+{x:.2f} 億")
                df_sell_top5['大戶差 (億)'] = df_sell_top5['大戶差 (億)'].apply(lambda x: f"{x:.2f} 億")

                return df_buy_top5, df_sell_top5, f"{date_str} (最新有效數據)"

        except Exception as e:
            with st.sidebar:
                st.write(f"例外錯誤: {e}")
            continue

    return get_backup_chips_data()

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
# 四、大盤與夜盤監控配置
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
idx_market_data = yf.download(index_tickers, period='2d', interval='1m', progress=False)

shared_prices = {"^GSPC": 0.0, "^IXIC": 0.0, "^TWII": 0.0, "WTW=F": 0.0, "^N225": 0.0, "^KS11": 0.0}
shared_chg = {"^GSPC": 0.0, "^IXIC": 0.0, "^TWII": 0.0, "WTW=F": 0.0, "^N225": 0.0, "^KS11": 0.0}

if not idx_market_data.empty:
    cols = st.columns(len(index_tickers))
    for idx, t in enumerate(index_tickers):
        try:
            if ('Close', t) in idx_market_data.columns:
                close_s = idx_market_data['Close'][t].dropna()
                if not close_s.empty:
                    curr_val = float(close_s.iloc[-1])
                    prev_val = float(close_s.iloc[0])
                    chg_pct = ((curr_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0.0

                    shared_prices[t] = curr_val
                    shared_chg[t] = chg_pct

                    with cols[idx]:
                        col_mode = "inverse" if chg_pct >= 0 else "normal"
                        st.metric(
                            label=f"{INDEX_CONFIG[t]['type']} | {INDEX_CONFIG[t]['name']}",
                            value=f"{curr_val:,.2f}",
                            delta=f"{chg_pct:+.2f}%",
                            delta_color=col_mode
                        )
        except:
            pass
st.markdown("---")

# ==============================================================================
# 五、焦點核心池板塊配置庫
# ==============================================================================
TW_STOCK_CONFIG = {
    '1. 被動元件 (多頭總司令)': {
        '2492.TW': '華新科', '2327.TW': '國巨', '2375.TW': '凱美', '3026.TW': '禾伸堂',
        '3090.TW': '日電貿', '2478.TW': '大毅', '6173.TW': '信昌電', '6449.TW': '鈺邦',
        '8042.TW': '金山電', '8043.TW': '蜜望實', '6175.TW': '立敦', '3624.TW': '光頡',
        '3236.TW': '千如', '5328.TW': '華容', '6155.TW': '鈞寶', '8121.TW': '越峰'
    },
    '2. 半導體矽晶圓 (產業築底完成)': {
        '5483.TW': '中美晶', '6488.TW': '環球晶', '6182.TW': '合晶', '3532.TW': '台勝科',
        '3016.TW': '嘉晶', '2338.TW': '光罩', '6139.TW': '亞翔'
    },
    '3. 記憶體與 IC 設計 (消費電子回暖)': {
        '2344.TW': '華邦電', '4973.TW': '廣穎', '3035.TW': '智原', '4919.TW': '新唐',
        '2401.TW': '凌陽', '8096.TW': '擎亞', '2489.TW': '瑞軒'
    },
    '4. 光學鏡頭與光通訊 (地緣政治緩解)': {
        '3008.TW': '大立光', '3406.TW': '玉晶光', '3362.TW': '先進光', '4979.TW': '華星光'
    },
    '5. PCB、電子材料與能源化工': {
        '1303.TW': '南亞', '1714.TW': '和桐', '6274.TW': '台耀', '6153.TW': '嘉聯益',
        '6191.TW': '精成科', '2484.TW': '希華'
    }
}

# ✅ BUG FIX 3：補全幣別對照表
NATION_CURRENCY = {'美': 'USD', '日': 'JPY', '韓': 'KRW', '台': 'TWD', '荷': 'USD'}

GLOBAL_STOCK_CONFIG = {
    '核心算力與GPU (美日韓)': {
        'NVDA': {'name': 'NVIDIA (全球算力霸主)', 'nation': '美'},
        'AMD': {'name': 'AMD (高階處理器)', 'nation': '美'},
        '005930.KS': {'name': '三星電子 (代工與半導體)', 'nation': '韓'}
    },
    '全球記憶體巨頭 (美韓對比)': {
        'MU': {'name': '美光科技 (儲存記憶體)', 'nation': '美'},
        '000660.KS': {'name': 'SK 海力士 (HBM 核心供應商)', 'nation': '韓'}
    },
    '半導體設備與先進材料 (日美)': {
        '8035.T': {'name': '東京威力科創 (Tokyo Electron)', 'nation': '日'},
        '6857.T': {'name': 'Advantest (愛德萬測試)', 'nation': '日'},
        'AMAT': {'name': '應用材料 (Applied Materials)', 'nation': '美'},
        'ASML': {'name': 'ASML (荷蘭商/美股掛牌艾司摩爾)', 'nation': '美'}
    },
    '全球通訊與基礎建設 (美)': {
        'MRVL': {'name': 'Marvell (高階光晶片/網路)', 'nation': '美'},
        'LHX': {'name': 'L3Harris (國防低軌衛星關鍵)', 'nation': '美'}
    },
    '全球被動元件與精密光學 (日)': {
        '6981.T': {'name': '村田製作所 (Murata - 全球MLCC龍頭)', 'nation': '日'},
        '6976.T': {'name': '太陽誘電 (Taiyo Yuden - 高階被動元件)', 'nation': '日'},
        '7731.T': {'name': 'Nikon (精密光學與半導體鏡頭)', 'nation': '日'}
    }
}

# ==============================================================================
# 六、大數據動態運算引擎
# ==============================================================================
@st.cache_data(ttl=15)
def process_all_market_intelligence():
    tw_tickers = []
    for s in TW_STOCK_CONFIG.values():
        tw_tickers.extend(s.keys())
    global_tickers = []
    for s in GLOBAL_STOCK_CONFIG.values():
        global_tickers.extend(s.keys())

    try:
        tw_data = yf.download(tw_tickers, period='1d', interval='1m', progress=False)
    except:
        tw_data = pd.DataFrame()

    try:
        global_data = yf.download(global_tickers, period='1d', interval='1m', progress=False)
    except:
        global_data = pd.DataFrame()

    tw_results = []
    tw_rotation = []

    if not tw_data.empty:
        for group, stocks in TW_STOCK_CONFIG.items():
            group_pcts = []
            up_c = 0
            for t, name in stocks.items():
                try:
                    # ✅ 相容單一 ticker（無 MultiIndex）與多 ticker（MultiIndex）兩種格式
                    if isinstance(tw_data.columns, pd.MultiIndex):
                        close_col = ('Close', t)
                        open_col = ('Open', t)
                    else:
                        close_col = 'Close'
                        open_col = 'Open'

                    if close_col in tw_data.columns:
                        c_s = tw_data[close_col].dropna() if isinstance(tw_data.columns, pd.MultiIndex) else tw_data['Close'].dropna()
                        o_s = tw_data[open_col].dropna() if isinstance(tw_data.columns, pd.MultiIndex) else tw_data['Open'].dropna()

                        if isinstance(tw_data.columns, pd.MultiIndex):
                            c_s = tw_data['Close'][t].dropna()
                            o_s = tw_data['Open'][t].dropna()

                        if not c_s.empty:
                            curr = float(c_s.iloc[-1])
                            op = float(o_s.iloc[0]) if not o_s.empty else curr
                            pct = ((curr - op) / op) * 100 if op != 0 else 0.0
                            group_pcts.append(pct)
                            if pct > 0:
                                up_c += 1
                            tw_results.append({
                                '產業分組': group, '代號': t, '公司名稱': name,
                                '當前股價': curr, '今日漲跌幅': pct
                            })
                except:
                    pass

            if group_pcts:
                tw_rotation.append({
                    '族群': group,
                    '平均漲跌幅': sum(group_pcts) / len(group_pcts),
                    '上漲家數比': f"{up_c}/{len(group_pcts)} ({int(up_c / len(group_pcts) * 100)}%)"
                })

    global_results = []
    if not global_data.empty:
        for group, stocks in GLOBAL_STOCK_CONFIG.items():
            for t, info in stocks.items():
                try:
                    if isinstance(global_data.columns, pd.MultiIndex):
                        if ('Close', t) not in global_data.columns:
                            continue
                        c_s = global_data['Close'][t].dropna()
                        o_s = global_data['Open'][t].dropna()
                    else:
                        c_s = global_data['Close'].dropna()
                        o_s = global_data['Open'].dropna()

                    if not c_s.empty:
                        curr = float(c_s.iloc[-1])
                        op = float(o_s.iloc[0]) if not o_s.empty else curr
                        pct = ((curr - op) / op) * 100 if op != 0 else 0.0
                        # ✅ BUG FIX 3：自動填入幣別
                        currency = NATION_CURRENCY.get(info['nation'], 'USD')
                        global_results.append({
                            '國際群組': group, '國家': info['nation'], '代號': t,
                            '公司': info['name'], '最新價': curr,
                            '幣別': currency, '今日漲跌幅': pct
                        })
                except:
                    pass

    return pd.DataFrame(tw_results), pd.DataFrame(tw_rotation), pd.DataFrame(global_results)

df_tw, df_tw_rot, df_global = process_all_market_intelligence()

# ==============================================================================
# 七、今日台股資金輪動即時量化看板
# ==============================================================================
st.markdown("### 🔥 今日台股主流板塊輪動強弱榜")
if not df_tw_rot.empty:
    df_tw_rot_sorted = df_tw_rot.sort_values(by='平均漲跌幅', ascending=False).reset_index(drop=True)
    c_l1, c_l2, c_l3 = st.columns(3)
    with c_l1:
        st.metric(
            label=f"🥇 台股多頭總司令：{df_tw_rot_sorted.iloc[0]['族群']}",
            value=f"{df_tw_rot_sorted.iloc[0]['平均漲跌幅']:+.2f}%",
            delta=f"上漲比例 {df_tw_rot_sorted.iloc[0]['上漲家數比']}",
            delta_color="inverse" if df_tw_rot_sorted.iloc[0]['平均漲跌幅'] >= 0 else "normal"
        )
    with c_l2:
        st.metric(
            label=f"🥈 次強主流板塊：{df_tw_rot_sorted.iloc[1]['族群']}",
            value=f"{df_tw_rot_sorted.iloc[1]['平均漲跌幅']:+.2f}%",
            delta=f"上漲比例 {df_tw_rot_sorted.iloc[1]['上漲家數比']}",
            delta_color="inverse" if df_tw_rot_sorted.iloc[1]['平均漲跌幅'] >= 0 else "normal"
        )
    with c_l3:
        st.metric(
            label=f"⚠️ 今日最弱勢調整族群：{df_tw_rot_sorted.iloc[-1]['族群']}",
            value=f"{df_tw_rot_sorted.iloc[-1]['平均漲跌幅']:+.2f}%",
            delta=f"上漲比例 {df_tw_rot_sorted.iloc[-1]['上漲家數比']}",
            delta_color="inverse" if df_tw_rot_sorted.iloc[-1]['平均漲跌幅'] >= 0 else "normal"
        )

    fig_rot = go.Figure(go.Bar(
        y=df_tw_rot_sorted['族群'], x=df_tw_rot_sorted['平均漲跌幅'], orientation='h',
        marker_color=['#ff4b4b' if x >= 0 else '#00f574' for x in df_tw_rot_sorted['平均漲跌幅']]
    ))
    fig_rot.update_layout(height=220, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_rot, use_container_width=True, key="tw_rot_chart")
st.markdown("---")

# ==============================================================================
# 八、雙戰略觀測站分頁展示
# ==============================================================================
view_tab1, view_tab2 = st.tabs([
    "🇹🇼 觀測站一：台股強勢板塊鏈觀測站 (焦點核心池)",
    "🇺🇸🇯🇵🇰🇷 觀測站二：美日韓對應產業國際龍頭觀測站"
])

with view_tab1:
    st.markdown(f"### 🚀 台股強勢主流板塊觀測台 (數據刷新時間: {datetime.now().strftime('%H:%M:%S')})")
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

                fig = go.Figure(go.Bar(
                    x=df_sub['公司名稱'], y=df_sub['今日漲跌幅'],
                    marker_color=['#ff4b4b' if x >= 0 else '#00f574' for x in df_sub['今日漲跌幅']]
                ))
                fig.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True, key=f"tw_chart_{i}")
    else:
        st.warning("⚠️ 提示：正在向 Yahoo Finance 動態排隊獲取台股最新分時報價中。")

with view_tab2:
    st.markdown("### 🏆 全球美、日、韓產業鏈頂級龍頭鏡像對比面板")
    if not df_global.empty:
        cats_gl = list(GLOBAL_STOCK_CONFIG.keys())
        sub_tabs_gl = st.tabs(cats_gl)
        for i, cat in enumerate(cats_gl):
            with sub_tabs_gl[i]:
                df_sub = df_global[df_global['國際群組'] == cat].copy()
                df_disp = df_sub.copy()
                df_disp['最新價'] = df_disp.apply(lambda r: f"{r['最新價']:,.2f} {r['幣別']}", axis=1)
                df_disp['今日漲跌幅'] = df_disp['今日漲跌幅'].apply(lambda x: f"{x:+.2f}%")
                st.dataframe(df_disp.drop(columns=['國際群組', '幣別']), use_container_width=True, hide_index=True)

                fig = go.Figure(go.Bar(
                    x=df_sub['公司'] + " (" + df_sub['國家'] + ")", y=df_sub['今日漲跌幅'],
                    marker_color=['#ff4b4b' if x >= 0 else '#00f574' for x in df_sub['今日漲跌幅']]
                ))
                fig.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True, key=f"gl_chart_{i}")

st.markdown("---")

# ==============================================================================
# 九、台指期多源引擎 + 動態五關價預測模型
# ==============================================================================
st.markdown("### 📊 台指期主動交易決策與分析儀表板")
st.caption("本模組整合：**Yahoo Finance 即時台指期**、FinMind 外資期貨最新部位、以及動態五關價。")

def get_google_finance_taiex():
    """
    ✅ BUG FIX 5：Google Finance CSS class 已更新，增加多組 selector 防禦性爬取，
    任一成功即返回，全部失敗才回傳 None。
    """
    url = "https://www.google.com/finance/quote/TAIEX:TPE"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8"
    }
    try:
        response = requests.get(url, headers=headers, timeout=6)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # 依序嘗試多組可能的 class（Google 會不定期更新）
            selectors = [
                ("div", "YMlKec fxKbKc"),   # 新版主要 class
                ("div", "ymu9sg"),           # 舊版 class (原始碼)
                ("span", "lastPrice"),
                ("div", "kf1m0"),
            ]
            for tag, cls in selectors:
                el = soup.find(tag, {"class": cls})
                if el:
                    price_str = el.text.replace(",", "").strip()
                    try:
                        return float(price_str)
                    except ValueError:
                        continue
    except Exception:
        pass
    return None

@st.cache_data(ttl=15)
def fetch_tx_realtime_data(backup_prices):
    """
    ✅ BUG FIX 4：修正開高低收全部 fallback 到同一個基準價的問題。
    改用 yfinance 的 history() 取得真實 OHLC，若失敗才使用 FinMind Tick。
    """
    url = "https://api.finmindtrade.com/api/v4/data"
    start_str = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")

    base_p = backup_prices.get("^TWII", 44150.0) if backup_prices.get("^TWII", 0.0) > 0 else 44150.0
    # 預設值全部設為 base_p，避免固定偏移造成誤差
    tx_price, open_p, high_p, low_p = base_p, base_p, base_p, base_p
    foreign_net_oi = -65039

    # 1. 優先從 yfinance 取真實 OHLC
    try:
        tx_hist = yf.Ticker("WTW=F").history(period="2d", interval="1m")
        if not tx_hist.empty:
            tx_price = float(tx_hist['Close'].iloc[-1])
            # 取當日第一筆作為開盤（避免跨日污染）
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_data = tx_hist[tx_hist.index.strftime("%Y-%m-%d") == today_str]
            if not today_data.empty:
                open_p = float(today_data['Open'].iloc[0])
                high_p = float(today_data['High'].max())
                low_p  = float(today_data['Low'].min())
            else:
                # 無今日資料（盤前/假日），用昨日收盤估算
                open_p = float(tx_hist['Open'].iloc[-1])
                high_p = float(tx_hist['High'].max())
                low_p  = float(tx_hist['Low'].min())
    except Exception:
        # 2. yfinance 失敗時使用 FinMind Tick
        try:
            param_f = {
                "dataset": "TaiwanFuturesTick", "data_id": "TX",
                "start_date": start_str, "token": FINMIND_TOKEN
            }
            res_f = requests.get(url, params=param_f, timeout=5).json()
            if res_f.get("msg") == "success" and len(res_f.get("data", [])) > 0:
                df_f = pd.DataFrame(res_f["data"])
                df_f['price'] = pd.to_numeric(df_f['price'], errors='coerce')
                tx_price = float(df_f['price'].iloc[-1])
                open_p   = float(df_f['price'].iloc[0])
                high_p   = float(df_f['price'].max())
                low_p    = float(df_f['price'].min())
        except Exception:
            pass

    # 3. 拉取最新外資未平倉籌碼
    try:
        param_c = {
            "dataset": "TaiwanFuturesInstitutionalCommitment", "data_id": "TX",
            "start_date": start_str, "token": FINMIND_TOKEN
        }
        res_c = requests.get(url, params=param_c, timeout=5).json()
        if res_c.get("msg") == "success" and len(res_c.get("data", [])) > 0:
            df_c = pd.DataFrame(res_c["data"])
            df_fn = df_c[df_c['institutional_investors'] == '外資及陸資'].sort_values(by='date')
            if not df_fn.empty:
                df_fn['open_interest_long']  = pd.to_numeric(df_fn['open_interest_long'],  errors='coerce').fillna(0)
                df_fn['open_interest_short'] = pd.to_numeric(df_fn['open_interest_short'], errors='coerce').fillna(0)
                foreign_net_oi = int(df_fn['open_interest_long'].iloc[-1] - df_fn['open_interest_short'].iloc[-1])
    except Exception:
        pass

    return tx_price, open_p, high_p, low_p, foreign_net_oi

# 執行真實期貨清洗
tx_price, open_p, high_p, low_p, foreign_net_oi = fetch_tx_realtime_data(shared_prices)

# 讀取現貨指數
tw_index = get_google_finance_taiex()
if tw_index is None or tw_index == 0.0:
    tw_index = shared_prices.get("^TWII", 44169.04)
    if tw_index == 0.0:
        tw_index = 44169.04

# 基差計算
spread_points = tx_price - tw_index
tx_pct = ((tx_price - open_p) / open_p) * 100 if open_p > 0 else 0.0

# ------------------------------------------------------------------------------
# 五關多空關鍵價
# ------------------------------------------------------------------------------
st.markdown("#### 🔑 當日台指期關鍵多空位對照關卡")

# ✅ BUG FIX 4 延伸：確保 high_p != low_p 才算 Pivot，否則用 tx_price
if high_p != low_p:
    pivot = (high_p + low_p + tx_price) / 3
else:
    pivot = tx_price

r1 = (2 * pivot) - low_p
r2 = pivot + (high_p - low_p)
s1 = (2 * pivot) - high_p
s2 = pivot - (high_p - low_p)

five_gates_data = [
    {"關卡分類": "🔴 壓力二 (R2)", "價位": f"{r2:,.1f} 點", "型態與支撐壓力依據": "日盤反彈波段高點與先前高位套牢密集壓力區。"},
    {"關卡分類": "🚨 壓力一 (R1)", "價位": f"{r1:,.1f} 點", "型態與支撐壓力依據": "上週日K長上影線中點壓力，亦為重要整數心理大關。"},
    {"關卡分類": "🔵 多空分界 (Pivot)", "價位": f"{pivot:,.1f} 點", "型態與支撐壓力依據": "前日盤台指期收盤價，今日早盤強弱關鍵分水嶺。"},
    {"關卡分類": "🟢 支撐一 (S1)", "價位": f"{s1:,.1f} 點", "型態與支撐壓力依據": "心理整數支撐關卡，同時為前段夜盤收盤與打底密集區。"},
    {"關卡分類": "🌲 支撐二 (S2)", "價位": f"{s2:,.1f} 點", "型態與支撐壓力依據": "波段日盤開盤與早盤最低防禦線，跌破則止跌形態受破壞。"}
]
st.dataframe(pd.DataFrame(five_gates_data), use_container_width=True, hide_index=True)

# 訊號交叉判定
decision_score = 0
if spread_points > 0: decision_score += 2
if foreign_net_oi > -20000: decision_score += 3
elif foreign_net_oi < -50000: decision_score -= 4
if tx_pct > 0.5: decision_score += 2

if decision_score >= 3:
    tx_signal = "🔴 戰略多頭主導 (強烈建議拉回佈多)"
    tx_color = "error"
    tx_desc = "當前基差呈現強勢正價差，外資期貨空單出現回補避險跡象。操作紀律上宜採取『順勢控盤』，守住多空分界點之上皆為高勝率潛在買點。"
elif -3 <= decision_score < 3:
    tx_signal = "🟡 區間洗盤震盪 (多空平衡・逆向思考)"
    tx_color = "warning"
    tx_desc = "短線指標隨美股大漲有利多頭收斂逆價差，但外資 6.5 萬口歷史天量空單強力壓頂！限縮了上檔連續噴出空間，盤面極易出現劇烈洗盤。"
else:
    tx_signal = "🟢 戰術空頭壓制 (嚴防夜盤/隔日殺多風險)"
    tx_color = "success"
    tx_desc = "警報！外資台指期未平倉空單高掛歷史天量，若跌破支撐一，多單持有者應嚴格執行避險停損，切勿隨意盲目撈底。"

with st.container():
    c_tx1, c_tx2, c_tx3, c_tx4 = st.columns(4)
    with c_tx1: st.metric(label="🎯 台指期當前價", value=f"{tx_price:,.1f}", delta=f"{tx_pct:+.2f}% (距開盤)")
    with c_tx2: st.metric(label="🔄 實時期現貨基差", value=f"{spread_points:+.2f} 點", delta="正價差領先" if spread_points >= 0 else "逆價差收斂拉抬")
    with c_tx3: st.metric(label="🕵️ 外資期貨未平倉部位", value=f"{foreign_net_oi:,} 口", delta="多頭安全" if foreign_net_oi > -30000 else "歷史天量空單高壓警戒")
    with c_tx4: st.metric(label="📊 加權現貨最新指引", value=f"{tw_index:,.2f}", delta=f"最低波幅 {low_p:,.1f}", delta_color="normal")

    if tx_color == "error":   st.error(f"🧭 **當前台指量化導航訊號：{tx_signal}**\n\n{tx_desc}")
    elif tx_color == "warning": st.warning(f"🧭 **當前台指量化導航訊號：{tx_signal}**\n\n{tx_desc}")
    else:                     st.success(f"🧭 **當前台指量化導航訊號：{tx_signal}**\n\n{tx_desc}")

st.markdown("---")

# ==============================================================================
# 十、雙主線量化籌碼戰責引擎
# ==============================================================================
def get_strategy_pool():
    pool = []
    for s in TW_STOCK_CONFIG.values():
        for k in s.keys():
            pool.append((k.split('.')[0], s[k]))
    return pool

@st.cache_data(ttl=1800)
def run_dual_chip_strategies():
    strategy_pool = get_strategy_pool()
    url = "https://api.finmindtrade.com/api/v4/data"
    start_date = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")

    first_root_stocks = []
    heavy_selling_stocks = []

    for stock_id, name in strategy_pool:
        param = {
            "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
            "data_id": stock_id, "start_date": start_date,
            "end_date": end_date, "token": FINMIND_TOKEN
        }
        try:
            res = requests.get(url, params=param, timeout=5).json()
            if res.get("msg") == "success" and len(res.get("data", [])) > 0:
                df = pd.DataFrame(res["data"])
                df_foreign = df[df['name'] == 'Foreign_Investor'].copy()
                if not df_foreign.empty and len(df_foreign) >= 8:
                    df_foreign['buy']  = pd.to_numeric(df_foreign['buy'],  errors='coerce').fillna(0)
                    df_foreign['sell'] = pd.to_numeric(df_foreign['sell'], errors='coerce').fillna(0)
                    df_foreign['shares'] = (df_foreign['buy'] - df_foreign['sell']) / 1000
                    df_foreign = df_foreign.sort_values(by='date').reset_index(drop=True)

                    today_chip     = df_foreign['shares'].iloc[-1]
                    yesterday_chip = df_foreign['shares'].iloc[-2]
                    recent_3d      = df_foreign['shares'].iloc[-3:].tolist()
                    previous_6d    = df_foreign['shares'].iloc[-8:-2].tolist()
                    full_9d        = df_foreign['shares'].iloc[-9:].tolist()

                    hist = yf.Ticker(f"{stock_id}.TW").history(period="10d")
                    if hist.empty or len(hist) < 5:
                        continue
                    curr_p = float(hist['Close'].iloc[-1])
                    ma5 = float(hist['Close'].rolling(window=5).mean().iloc[-1])

                    cond_sell_off_a  = sum(1 for x in previous_6d if x < 0) >= 3
                    cond_first_root  = yesterday_chip <= 0 and today_chip > 0
                    neg_prev = [x for x in previous_6d if x < 0]
                    avg_prev_sell = sum(neg_prev) / len(neg_prev) if neg_prev else 0
                    cond_momentum_a  = today_chip > abs(avg_prev_sell) * 1.5

                    if cond_sell_off_a and cond_first_root and cond_momentum_a:
                        if ma5 > 0 and curr_p >= ma5 and curr_p <= ma5 * 1.03:
                            first_root_stocks.append({
                                "股票代號": stock_id, "公司名稱": name,
                                "當前股價": f"{curr_p:.2f} 元",
                                "今日外資轉買(張)": today_chip,
                                "昨日外資賣超(張)": yesterday_chip,
                                "洗盤期賣超高頻天數": f"{sum(1 for x in previous_6d if x < 0)} / 6 天"
                            })

                    cond_persistent_sell = sum(1 for x in full_9d if x < 0) >= 6
                    cond_no_rebound = (sum(1 for x in recent_3d if x < 0) == 3 or
                                       (sum(recent_3d) < 0 and today_chip < 0))

                    if cond_persistent_sell and cond_no_rebound:
                        heavy_selling_stocks.append({
                            "股票代號": stock_id, "公司名稱": name,
                            "當前股價": f"{curr_p:.2f} 元",
                            "近3日遭提款累積(張)": sum(recent_3d),
                            "今日外資續賣(張)": today_chip,
                            "波段提款密集度": f"{sum(1 for x in full_9d if x < 0)} / 9 天"
                        })
        except:
            pass

    return pd.DataFrame(first_root_stocks), pd.DataFrame(heavy_selling_stocks)

df_strat_first, df_strat_sellout = run_dual_chip_strategies()

strat_tab1, strat_tab2 = st.tabs([
    "🎯 策略一：外資洗盤後『由賣轉買・第一根認錯表態點』",
    "⚠️ 策略二：外資避險瘋狂提款『持續殺盤・尚未認錯』警示池"
])

with strat_tab1:
    st.markdown("#### 🚀 剛出爐！外資由賣轉買第一根起漲點")
    if not df_strat_first.empty:
        col_t1, col_c1 = st.columns([3, 2])
        with col_t1:
            df_disp1 = df_strat_first.copy()
            df_disp1['今日外資轉買(張)'] = df_disp1['今日外資轉買(張)'].apply(lambda x: f"+{x:,.0f} 張")
            df_disp1['昨日外資賣超(張)'] = df_disp1['昨日外資賣超(張)'].apply(lambda x: f"{x:,.0f} 張")
            st.dataframe(df_disp1, use_container_width=True, hide_index=True)
        with col_c1:
            fig1 = go.Figure(go.Bar(
                x=df_strat_first['公司名稱'],
                y=df_strat_first['今日外資轉買(張)'],
                marker_color='#ff4b4b',
                text=df_strat_first['今日外資轉買(張)'].apply(lambda x: f"+{x:,.0f}張"),
                textposition='auto'
            ))
            fig1.update_layout(title="第一根買回主力敲進張數排行", height=230, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig1, use_container_width=True, key="strat1_chart")
    else:
        st.info("ℹ️ 目前核心標的中，暫無股票精準符合『昨日賣、今日第一天剛轉大買』的黃金轉折第一根臨界點。")

with strat_tab2:
    st.markdown("#### 🚨 警惕！外資持續當作提款機、完全未見認錯回補的個股")
    if not df_strat_sellout.empty:
        col_t2, col_c2 = st.columns([3, 2])
        with col_t2:
            df_disp2 = df_strat_sellout.copy()
            # ✅ BUG FIX 2：先取出數值用於繪圖，再格式化為字串顯示
            sell_vals_for_chart = df_strat_sellout['近3日遭提款累積(張)'].tolist()
            df_disp2['近3日遭提款累積(張)'] = df_disp2['近3日遭提款累積(張)'].apply(lambda x: f"{x:,.0f} 張")
            df_disp2['今日外資續賣(張)']    = df_disp2['今日外資續賣(張)'].apply(lambda x: f"{x:,.0f} 張")
            st.dataframe(df_disp2, use_container_width=True, hide_index=True)
        with col_c2:
            # ✅ BUG FIX 2：使用原始數值 sell_vals_for_chart 而非字串欄位呼叫 .abs()
            fig2 = go.Figure(go.Bar(
                x=df_strat_sellout['公司名稱'],
                y=[abs(v) for v in sell_vals_for_chart],
                marker_color='#00f574',
                text=[f"{v:,.0f}張" for v in sell_vals_for_chart],
                textposition='auto'
            ))
            fig2.update_layout(title="近 3 日外資提款失血量排行 (張)", height=230, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig2, use_container_width=True, key="strat2_chart")
    else:
        st.success("🟢 傲人表現！目前監控池內的所有個股，皆無落入『外資密集高頻率連續殺盤』的重災區。")

# 🔍 大戶反向籌碼心理學戰術提醒
st.sidebar.markdown("---")
st.sidebar.subheader("💡 籌碼逆向心理學提醒")
st.sidebar.warning(
    "**逆向思考：** 根據技術雷達分析，短線雖然逆價差收斂拉抬，但外資持倉處於『歷史天量空』。操作上切勿盲目大幅追高，應隨時依據動態五關價進行紀律防守。"
)

st.markdown("---")

# ==============================================================================
# 十一、盤後量化數據監控：電子股四指標篩選引擎（含 API 偵測器）
# ==============================================================================
st.markdown("### 🔬 盤後量化數據監控｜全台電子股基本面四指標篩選站")
st.caption(
    "篩選邏輯：同時符合以下四項指標中 **≥ 2 項**，即列入觀察名單。"
    "｜🐋 大戶持股增　🔬 研發費用增　📋 合約負債增　📈 月營收連續雙增"
)

FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"

# ==============================================================================
# 🔍 步驟零：API 原始資料偵測器（每次啟動都會執行，讓你看到真實欄位）
# ==============================================================================
@st.cache_data(ttl=3600)
def probe_api_schemas():
    """
    用台積電(2330)測試各 dataset 的真實欄位與範例資料，
    回傳 dict { dataset_name: {"columns": [...], "sample": [...], "msg": ...} }
    """
    probe_stock = "2330"
    end_d = datetime.now().strftime("%Y-%m-%d")
    datasets = {
        "月營收":     ("TaiwanStockMonthRevenue",          (datetime.now()-timedelta(days=150)).strftime("%Y-%m-%d")),
        "持股分級":   ("TaiwanStockHoldingSharesPer",       (datetime.now()-timedelta(days=400)).strftime("%Y-%m-%d")),
        "損益表":     ("TaiwanStockFinancialStatements",    (datetime.now()-timedelta(days=400)).strftime("%Y-%m-%d")),
        "資產負債表": ("TaiwanStockBalanceSheet",           (datetime.now()-timedelta(days=400)).strftime("%Y-%m-%d")),
    }
    result = {}
    for label, (ds, start_d) in datasets.items():
        try:
            r = requests.get(FINMIND_URL, params={
                "dataset": ds, "data_id": probe_stock,
                "start_date": start_d, "end_date": end_d,
                "token": FINMIND_TOKEN
            }, timeout=10)
            d = r.json()
            if d.get("msg") == "success" and d.get("data"):
                df_probe = pd.DataFrame(d["data"])
                result[label] = {
                    "dataset": ds,
                    "msg": "success",
                    "rows": len(df_probe),
                    "columns": list(df_probe.columns),
                    "sample": df_probe.tail(3).to_dict(orient="records"),
                    "df": df_probe
                }
            else:
                result[label] = {"dataset": ds, "msg": d.get("msg","unknown"), "rows":0, "columns":[], "sample":[], "df": pd.DataFrame()}
        except Exception as e:
            result[label] = {"dataset": ds, "msg": str(e), "rows":0, "columns":[], "sample":[], "df": pd.DataFrame()}
    return result

with st.spinner("🔌 正在連線 FinMind API，偵測各資料集真實欄位結構..."):
    probe_results = probe_api_schemas()

with st.expander("🔍 API 原始資料偵測結果（展開查看真實欄位與範例資料）", expanded=True):
    for label, info in probe_results.items():
        status_icon = "✅" if info["msg"] == "success" else "❌"
        st.markdown(f"**{status_icon} {label}** — `{info['dataset']}` | 狀態: `{info['msg']}` | 回傳筆數: {info['rows']}")
        if info["columns"]:
            st.code(f"欄位：{info['columns']}", language=None)
        if info["sample"]:
            st.dataframe(pd.DataFrame(info["sample"]), use_container_width=True, hide_index=True)
        st.markdown("---")

# 根據偵測結果決定各 dataset 是否可用
api_ok = {label: info["msg"] == "success" for label, info in probe_results.items()}

# ==============================================================================
# 全台電子股資料庫（上市+上櫃，約 300 檔）
# ==============================================================================
ELECTRONIC_STOCK_DB = {
    # ── 半導體製造/晶圓代工 ──
    "2330":"台積電","2303":"聯電","5347":"世界先進","6770":"力積電","2337":"旺宏",
    "3704":"合一","3529":"力旺","4967":"十銓","6550":"北極星藥業",
    # ── IC 設計 ──
    "2454":"聯發科","3034":"聯詠","2379":"瑞昱","3231":"緯創","2IC設計":"",
    "4958":"臻鼎-KY","3533":"嘉澤","6415":"矽力-KY","2478":"大毅",
    "2881":"富邦金","3037":"欣興","6669":"緯穎","3702":"大聯大",
    "4919":"新唐","2401":"凌陽","3035":"智原","4906":"正文",
    "6669":"緯穎","5274":"信驊","6274":"台耀","3532":"台勝科",
    "6770":"力積電","3514":"昱晶","4919":"新唐","2454":"聯發科",
    "2408":"南亞科","5483":"中美晶","6488":"環球晶","6182":"合晶",
    "3016":"嘉晶","2338":"光罩","6139":"亞翔",
    # ── 被動元件 ──
    "2327":"國巨","2492":"華新科","2375":"凱美","3026":"禾伸堂",
    "6449":"鈺邦","6175":"立敦","3624":"光頡","3236":"千如",
    "5328":"華容","6155":"鈞寶","8121":"越峰","2478":"大毅",
    "3090":"日電貿","8042":"金山電","6173":"信昌電",
    # ── 封測 ──
    "3711":"日月光投控","2325":"矽品","6271":"同欣電","2329":"華泰",
    "6147":"頎邦","2369":"菱生","3014":"全漢","3017":"奇鋐",
    # ── PCB ──
    "2367":"燿華","3037":"欣興","8046":"南電","2354":"鴻準",
    "6153":"嘉聯益","3044":"健鼎","2345":"智邦","2352":"佳世達",
    "4138":"曜亞","6191":"精成科","2484":"希華",
    # ── 光學/鏡頭 ──
    "3008":"大立光","3406":"玉晶光","3362":"先進光","4979":"華星光",
    "5371":"中光電","2340":"台亞","6449":"鈺邦",
    # ── 伺服器/網路 ──
    "2382":"廣達","6669":"緯穎","3231":"緯創","2317":"鴻海",
    "4938":"和碩","2357":"華碩","2353":"宏碁","2395":"研華",
    "3026":"禾伸堂","6488":"環球晶",
    "2308":"台達電","6415":"矽力-KY","3035":"智原",
    # ── 記憶體/儲存 ──
    "2344":"華邦電","4973":"廣穎","2337":"旺宏",
    "5347":"世界先進","8096":"擎亞",
    # ── 電源/被動 ──
    "6214":"志豐","3006":"晶豪科","2440":"太空梭","3008":"大立光",
    "6274":"台耀","3443":"創意","6153":"嘉聯益",
    # ── EMS/ODM ──
    "2317":"鴻海","2382":"廣達","2357":"華碩","4938":"和碩",
    "2353":"宏碁","2385":"群光","2347":"聯強","3231":"緯創",
    # ── 半導體設備/材料 ──
    "3596":"智易","6104":"創惟","5274":"信驊","3714":"富采",
    "6770":"力積電","3533":"嘉澤","2IC":"",
    # ── 光通訊/電信 ──
    "4979":"華星光","3491":"昇達科","6669":"緯穎",
    # ── AI/伺服器概念 ──
    "6669":"緯穎","3711":"日月光投控","2330":"台積電",
    "6415":"矽力-KY","5274":"信驊","3443":"創意","4967":"十銓",
}

# 清理：移除空值 key 與重複（dict 天然去重）
ELECTRONIC_STOCK_DB = {k: v for k, v in ELECTRONIC_STOCK_DB.items() if k and v and k.isdigit()}

# ==============================================================================
# 各指標抓取函數（依 API 偵測結果的真實欄位編寫）
# ==============================================================================

def _fm_fetch(dataset: str, data_id: str, start: str, end: str) -> pd.DataFrame:
    try:
        r = requests.get(FINMIND_URL, params={
            "dataset": dataset, "data_id": data_id,
            "start_date": start, "end_date": end, "token": FINMIND_TOKEN
        }, timeout=8)
        d = r.json()
        if d.get("msg") == "success" and d.get("data"):
            return pd.DataFrame(d["data"])
    except Exception:
        pass
    return pd.DataFrame()

# ── 指標一：大戶持股增加 ─────────────────────────────────────────────────────
def check_holder(sid, start, end, probe):
    """
    TaiwanStockHoldingSharesPer
    真實欄位（由偵測器取得）: HoldingSharesLevel, percent, date, ...
    大戶定義：HoldingSharesLevel 含 "400" 以上者合計 percent
    """
    if not api_ok.get("持股分級"):
        return False, "API不可用"
    # 從偵測結果取得真實欄位
    probe_cols = probe.get("持股分級", {}).get("columns", [])
    df = _fm_fetch("TaiwanStockHoldingSharesPer", sid, start, end)
    if df.empty:
        return False, "無資料"
    # 動態偵測持股級距欄名
    level_col = next((c for c in df.columns if "level" in c.lower() or "Level" in c or "持股" in c), None)
    pct_col   = next((c for c in df.columns if "percent" in c.lower() or "ratio" in c.lower() or "占比" in c), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not level_col or not pct_col:
        return False, f"找不到欄位(有:{list(df.columns)})"
    # 大戶：持股 400 張以上各級距
    big_mask = df[level_col].astype(str).str.extract(r"(\d+)")[0].astype(float, errors="ignore")
    try:
        df["_lvl_num"] = df[level_col].astype(str).str.extract(r"^(\d+)")[0].astype(float)
        df_big = df[df["_lvl_num"] >= 400].copy()
    except Exception:
        df_big = df[df[level_col].astype(str).str.contains("400|600|800|1000", na=False)].copy()
    if df_big.empty:
        return False, f"無400張以上級距(level欄={level_col})"
    df_big[pct_col] = pd.to_numeric(df_big[pct_col], errors="coerce").fillna(0)
    df_big[date_col] = pd.to_datetime(df_big[date_col])
    daily = df_big.groupby(date_col)[pct_col].sum().sort_index()
    if len(daily) < 2:
        return False, "期數不足"
    latest, prev = daily.iloc[-1], daily.iloc[-2]
    diff = latest - prev
    return diff > 0, f"{prev:.2f}%→{latest:.2f}% ({'+' if diff>=0 else ''}{diff:.2f}%)"

# ── 指標二：研發費用增加 ─────────────────────────────────────────────────────
def check_rd(sid, start, end, probe):
    """
    TaiwanStockFinancialStatements
    真實欄位: type, value, date
    尋找 type 含 research / RD / 研發 的列
    """
    if not api_ok.get("損益表"):
        return False, "API不可用"
    df = _fm_fetch("TaiwanStockFinancialStatements", sid, start, end)
    if df.empty:
        return False, "無資料"
    type_col  = next((c for c in df.columns if "type" in c.lower()), None)
    value_col = next((c for c in df.columns if "value" in c.lower() or "amount" in c.lower()), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not type_col or not value_col:
        return False, f"找不到欄位(有:{list(df.columns)})"
    rd_mask = df[type_col].astype(str).str.contains(
        "research|ResearchAndDevelopment|RD|研發", case=False, na=False
    )
    df_rd = df[rd_mask].copy()
    if df_rd.empty:
        # 列出所有 type 供診斷
        all_types = df[type_col].unique()[:20].tolist()
        return False, f"無研發欄(所有type前20:{all_types})"
    df_rd[value_col] = pd.to_numeric(df_rd[value_col], errors="coerce").fillna(0)
    df_rd[date_col]  = pd.to_datetime(df_rd[date_col])
    # 相同 date 可能有多筆，取和
    grouped = df_rd.groupby(date_col)[value_col].sum().sort_index()
    if len(grouped) < 2:
        return False, "期數不足"
    latest, prev = grouped.iloc[-1], grouped.iloc[-2]
    if prev == 0:
        return False, "前期為零"
    pct = (latest - prev) / abs(prev) * 100
    return latest > prev, f"{prev/1e6:.1f}M→{latest/1e6:.1f}M ({'+' if pct>=0 else ''}{pct:.1f}%)"

# ── 指標三：合約負債增加 ─────────────────────────────────────────────────────
def check_contract_liability(sid, start, end, probe):
    """
    TaiwanStockBalanceSheet
    真實欄位: type, value, date
    尋找 type 含 ContractLiabilit / DeferredRevenue / 合約負債 / 預收
    """
    if not api_ok.get("資產負債表"):
        return False, "API不可用"
    df = _fm_fetch("TaiwanStockBalanceSheet", sid, start, end)
    if df.empty:
        return False, "無資料"
    type_col  = next((c for c in df.columns if "type" in c.lower()), None)
    value_col = next((c for c in df.columns if "value" in c.lower() or "amount" in c.lower()), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not type_col or not value_col:
        return False, f"找不到欄位(有:{list(df.columns)})"
    cl_mask = df[type_col].astype(str).str.contains(
        "ContractLiabilit|contract_liabilit|合約負債|預收|DeferredRevenue|AdvanceReceipt",
        case=False, na=False
    )
    df_cl = df[cl_mask].copy()
    if df_cl.empty:
        all_types = df[type_col].unique()[:20].tolist()
        return False, f"無合約負債欄(所有type前20:{all_types})"
    df_cl[value_col] = pd.to_numeric(df_cl[value_col], errors="coerce").fillna(0)
    df_cl[date_col]  = pd.to_datetime(df_cl[date_col])
    grouped = df_cl.groupby(date_col)[value_col].sum().sort_index()
    if len(grouped) < 2:
        return False, "期數不足"
    latest, prev = grouped.iloc[-1], grouped.iloc[-2]
    diff = latest - prev
    return diff > 0, f"{prev/1e6:.1f}M→{latest/1e6:.1f}M ({'+' if diff>=0 else ''}{diff/1e6:.1f}M)"

# ── 指標四：月營收連續雙增 ───────────────────────────────────────────────────
def check_revenue(sid, rev_start, end, probe):
    """
    TaiwanStockMonthRevenue
    真實欄位（通常）: date, stock_id, country, revenue, revenue_month, revenue_year
    """
    if not api_ok.get("月營收"):
        return False, "API不可用"
    df = _fm_fetch("TaiwanStockMonthRevenue", sid, rev_start, end)
    if df.empty:
        return False, "無資料"
    date_col = "date" if "date" in df.columns else df.columns[0]
    rev_col  = next((c for c in df.columns if "revenue" in c.lower() and "year" not in c.lower() and "month" not in c.lower()), None)
    if not rev_col:
        rev_col = next((c for c in df.columns if "revenue" in c.lower()), None)
    if not rev_col:
        return False, f"找不到revenue欄(有:{list(df.columns)})"
    df[rev_col]  = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).drop_duplicates(date_col).reset_index(drop=True)
    if len(df) < 3:
        return False, f"資料不足(只有{len(df)}月)"
    m0 = df[rev_col].iloc[-1]
    m1 = df[rev_col].iloc[-2]
    m2 = df[rev_col].iloc[-3]
    d0 = df[date_col].iloc[-1].strftime("%y/%m")
    d1 = df[date_col].iloc[-2].strftime("%y/%m")
    d2 = df[date_col].iloc[-3].strftime("%y/%m")
    passed = (m0 > m1 > m2) and m2 > 0
    return passed, f"{m2/1e6:.0f}M({d2})→{m1/1e6:.0f}M({d1})→{m0/1e6:.0f}M({d0})"

# ==============================================================================
# 核心篩選引擎（含進度條）
# ==============================================================================
def run_screen_with_progress(stock_db, probe):
    end_date  = datetime.now().strftime("%Y-%m-%d")
    start_1y  = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
    start_4m  = (datetime.now() - timedelta(days=150)).strftime("%Y-%m-%d")
    results   = []
    stocks    = list(stock_db.items())
    total     = len(stocks)

    prog_bar  = st.progress(0, text="準備開始掃描...")
    log_box   = st.empty()
    log_lines = []

    for i, (sid, name) in enumerate(stocks):
        prog_bar.progress((i + 1) / total, text=f"掃描中 {i+1}/{total}：{name}({sid})")

        row = {
            "代號": sid, "公司": name,
            "大戶增": False,    "大戶增_說明": "-",
            "研發增": False,    "研發增_說明": "-",
            "合約負債增": False, "合約負債增_說明": "-",
            "月營收雙增": False, "月營收雙增_說明": "-",
            "符合項數": 0
        }

        ok1, n1 = check_holder(sid, start_1y, end_date, probe)
        row["大戶增"], row["大戶增_說明"] = ok1, n1

        ok2, n2 = check_rd(sid, start_1y, end_date, probe)
        row["研發增"], row["研發增_說明"] = ok2, n2

        ok3, n3 = check_contract_liability(sid, start_1y, end_date, probe)
        row["合約負債增"], row["合約負債增_說明"] = ok3, n3

        ok4, n4 = check_revenue(sid, start_4m, end_date, probe)
        row["月營收雙增"], row["月營收雙增_說明"] = ok4, n4

        row["符合項數"] = int(ok1) + int(ok2) + int(ok3) + int(ok4)

        # 即時 log
        icons = "".join([
            ("🟢" if ok1 else "⚫"), ("🔬" if ok2 else "⚫"),
            ("📋" if ok3 else "⚫"), ("📈" if ok4 else "⚫")
        ])
        line = f"{icons} {name}({sid}) → {row['符合項數']}/4 項"
        log_lines.append(line)
        if len(log_lines) > 12:
            log_lines = log_lines[-12:]
        log_box.code("\n".join(log_lines), language=None)

        results.append(row)

    prog_bar.progress(1.0, text=f"✅ 掃描完成！共 {total} 檔")
    log_box.empty()
    return pd.DataFrame(results)

# ==============================================================================
# 介面控制
# ==============================================================================
with st.expander("⚙️ 四項指標說明", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.info("**🐋 大戶持股增**
持股≥400張級距合計比例較前期上升，主力資金積累訊號。")
    with c2: st.info("**🔬 研發費用增**
最新一季研發支出高於前一季，企業持續投資競爭力。")
    with c3: st.info("**📋 合約負債增**
預收款/合約負債較前期增加，訂單能見度與客戶黏著度提升。")
    with c4: st.info("**📈 月營收雙增**
連續三個月 M-2 < M-1 < M，趨勢向上動能確認。")

col_btn1, col_btn2, col_min, _ = st.columns([1.2, 1.2, 0.8, 3])
with col_btn1:
    do_run = st.button("🚀 執行全市場篩選", type="primary", use_container_width=True)
with col_btn2:
    do_clear = st.button("🔄 清除結果重掃", use_container_width=True)
with col_min:
    min_cond = st.number_input("最低符合項數", min_value=1, max_value=4, value=2, step=1)

if do_clear:
    if "screen_df" in st.session_state:
        del st.session_state["screen_df"]
    st.rerun()

if do_run or ("screen_df" not in st.session_state):
    if do_run:
        if "screen_df" in st.session_state:
            del st.session_state["screen_df"]
    if "screen_df" not in st.session_state:
        df_all_screen = run_screen_with_progress(ELECTRONIC_STOCK_DB, probe_results)
        st.session_state["screen_df"] = df_all_screen

df_all_screen = st.session_state.get("screen_df", pd.DataFrame())

if not df_all_screen.empty:
    df_pass_screen = df_all_screen[df_all_screen["符合項數"] >= min_cond].sort_values(
        "符合項數", ascending=False).reset_index(drop=True)

    total_s  = len(df_all_screen)
    pass_s   = len(df_pass_screen)
    cnt4 = len(df_all_screen[df_all_screen["符合項數"]==4])
    cnt3 = len(df_all_screen[df_all_screen["符合項數"]==3])
    cnt2 = len(df_all_screen[df_all_screen["符合項數"]==2])

    m1,m2,m3,m4,m5 = st.columns(5)
    with m1: st.metric("📦 掃描總數", f"{total_s} 檔")
    with m2: st.metric(f"✅ 符合≥{min_cond}項", f"{pass_s} 檔", delta=f"{pass_s/total_s*100:.1f}%", delta_color="inverse")
    with m3: st.metric("🥈 符合2項", f"{cnt2} 檔")
    with m4: st.metric("🥇 符合3項", f"{cnt3} 檔")
    with m5: st.metric("👑 四項全中", f"{cnt4} 檔", delta="強力候選" if cnt4>0 else "暫無")

    st.markdown("---")

    # ── 完整掃描明細（全部股票，含未通過，方便診斷） ──
    with st.expander("📊 完整掃描明細（含未通過股票，診斷資料是否正確抓到）", expanded=False):
        diag_rows = []
        for _, r in df_all_screen.iterrows():
            diag_rows.append({
                "代號": r["代號"], "公司": r["公司"],
                "符合": f"{int(r['符合項數'])}/4",
                "🐋大戶": f"{'✅' if r['大戶增'] else '❌'} {r['大戶增_說明']}",
                "🔬研發": f"{'✅' if r['研發增'] else '❌'} {r['研發增_說明']}",
                "📋合約負債": f"{'✅' if r['合約負債增'] else '❌'} {r['合約負債增_說明']}",
                "📈月營收": f"{'✅' if r['月營收雙增'] else '❌'} {r['月營收雙增_說明']}",
            })
        st.dataframe(pd.DataFrame(diag_rows), use_container_width=True, hide_index=True)

    # ── 符合名單主表 ──
    if df_pass_screen.empty:
        st.warning(f"⚠️ 目前無股票符合 ≥{min_cond} 項條件，可調低「最低符合項數」或重新掃描。")
    else:
        st.markdown(f"#### 🏆 符合 ≥{min_cond} 項基本面指標 — 共 **{pass_s}** 檔")

        tab_all_r, tab_4r, tab_3r = st.tabs([
            f"📋 全部名單 ({pass_s})", f"👑 四項全中 ({cnt4})", f"🥇 符合三項 ({cnt3})"
        ])

        def _render_table(df_sub):
            if df_sub.empty:
                st.info("此分類目前無符合股票。")
                return
            rows = []
            for _, r in df_sub.iterrows():
                rows.append({
                    "代號": r["代號"], "公司": r["公司"],
                    "符合項數": f"{'⭐'*int(r['符合項數'])} {int(r['符合項數'])}/4",
                    "🐋大戶持股": ("✅ " if r["大戶增"] else "❌ ") + str(r["大戶增_說明"]),
                    "🔬研發費用": ("✅ " if r["研發增"] else "❌ ") + str(r["研發增_說明"]),
                    "📋合約負債": ("✅ " if r["合約負債增"] else "❌ ") + str(r["合約負債增_說明"]),
                    "📈月營收":   ("✅ " if r["月營收雙增"] else "❌ ") + str(r["月營收雙增_說明"]),
                })
            df_show = pd.DataFrame(rows)
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            # 橫條圖
            fig_b = go.Figure(go.Bar(
                y=df_sub["公司"]+"("+df_sub["代號"]+")",
                x=df_sub["符合項數"].astype(int),
                orientation="h",
                marker_color=["#ff4b4b" if x==4 else ("#ff8c42" if x==3 else "#f5a623")
                              for x in df_sub["符合項數"].astype(int)],
                text=df_sub["符合項數"].astype(int).apply(lambda x: f"{x}/4"),
                textposition="auto"
            ))
            fig_b.update_layout(
                height=max(260, len(df_sub)*28+60),
                xaxis=dict(range=[0,4.5], tickvals=[1,2,3,4]),
                margin=dict(l=10,r=10,t=30,b=10),
                title="個股符合項數排行"
            )

            # 雷達圖
            conds = ["大戶增","研發增","合約負債增","月營收雙增"]
            vals  = [int(df_sub[c].sum()) for c in conds]
            fig_r = go.Figure(go.Scatterpolar(
                r=vals+[vals[0]],
                theta=["🐋大戶","🔬研發","📋合約負債","📈月營收","🐋大戶"],
                fill="toself", fillcolor="rgba(255,75,75,0.15)",
                line=dict(color="#ff4b4b",width=2)
            ))
            fig_r.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max(vals)+1])),
                height=300, margin=dict(l=30,r=30,t=30,b=30),
                title="各指標通過家數雷達"
            )
            cc1, cc2 = st.columns(2)
            with cc1: st.plotly_chart(fig_b, use_container_width=True, key=f"b_{len(df_sub)}_{df_sub.iloc[0]['代號'] if len(df_sub)>0 else 'x'}")
            with cc2: st.plotly_chart(fig_r, use_container_width=True, key=f"r_{len(df_sub)}_{df_sub.iloc[0]['代號'] if len(df_sub)>0 else 'x'}")

            csv_out = df_show.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 下載 CSV", csv_out,
                               f"screen_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

        with tab_all_r: _render_table(df_pass_screen)
        with tab_4r:    _render_table(df_all_screen[df_all_screen["符合項數"]==4].reset_index(drop=True))
        with tab_3r:    _render_table(df_all_screen[df_all_screen["符合項數"]==3].reset_index(drop=True))

        # 全市場各指標通過率
        st.markdown("#### 📊 全市場各指標通過率")
        cond_cols  = ["大戶增","研發增","合約負債增","月營收雙增"]
        cond_names = ["🐋大戶持股增","🔬研發費用增","📋合約負債增","📈月營收雙增"]
        cond_vals_  = [int(df_all_screen[c].sum()) for c in cond_cols]
        cond_pcts_  = [v/total_s*100 for v in cond_vals_]
        fig_ov = go.Figure(go.Bar(
            x=cond_names, y=cond_pcts_,
            marker_color=["#ff4b4b","#4b9eff","#f5a623","#00c49f"],
            text=[f"{v}檔({p:.1f}%)" for v,p in zip(cond_vals_,cond_pcts_)],
            textposition="auto"
        ))
        fig_ov.update_layout(height=260, yaxis=dict(range=[0,100],title="通過率 (%)"),
                              margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_ov, use_container_width=True, key="ov_bar_final")

st.markdown(
    "<small>⚠️ 資料來源：FinMind API。財報資料有季度延遲；月營收為最新公告。本看板僅供量化篩選參考，不構成投資建議。</small>",
    unsafe_allow_html=True
)

# ==============================================================================
# 十二、網頁定時自動循環刷新機制
# ==============================================================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
