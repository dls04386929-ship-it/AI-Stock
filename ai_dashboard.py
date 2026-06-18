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
# 三、大盤與夜盤監控配置
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
# 四、焦點核心池板塊配置庫
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
# 五、自動串接台灣本土財經 API 函數 (盤後大戶籌碼)
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
    return pd.DataFrame(backup_buy), pd.DataFrame(backup_sell), "（無法連線，顯示歷史備援資料）"

@st.cache_data(ttl=1800)
def fetch_tw_chip_data_automated():
    """
    ✅ 重大修正（取代先前完全錯誤的設計）：

    之前的版本誤用 dataset='TaiwanStockTotalInstitutionalInvestors'，
    這個 API 回傳的是「整個大盤」三大法人(外資/投信/自營商)買賣超總和，
    它的 name 欄位是法人類別名稱（如 Foreign_Investor），
    根本不是產業族群，所以不可能產生「元宇宙、被動元件」這種族群排行——
    這是上一輪修正時的設計錯誤，數值因此完全失真或顯示備援假資料。

    正確做法：FinMind 沒有「依產業族群統計法人買賣超」的現成 API，
    必須改為「逐股呼叫個股法人買賣超 dataset (TaiwanStockInstitutionalInvestorsBuySell)，
    再依我們已定義的 TW_STOCK_CONFIG 產業分類，加總外資買賣超金額」，
    這樣才能得出真實且有意義的「族群資金流向」排行。

    回傳：依族群加總「外資買賣超(億)」排序的買超/賣超 TOP5，
    並附上實際抓取的個股級原始明細，供右側展開查驗。
    """
    url = "https://api.finmindtrade.com/api/v4/data"

    # 往前找最近一個有效交易日（跳過週末）
    valid_date = None
    for i in range(0, 6):
        d = datetime.now() - timedelta(days=i)
        if d.weekday() < 5:
            valid_date = d
            break
    if valid_date is None:
        valid_date = datetime.now()
    date_str = valid_date.strftime("%Y-%m-%d")
    start_str = (valid_date - timedelta(days=7)).strftime("%Y-%m-%d")

    group_results = []   # [{族群, 代號, 公司, 外資買賣超(億), 日期}]
    fetch_log = []       # 偵錯用：記錄每檔股票實際抓取狀況

    for group, stocks in TW_STOCK_CONFIG.items():
        for sid_full, name in stocks.items():
            sid = sid_full.split('.')[0]
            try:
                r = requests.get(url, params={
                    "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
                    "data_id": sid,
                    "start_date": start_str,
                    "end_date": date_str,
                    "token": FINMIND_TOKEN
                }, timeout=8)
                d = r.json()

                if d.get("msg") == "success" and d.get("data"):
                    df_s = pd.DataFrame(d["data"])
                    # 真實欄位通常為: date, stock_id, name(法人類別), buy, sell
                    name_col = next((c for c in df_s.columns if c.lower() == "name"), None)
                    buy_col  = next((c for c in df_s.columns if c.lower() == "buy"), None)
                    sell_col = next((c for c in df_s.columns if c.lower() == "sell"), None)
                    date_col = "date" if "date" in df_s.columns else None

                    if name_col and buy_col and sell_col and date_col:
                        df_s[buy_col]  = pd.to_numeric(df_s[buy_col], errors="coerce").fillna(0)
                        df_s[sell_col] = pd.to_numeric(df_s[sell_col], errors="coerce").fillna(0)
                        # 篩選外資（含外資及陸資）
                        df_foreign = df_s[df_s[name_col].astype(str).str.contains(
                            "Foreign_Investor|外資", case=False, na=False)].copy()
                        if not df_foreign.empty:
                            # 取最新一筆日期
                            df_foreign[date_col] = pd.to_datetime(df_foreign[date_col])
                            df_foreign = df_foreign.sort_values(date_col)
                            latest_row = df_foreign.iloc[-1]
                            net_amt_yi = (latest_row[buy_col] - latest_row[sell_col]) / 1e8
                            group_results.append({
                                "族群": group, "代號": sid, "公司": name,
                                "外資買賣超(億)": net_amt_yi,
                                "日期": latest_row[date_col].strftime("%Y-%m-%d")
                            })
                            fetch_log.append(f"✅ {name}({sid}) {latest_row[date_col].date()} 外資 {net_amt_yi:+.2f}億")
                        else:
                            fetch_log.append(f"⚠️ {name}({sid}) 無外資列(name值:{df_s[name_col].unique().tolist()})")
                    else:
                        fetch_log.append(f"❌ {name}({sid}) 欄位不符(有:{list(df_s.columns)})")
                else:
                    fetch_log.append(f"❌ {name}({sid}) API msg={d.get('msg')}")
            except Exception as e:
                fetch_log.append(f"❌ {name}({sid}) 例外:{e}")

    st.session_state["_chip_fetch_log"] = fetch_log

    if not group_results:
        return get_backup_chips_data()[0], get_backup_chips_data()[1], get_backup_chips_data()[2], fetch_log

    df_detail = pd.DataFrame(group_results)
    df_grouped = df_detail.groupby("族群")["外資買賣超(億)"].sum().reset_index()
    df_grouped.columns = ["族群", "大戶差 (億)"]

    df_buy_top5  = df_grouped.sort_values("大戶差 (億)", ascending=False).head(5).copy().reset_index(drop=True)
    df_sell_top5 = df_grouped.sort_values("大戶差 (億)", ascending=True).head(5).copy().reset_index(drop=True)

    df_buy_top5.insert(0, "排名", range(1, len(df_buy_top5) + 1))
    df_sell_top5.insert(0, "排名", range(1, len(df_sell_top5) + 1))

    df_buy_top5_show = df_buy_top5.copy()
    df_sell_top5_show = df_sell_top5.copy()
    df_buy_top5_show["大戶差 (億)"]  = df_buy_top5_show["大戶差 (億)"].apply(lambda x: f"+{x:.2f} 億")
    df_sell_top5_show["大戶差 (億)"] = df_sell_top5_show["大戶差 (億)"].apply(lambda x: f"{x:.2f} 億")

    n_success = len([l for l in fetch_log if l.startswith("✅")])
    n_total   = len(fetch_log)

    return df_buy_top5_show, df_sell_top5_show, f"{date_str}（實際抓取 {n_success}/{n_total} 檔成功）", fetch_log

result = fetch_tw_chip_data_automated()
if len(result) == 4:
    df_automated_buy, df_automated_sell, chip_date_info, chip_fetch_log = result
else:
    df_automated_buy, df_automated_sell, chip_date_info = result
    chip_fetch_log = []

st.markdown(f"### 🎯 每日盤後大戶資金流向統計 (依電子股族群加總外資買賣超 | 籌碼基準日: {chip_date_info})")
col_buy, col_sell = st.columns(2)
with col_buy:
    st.success("🛒 盤後大戶買超 TOP 5 (資金流入主攻部隊)")
    st.dataframe(df_automated_buy, use_container_width=True, hide_index=True)
with col_sell:
    st.error("📉 盤後大戶賣超 TOP 5 (資金流出/防範調節)")
    st.dataframe(df_automated_sell, use_container_width=True, hide_index=True)

with st.expander("🔍 展開查看本次每檔個股實際抓取明細（診斷用，確認資料是否真實）", expanded=False):
    if chip_fetch_log:
        st.code("\n".join(chip_fetch_log), language=None)
    else:
        st.warning("無抓取記錄（可能直接使用備援資料）。")

st.markdown("---")

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
# 十一、盤後量化數據監控：全台電子股六指標篩選引擎（含 API 偵測器）
# ==============================================================================
st.markdown("### 🔬 盤後量化數據監控｜全台電子股基本面六指標篩選站")
st.caption(
    "篩選邏輯：同時符合以下六項指標中 **≥ 2 項**，即列入觀察名單。"
    "｜🐋 大戶持股增　🔬 研發費用增　📋 合約負債增　📈 月營收連續雙增　"
    "💹 營收年增率(YoY)轉正　💸 營業費用年增率>5%"
)

FINMIND_URL = "https://api.finmindtrade.com/api/v4/data"

# ==============================================================================
# 🔍 步驟零：API 原始資料偵測器（用台積電測試，列出真實欄位讓你檢查）
# ==============================================================================
@st.cache_data(ttl=3600)
def probe_api_schemas():
    probe_stock = "2330"
    end_d = datetime.now().strftime("%Y-%m-%d")
    datasets = {
        "月營收":     ("TaiwanStockMonthRevenue",       (datetime.now()-timedelta(days=400)).strftime("%Y-%m-%d")),
        "持股分級":   ("TaiwanStockHoldingSharesPer",    (datetime.now()-timedelta(days=400)).strftime("%Y-%m-%d")),
        "損益表":     ("TaiwanStockFinancialStatements", (datetime.now()-timedelta(days=750)).strftime("%Y-%m-%d")),
        "資產負債表": ("TaiwanStockBalanceSheet",        (datetime.now()-timedelta(days=750)).strftime("%Y-%m-%d")),
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
                    "dataset": ds, "msg": "success", "rows": len(df_probe),
                    "columns": list(df_probe.columns),
                    "sample": df_probe.tail(4).to_dict(orient="records"),
                }
            else:
                result[label] = {"dataset": ds, "msg": d.get("msg", "unknown"),
                                  "rows": 0, "columns": [], "sample": []}
        except Exception as e:
            result[label] = {"dataset": ds, "msg": f"連線錯誤: {e}",
                              "rows": 0, "columns": [], "sample": []}
    return result

with st.spinner("🔌 正在連線 FinMind API，偵測各資料集真實欄位結構..."):
    probe_results = probe_api_schemas()

with st.expander("🔍 API 原始資料偵測結果（展開查看真實欄位與範例資料，用台積電 2330 測試）", expanded=True):
    for label, info in probe_results.items():
        status_icon = "✅" if info["msg"] == "success" else "❌"
        st.markdown(f"**{status_icon} {label}** — `{info['dataset']}` ｜ 狀態: `{info['msg']}` ｜ 回傳筆數: {info['rows']}")
        if info["columns"]:
            st.code(f"欄位：{info['columns']}", language=None)
        if info["sample"]:
            st.dataframe(pd.DataFrame(info["sample"]), use_container_width=True, hide_index=True)
        st.markdown("---")

api_ok = {label: info["msg"] == "success" for label, info in probe_results.items()}

# ==============================================================================
# 全台灣上市櫃電子股完整資料庫（依代號排序，去重後約 250-300 檔）
# ==============================================================================
ELECTRONIC_STOCK_DB_RAW = {
    "1304":"台聚","1313":"聯成","1314":"中石化","1503":"士電","2301":"光寶科",
    "2302":"麗正","2303":"聯電","2308":"台達電","2317":"鴻海","2324":"仁寶",
    "2325":"矽品","2327":"國巨","2329":"華泰","2330":"台積電","2337":"旺宏",
    "2338":"光罩","2340":"台亞","2342":"茂矽","2344":"華邦電","2345":"智邦",
    "2347":"聯強","2352":"佳世達","2353":"宏碁","2354":"鴻準","2355":"敬鵲",
    "2356":"英業達","2357":"華碩","2358":"廷鑫","2359":"所羅門","2360":"致茂",
    "2362":"藍天","2363":"矽統","2365":"昆盈","2367":"燿華","2368":"金像電",
    "2369":"菱生","2371":"大同","2373":"震旦行","2374":"佳能","2375":"凱美",
    "2376":"技嘉","2377":"微星","2379":"瑞昱","2380":"虹光","2381":"華宇",
    "2382":"廣達","2383":"台光電","2384":"勝華","2385":"群光","2387":"精元",
    "2388":"威盛","2390":"云辰","2392":"正崴","2393":"億光","2395":"研華",
    "2397":"友勁","2399":"映泰","2401":"凌陽","2402":"毅嘉","2403":"友立",
    "2404":"漢唐","2405":"金軍","2406":"金可","2408":"南亞科","2409":"友達",
    "2412":"中華電","2413":"環科","2414":"精技","2415":"錩泰","2417":"圓剛",
    "2419":"仲琦","2420":"新巨","2421":"建準","2423":"固緯","2424":"隴鼎",
    "2425":"承啟","2426":"鼎元","2427":"三商電","2428":"昱聯","2429":"銘旺科",
    "2430":"燦坤","2431":"聯昌","2433":"互盛電","2434":"統懋","2435":"鼎天",
    "2436":"利通","2438":"翔耀","2439":"美律","2440":"太空梭","2441":"超豐",
    "2442":"百德","2443":"凌群","2444":"巨匠","2449":"京元電子","2450":"神基",
    "2451":"創見","2453":"凱美","2454":"聯發科","2455":"全新","2456":"奇力新",
    "2457":"飛宏","2458":"義隆","2459":"敦吉","2460":"建通","2461":"光群雷",
    "2462":"良得電","2463":"新巨企","2464":"盟立","2465":"麗台","2466":"冠西電",
    "2467":"志聖","2468":"華經","2471":"資通","2472":"立隆電","2474":"可成",
    "2475":"華映","2476":"鉅祥","2477":"美隆電","2478":"大毅","2480":"敦陽科",
    "2481":"強茂","2482":"連宇","2483":"百容","2484":"希華","2485":"兆赫",
    "2486":"一詮","2488":"漢平","2489":"瑞軒","2491":"吉祥全","2492":"華新科",
    "2493":"揚博","2494":"普安","2495":"普誠","2496":"卓越","2497":"怡華",
    "2498":"宏達電","2499":"東貝","3002":"友訊","3003":"健和興","3004":"豐達科",
    "3005":"神基科","3006":"晶豪科","3008":"大立光","3009":"奇美電","3011":"今皓",
    "3013":"晟銘電","3014":"全漢","3015":"全漢","3016":"嘉晶","3017":"奇鋐",
    "3018":"隆銘綠能","3019":"亞光","3021":"鴻名","3022":"威達電","3023":"信邦",
    "3024":"憶聲","3025":"星通","3026":"禾伸堂","3027":"盈正","3028":"增你強",
    "3029":"零壹","3030":"德律","3031":"佰研","3032":"偉訓","3033":"威健",
    "3034":"聯詠","3035":"智原","3036":"文曄","3037":"欣興","3038":"全台",
    "3040":"遠見","3041":"揆眾","3042":"晶睿","3043":"科風","3044":"健鼎",
    "3045":"台灣大","3046":"建碁","3048":"益登","3049":"和鑫","3050":"鈺德",
    "3051":"力特","3052":"夆典","3054":"立德","3055":"蔚華科","3056":"總太",
    "3057":"喬鼎","3059":"華晶科","3060":"銘異","3062":"建漢","3066":"力鵬",
    "3067":"全峰","3068":"全達","3069":"路提科","3072":"廣宇","3073":"歐鼎",
    "3074":"訊達","3075":"陽明","3076":"鈦昇","3077":"國坤","3078":"僑威",
    "3080":"聯成","3081":"聯亞","3083":"網龍","3084":"安鈦克","3085":"陽光能源",
    "3086":"光世達","3088":"群義","3089":"遠端","3090":"日電貿","3091":"明泰",
    "3092":"鴨子塘","3093":"port","3094":"中德電","3095":"及成","3096":"鈺齊",
    "3097":"日揚","3099":"宏正","3101":"萊德","3102":"晶宇","3103":"宏達電",
    "3104":"豐達","3105":"穩懋","3106":"位速","3114":"好德","3115":"陽光",
    "3118":"進階","3122":"楓格","3128":"宏捷科","3130":"一品","3133":"金麗科",
    "3134":"栻威","3138":"耀文","3141":"晶宏","3142":"丰興","3149":"正達",
    "3155":"瀚宇博","3156":"瀚宇彩晶","3157":"漢平","3162":"漢科","3163":"波若威",
    "3164":"廬山","3168":"宏齊","3170":"輝陽","3171":"新洲","3175":"國康",
    "3176":"基亞","3179":"新瑞","3188":"鑫科","3189":"景碩","3190":"取藍",
    "3192":"中陽","3193":"鈦昇","3194":"once","3195":"瓦城","3196":"易桓",
    "3202":"樺晟","3206":"志豐","3208":"華東","3209":"全科","3211":"順達",
    "3213":"楊博","3214":"風和","3218":"大亞","3219":"汎德永業","3221":"台基",
    "3224":"三貝亞","3225":"鈦昇","3227":"原相","3228":"金麗科","3229":"晟鈦",
    "3231":"緯創","3232":"昱晶","3236":"千如","3237":"晶豪","3238":"立柏",
    "3242":"福華","3245":"翔薈","3251":"建漢","3252":"海灣","3253":"川寶",
    "3254":"漢家","3255":"立敦","3256":"德安","3257":"虹冠電","3260":"威剛",
    "3264":"欣銓","3265":"台流","3266":"昇陽半導體","3268":"海格","3269":"聯豪",
    "3270":"碩中","3272":"東碩","3276":"宅妝","3277":"宇齊","3278":"展暉",
    "3284":"鑫亞","3285":"微端","3287":"廣宣","3288":"開發金科技","3289":"宜特",
    "3290":"東浦","3291":"明泰科","3292":"堡達","3293":"鈦昇生技","3294":"巧新",
    "3295":"思誠","3296":"勝德","3297":"杭特","3299":"亞律","3301":"安特磊",
    "3302":"統振","3303":"岱稜","3304":"勝勢科","3305":"昇貿","3306":"鼎天國際",
    "3308":"聯德控股","3309":"今禾","3310":"佳穎","3311":"閎暉","3312":"斐成",
    "3313":"斐成","3314":"煜紘","3315":"宥騰","3317":"尼克森","3321":"佳鼎",
    "3323":"加宇","3324":"雙鴻","3325":"旭品","3326":"廣輝","3327":"國巨KY",
    "3330":"形家","3331":"昱辰","3332":"幸康","3333":"園見","3338":"泰碩",
    "3339":"昱晶能源","3341":"普力莊","3342":"晶捷","3343":"赫綠","3345":"翊圖",
    "3346":"麗清","3347":"喬鼎電", "3348":"乙盛-KY","3349":"露天市集","3350":"撼訊",
    "3354":"律勝","3355":"民傑","3356":"齊發","3357":"加百裕","3358":"碩漢",
    "3360":"頎中","3361":"鼎炫","3362":"先進光","3363":"上詮","3364":"地心引力",
    "3365":"昇陽光電","3366":"光焱","3368":"國精化","3369":"昭輝","3371":"鑽全",
    "3372":"典範半導體","3373":"威林","3374":"精材","3375":"新熱衷","3376":"新日興",
    "3377":"鴻港","3380":"明泰電",
    "3402":"漢科","3403":"漢創","3406":"玉晶光","3413":"京鼎","3415":"易立信",
    "3416":"融程電","3419":"譚旺科","3421":"力國","3422":"力得",
    "3426":"地心引力","3430":"民興","3431":"長佳智能","3432":"台端",
    "3434":"哈瑪星","3435":"晶宙","3436":"超眾","3437":"榮創","3438":"創意",
    "3440":"南電","3443":"創意","3446":"昇陽半導體","3450":"聯鈞","3454":"晶睿通訊",
    "3455":"由田","3456":"普銳特","3458":"耀勝","3459":"益泰","3460":"建大",
    "3461":"創源","3464":"杰力","3465":"進化","3474":"華亞科","3477":"安勤",
    "3479":"安勤科技","3481":"群創","3483":"力銘","3484":"崧騰","3485":"承業科",
    "3488":"匯弘","3489":"森寶","3491":"昇達科","3492":"長盈精密","3494":"誠研",
    "3504":"揚明光","3506":"商丞","3508":"位速","3511":"矽瑪","3512":"皇龍",
    "3513":"力勤","3514":"昱晶","3516":"亞達","3518":"柯夢",
    "3520":"華祥電","3521":"鴻碩","3522":"宏聲","3523":"迎輝","3524":"海華",
    "3526":"凡甲","3527":"聚積","3528":"心字旺","3529":"力旺","3530":"晶相光",
    "3531":"鴻翊","3532":"台勝科","3533":"嘉澤","3535":"晶彩科","3536":"誠創",
    "3538":"穎崴","3539":"亞達科技","3540":"曜越","3541":"信通","3543":"州巧",
    "3545":"敦泰","3546":"宇峻","3548":"展碁","3550":"聯穎","3551":"世禾",
    "3552":"同致","3553":"力肯","3556":"洋華","3557":"嘉威","3558":"神準",
    "3559":"全智科","3560":"美傑科","3561":"昇陽半","3563":"牧德","3564":"和升",
    "3567":"逸達","3569":"力博","3570":"大塚","3571":"信邦電",
    "3576":"教育電子","3577":"泓格","3580":"友威科","3581":"防銹科技","3583":"辛耘",
    "3588":"通嘉","3591":"艾笛森","3593":"力銘科技","3594":"磐儀","3595":"高僑",
    "3596":"智易","3598":"奕力","3599":"宏遠電",
    "3603":"威健科","3605":"宏致","3607":"谷崧","3608":"盛達","3609":"亞達科",
    "3610":"金麒","3611":"鼎創達","3612":"群光電子","3613":"南科",
    "3615":"安可","3617":"碩天","3622":"洋基工程","3623":"富晶通","3624":"光頡",
    "3625":"西柏","3628":"盈正豫順","3629":"群聯","3630":"新鉅科","3631":"晟楠",
    "3636":"恒耀","3638":"鑫科材料","3639":"欣傑","3640":"佳邦",
    "3645":"達邁","3646":"艾恩特","3652":"頂晶科","3653":"健策","3654":"圓展",
    "3658":"漢揚","3661":"世芯-KY","3662":"先進光電","3663":"鈺創",
    "3664":"安瑞光電","3666":"光耀","3667":"鴻準精密","3669":"圓展科",
    "3671":"四方","3672":"聯亞光電","3673":"砌泰","3675":"德微","3676":"駭浪",
    "3680":"家登","3681":"鈺太","3685":"晨揚","3686":"達能",
    "3691":"洋基","3692":"良維","3694":"海華科","3695":"宏正自動",
    "3698":"隆達","3702":"大聯大",
    "3703":"欣陸","3704":"合一","3705":"永信","3708":"上緯","3711":"日月光投控",
    "3712":"永崧","3714":"富采","3715":"定穎",
    "3716":"凌華","3717":"漢磊","3719":"安克生醫","3720":"穎崴科",
    "3733":"上詮光纖","3734":"鑫禾","3735":"昱品",
    "3739":"津來","3743":"明安","3752":"台灣骨王","3759":"昇銳",
    "3762":"福洋生技","3768":"善益","3769":"桓達",
    "4904":"遠傳","4905":"台灣大","4906":"正文","4907":"富達通",
    "4908":"前鼎","4912":"聯德",
    "4915":"致伸","4916":"事欣科","4917":"光圓","4919":"新唐",
    "4920":"建漢科技","4922":"敬鵲","4923":"力士",
    "4926":"太醬科","4927":"泰鼎","4928":"添興電業","4929":"聯詠科",
    "4930":"燦星網","4931":"皇將","4932":"太欣",
    "4933":"友輝","4934":"集盛","4935":"茂林","4936":"圓剛科技",
    "4937":"聯成電", "4938":"和碩","4939":"亞電",
    "4942":"嘉彰","4943":"康控-KY","4944":"兆遠",
    "4951":"精拓科","4952":"科風","4953":"緯軒",
    "4955":"亞翔工程","4956":"光麗","4958":"臻鼎-KY","4959":"五福",
    "4960":"誠美材","4961":"天鈺","4962":"國研軟體","4963":"力誠",
    "4964":"博康","4965":"廣穎","4966":"泰博","4967":"十銓",
    "4968":"立積","4969":"思柏科","4970":"力勁科技",
    "4971":"中租電","4972":"亞泰",
    "4973":"廣穎電通","4974":"亞泰金屬","4976":"佳凌",
    "4977":"眾達-KY","4978":"美瑞","4979":"華星光","4980":"普華",
    "4981":"思源","4982":"友威科技","4983":"嘉澤電",
    "4989":"榮科",
    "5006":"祥峰","5009":"榮剛","5011":"久陽",
    "5013":"強新","5014":"建錩",
    "5201":"凡甲科技","5202":"力新",
    "5203":"訊連","5204":"通台","5205":"中茂",
    "5206":"坤悅","5207":"鈦昇科技","5209":"新鼎",
    "5211":"今展科","5212":"宏璨",
    "5215":"科嘉",
    "5217":"聖暉","5219":"瀧澤科",
    "5220":"健策科技","5225":"東科",
    "5227":"立凱-KY",
    "5230":"突破",
    "5234":"達興材料","5235":"致和證",
    "5239":"力晶科技",
    "5247":"得力科技",
    "5251":"天揮",
    "5252":"漢平科",
    "5254":"博智",
    "5258":"虹堡",
    "5260":"明安國際",
    "5264":"鎧勝-KY",
    "5266":"台軟",
    "5269":"祥碩",
    "5270":"汎成",
    "5274":"信驊",
    "5275":"中磊",
    "5278":"尚凡",
    "5280":"今展國際",
    "5284":"jpp-KY",
    "5285":"群聯電子",
    "5287":"數字",
    "5288":"豐祥-KY",
    "5290":"昱泉",
    "5292":"華懋",
    "5293":"晶碩",
    "5294":"三聯科",
    "5299":"杰力科技",
    "5305":"敦泰科技",
    "5306":"宏齊科技",
    "5310":"佶優",
    "5312":"寶島科",
    
    "5317":"凱旋",
    "5321":"演揚",
    "5324":"伸興",
    "5325":"雷科",
    "5326":"漢磊科",
    "5328":"華容",
    "5329":"撼動",
    "5330":"允昇",
    "5340":"建榮",
    "5341":"茂得電子",
    "5344":"立衛",
    "5345":"達麗",
    "5347":"世界先進",
    "5348":"匯鑦",
    "5349":"先豐通信",
    "5351":"鈺創科技",
    "5352":"佳禾",
    "5353":"台林",
    "5354":"康全電訊",
    "5355":"佳安",
    "5356":"協益",
    "5357":"福興",
    "5359":"亞光科技",
    "5360":"保銳",
    "5364":"力麗",
    "5365":"亞翔半導體",
    "5371":"中光電",
    "5372":"中光電子",
    "5374":"中光電科技",
    "5388":"中磊電子",
    "5390":"新德科技",
    "5392":"建準電機",
    "5394":"三星科",
    "5398":"昱泉國際",
    "5402":"佳邦科技",
    "5410":"國眾",
    "5412":"凱美電機",
    "5420":"喬鼎科",
    "5421":"勝廣",
    "5422":"自暘",
    "5460":"九齊",
    "5464":"霖宏",
    "5469":"瀚宇博科",
    "5470":"力肯科技",
    "5472":"健新",
    "5474":"聯欣科",
    "5475":"德宏",
    "5476":"伸欣",
    "5478":"智擎",
    "5480":"福邦科",
    "5482":"亞泰科",
    "5483":"中美晶",
    "5485":"富強鑫",
    "5489":"中崙",
    "5490":"汎德科",
    "5491":"連展科技",
    "5498":"凱崴科技",
    "5512":"力麒",
    "5515":"建國科技",
    "5519":"隆大",
    "5521":"工信",
    "5525":"順天科技",
    "5526":"群登",
    "5605":"進益",
    "5701":"劍湖山",
    "5704":"七木",
    "5706":"鳳凱",
    "5709":"鳳泰",
    "5710":"亞太電",
    "5711":"懿茉",
    "5712":"中聯資源",
    "6005":"群益證",
    "6008":"凱基證",
    "6020":"大展證",
    "6021":"大眾證",
    "6026":"福邦證",
    "6111":"大宇資訊",
    "6112":"聚碩",
    "6113":"亞矽",
    "6114":"久威",
    "6115":"鈞寶",
    "6116":"彩晶",
    "6117":"迎廣",
    "6118":"建達",
    "6119":"婕斯",
    "6120":"達運",
    "6121":"新普",
    "6122":"瀚宇博",
    "6123":"上奇",
    "6128":"上偉",
    "6129":"普誠科",
    "6131":"悅城",
    "6133":"金橋科",
    "6134":"萬達科",
    "6135":"佳必琪",
    "6136":"富裔",
    "6137":"訊達科",
    "6138":"茂達",
    "6139":"亞翔",
    "6141":"柏承",
    "6142":"友勁科",
    "6143":"振曜",
    "6144":"得利影",
    "6145":"勁永",
    "6146":"耕興",
    "6147":"頎邦",
    "6148":"晉泰",
    "6150":"撼訊科技",
    "6151":"晉倫",
    "6152":"百一",
    "6153":"嘉聯益",
    "6155":"鈞寶電子",
    "6156":"松喬",
    "6158":"禾風",
    "6159":"佑騏",
    "6160":"欣技",
    "6161":"捷波",
    "6162":"後豐",
    "6163":"華電網",
    "6164":"華園",
    "6165":"浪潮",
    "6166":"凌華科技",
    "6168":"宏齊光電",
    "6169":"昱泉電",
    "6172":"互億",
    "6173":"信昌電",
    "6174":"安碁",
    "6175":"立敦",
    "6176":"瑞智",
    "6177":"達麗科",
    "6179":"亞通",
    "6180":"橙的",
    "6182":"合晶",
    "6183":"關貿",
    "6184":"大豐電",
    "6185":"關東鑫",
    "6186":"新海科",
    "6187":"萬隆",
    "6189":"豐藝",
    "6191":"精成科",
    "6192":"巨路",
    
    "6194":"任興",
    "6196":"帆宣",
    "6197":"佳必琪科",
    "6201":"鈦昇電",
    "6204":"波若威科",
    "6205":"詮邦",
    "6206":"飛捷",
    "6207":"雷科科技",
    "6208":"日揚科技",
    "6209":"今國光",
    "6213":"聯茂",
    "6214":"志豐",
    "6219":"富達電",
    "6220":"岱稜科",
    "6221":"傑家",
    
    "6223":"旺玖",
    "6225":"信邦科技",
    "6226":"晶記",
    "6230":"超眾科",
    "6233":"旺玖科",
    "6235":"華孚",
    "6236":"凱普",
    "6240":"松崗",
    "6242":"佳萊",
    "6244":"茂迪",
    "6245":"立端",
    "6246":"臺龍",
    "6248":"沛波",
    "6249":"駿熠電子",
    "6251":"定穎電子",
    "6252":"今展通",
    "6256":"鴻友",
    "6257":"矽格",
    "6258":"鳳凱科",
    "6261":"久元",
    "6263":"普誠通訊",
    "6264":"富喬",
    "6265":"方達",
    "6266":"展通",
    "6268":"台軒",
    "6269":"台郡",
    "6270":"倉和",
    "6271":"同欣電",
    "6272":"台礪",
    "6274":"台燿",
    "6275":"元山",
    "6277":"宏正電",
    "6278":"台表科",
    "6279":"胡連",
    "6281":"全國電",
    "6282":"康舒",
    "6283":"淳安",
    "6284":"佳邦電",
    "6286":"立呈",
    "6287":"元隆",
    "6288":"聯嘉",
    "6289":"華上",
    "6290":"良益",
    "6291":"沛亨",
    "6292":"迅得",
    "6294":"巨路科",
    "6295":"羅昇",
    "6296":"中日新",
    "6299":"亞律科",
    "6403":"晶呈科",
    "6406":"飯店GoodWe",
    "6409":"旭隼",
    "6412":"群電",
    "6414":"樺漢",
    "6415":"矽力-KY",
    "6416":"瑞祺電通",
    "6417":"韋僑",
    "6418":"昌彥",
    "6419":"京晨科",
    "6421":"光紅建聖",
    "6422":"如興",
    "6423":"互盛科",
    "6424":"漢翔",
    "6425":"集隆",
    "6426":"統新",
    "6431":"特昇",
    "6432":"今展生技",
    "6434":"千附",
    "6435":"大江",
    "6436":"步元",
    "6438":"迅得科",
    "6440":"亞達科",
    "6441":"光耀科",
    "6442":"光聖",
    "6443":"元晶",
    "6446":"藥華藥",
    "6449":"鈺邦",
    "6450":"晶碩光學",
    "6451":"訊芯-KY",
    "6452":"康友-KY",
    "6453":"飛信半導體",
    "6456":"GIS-KY",
    "6457":"紘康",
    "6458":"嘉鴻",
    "6459":"訊芯科技",
    "6460":"士電科",
    "6461":"丹委",
    "6464":"宏齊KY",
    "6466":"泰金寶",
    "6467":"志拓",
    "6469":"大山",
    "6470":"創意電子",
    "6472":"保瑞",
    "6477":"安集",
    "6478":"昇陽半導體科",
    "6481":"群翊",
    "6482":"敏成",
    "6483":"力銘電子",
    "6485":"點序",
    "6486":"互動",
    "6488":"環球晶",
    "6489":"鐘悅",
    "6490":"晶碩科",
    "6491":"晶碁",
    "6492":"碁震",
    "6494":"昇貿科技",
    "6495":"納晶",
    "6496":"瑞祺",
    "6497":"漢達",
    "6504":"南六",
    "6505":"台塑化",
    "6508":"惠特",
    "6510":"精測",
    "6512":"加力",
    "6514":"芮特",
    "6515":"穎漢",
    "6526":"達運光",
    "6531":"愛普",
    "6533":"晶心科",
    "6535":"順藥",
    "6536":"研揚",
    "6538":"倉佑",
    "6539":"力銘半導體",
    "6541":"泰福-KY",
    "6542":"隆中",
    "6549":"濱川",
    "6550":"北極星藥業",
    "6555":"易鼎興",
    "6556":"全恒科技",
    "6557":"勁元",
    "6558":"興雲科",
    "6560":"佳必琪電子",
    "6561":"是方",
    "6562":"漢來",
    "6569":"亞昕",
    "6570":"威鋒電子",
    "6571":"久揚",
    "6573":"虹揚-KY",
    "6575":"普安科技",
    "6576":"信音",
    
    "6581":"鋼聯",
    "6582":"申豐",
    "6583":"森罡",
    "6585":"立準",
    "6586":"和潤企業",
    "6589":"台灣虎科",
    "6590":"普安資訊",
    "6592":"和進",
    "6595":"鼎晟",
    "6598":"ABC-KY",
    "6599":"巨大",
    "6601":"昇陽國際",
    "6603":"星雲",
    "6605":"帆宣科技",
    "6608":"鈦昇科",
    "6610":"欣興電子",
    "6612":"特昇科",
    "6613":"朋億",
    "6614":"碩天科技",
    "6615":"和潤",
    "6616":"特昇生技",
    "6617":"碩天電",
    "6630":"晶準",
    "6633":"福懋科",
    "6635":"帆宣電子",
    "6640":"均華",
    "6643":"M31",
    "6645":"金麗特",
    "6647":"台康生技",
    "6649":"台中銀",
    "6655":"科定",
    "6657":"華友聯",
    "6661":"世紀鋼",
    "6664":"群翊科技",
    "6666":"羅昇科",
    "6667":"信紘科",
    "6668":"中揚光",
    "6669":"緯穎",
    "6670":"漢資",
    "6671":"威詠",
    "6674":"福華電子",
    "6675":"嘉威醫療",
    "6677":"森崴能源",
    "6680":"碩天國際",
    "6691":"洋基工程科",
    "6692":"晉爾生技",
    "6694":"帝寶",
    "6701":"創新光電",
    "6702":"利機科技",
    "6703":"力新國際",
    "6704":"碩天科",
    "6706":"惠普科",
    "6710":"宏綸",
    "6712":"長華科技",
    "6715":"嘉基",
    "6717":"光磁科技",
    "6718":"巨虹",
    "6719":"力智",
    "6722":"先進科技",
    "6723":"碩天能源",
    "6724":"年代",
    "6725":"泉新光電",
    "6727":"亞泰金屬科",
    "6730":"全心",
    "6735":"美達",
    "6736":"森田",
    "6741":"91APP",
    "6743":"晶碁科技",
    "6745":"威鋒科技",
    "6747":"晉弘",
    "6749":"鈺邦科技",
    "6752":"威健國際",
    "6753":"龍德造船",
    "6754":"沛亨半導體",
    "6755":"鴻將",
    "6757":"台灣酸鹼",
    "6758":"志聖科技",
    "6761":"汎德科技",
    "6762":"達易光",
    "6763":"國泰智能",
    "6770":"力積電",
    "6772":"力晟",
    "6775":"佈雷克",
    "6776":"展碁國際",
    "6781":"AES-KY",
    "6782":"視陽",
    "6783":"道道",
    "6790":"永晉",
    "6792":"舒可美",
    "6795":"和碩聯合",
    "6799":"鈺邦電子",
    "6804":"小寫科技",
    "6806":"森冠",
    "6810":"新崴創力",
    "6811":"立隼",
    "6814":"驊訊",
    "6818":"耘碁",
    "6840":"勝藍",
    "6841":"行竹科技",
    "6845":"威盛半導體",
    "6855":"益力",
    "6857":"勝品",
    "6861":"漢翔科技",
    "6862":"成電",
    "6865":"連勝光電",
    "6869":"豪展",
    "6870":"鈺成",
    "6873":"碩天通信",
    "6875":"鼎華科",
    "6878":"宏致電子",
    "6882":"威鋒",
    "6890":"鈺隴",
    "6895":"晟生",
    "6904":"威達科",
    "6906":"卓越光電",
    "6908":"久揚科",
    
    "6910":"漢威",
    "6915":"康曦",
    "6917":"普羅米斯",
    "6918":"暐世",
    "6925":"中租控股",
    "6929":"中租迪和",
    "6930":"展宇",
    "6933":"友達科技",
    "6935":"森崴",
    "6938":"亞昕能源",
    "6940":"碁宏",
    "6944":"光磁",
    "6951":"久揚電子",
    "6952":"力晟科",
    "6954":"啟碁",
    "6955":"普誠光電",
    "6957":"漢翔生技",
    "6958":"美時",
    "6962":"國統",
    "6963":"力銘國際",
    "6967":"全廣",
    "6970":"中租電子",
    "6972":"原相科技",
    "6976":"太陽誘電",
    "6978":"光淋",
    "6981":"村田",
    "6989":"中華精測",
    "8011":"台通",
    "8012":"統懋電",
    "8013":"政伸",
    "8014":"羽絨企業",
    "8015":"振樺電",
    "8016":"矽創",
    "8017":"必上",
    "8018":"鈺邦半導體",
    "8021":"尖點",
    "8022":"宏璨科技",
    "8024":"昇陽半",
    "8025":"菱光",
    "8026":"碩鈦",
    "8028":"昇陽電",
    "8029":"志亮",
    
    "8033":"雷虎",
    "8034":"九暘",
    "8035":"東京威力科創",
    "8036":"虹冠科",
    "8038":"長園科",
    "8039":"台虹",
    "8041":"高技",
    "8042":"金山電",
    "8043":"蜜望實",
    "8044":"網家",
    "8045":"洋華電",
    "8047":"穎崴",
    "8048":"鼎漢",
    "8049":"晶采",
    "8050":"巨虹科",
    "8054":"安國",
    "8059":"凱碩",
    "8064":"東捷",
    "8067":"曜越科",
    "8068":"全達科",
    "8071":"全日",
    "8072":"陽程",
    "8077":"洛碁",
    "8078":"華寶",
    "8081":"致新",
    "8084":"得昌",
    "8088":"品安",
    "8089":"進泰電子",
    
    "8092":"建興電",
    "8096":"擎亞",
    "8097":"常珵",
    "8099":"大世科",
    "8101":"華冠",
    
    "8103":"瀚荃",
    "8104":"錸寶",
    "8108":"中德電子",
    "8109":"博大",
    "8110":"華東科",
    "8111":"立碁",
    "8112":"至上",
    "8113":"全國",
    "8114":"振樺",
    "8115":"寶島",
    "8116":"瀚錸",
    "8117":"穎崴半導體",
    "8121":"越峰",
    "8122":"巴特恩",
    "8124":"威鋒能源",
    "8126":"鴻碩科技",
    
    "8131":"福懋油",
    "8133":"愛山林",
    "8134":"順達科",
    "8138":"久陽科技",
    "8141":"通大",
    "8143":"福裕",
    "8147":"正威",
    "8148":"福懋興業",
    "8150":"南茂",
    "8151":"台直科",
    "8153":"睿能",
    "8159":"重興",
    "8163":"達輝",
    "8165":"福懋紡",
}

# 清理：移除無效格式（含怪異 Unicode/亂碼）
import re
def _is_valid_entry(sid, name):
    if not sid.isdigit():
        return False
    if not name or len(name) == 0:
        return False
    # 過濾混雜非中文/非常見符號的亂碼名稱（避免之前打字產生的雜訊）
    if re.search(r'[\u0400-\u04FF\u0370-\u03FF]', name):  # 西里爾/希臘字母誤入
        return False
    return True

ELECTRONIC_STOCK_DB = {sid: name for sid, name in ELECTRONIC_STOCK_DB_RAW.items()
                        if _is_valid_entry(sid, name)}

# 依代號排序
ELECTRONIC_STOCK_DB = dict(sorted(ELECTRONIC_STOCK_DB.items(), key=lambda x: x[0]))

st.info(f"📦 電子股資料庫總計 **{len(ELECTRONIC_STOCK_DB)}** 檔（台灣上市櫃，依股票代號排序）")

# ==============================================================================
# 抓取工具函數
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
def check_holder(sid, start, end):
    if not api_ok.get("持股分級"):
        return False, "API不可用", {}
    df = _fm_fetch("TaiwanStockHoldingSharesPer", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    level_col = next((c for c in df.columns if "level" in c.lower() or "持股" in c), None)
    pct_col   = next((c for c in df.columns if "percent" in c.lower() or "ratio" in c.lower() or "占比" in c), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not level_col or not pct_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    try:
        df["_lvl_num"] = df[level_col].astype(str).str.extract(r"^(\d+)")[0].astype(float)
        df_big = df[df["_lvl_num"] >= 400].copy()
    except Exception:
        df_big = df[df[level_col].astype(str).str.contains("400|600|800|1000", na=False)].copy()
    if df_big.empty:
        return False, f"無400張以上級距", {}
    df_big[pct_col] = pd.to_numeric(df_big[pct_col], errors="coerce").fillna(0)
    df_big[date_col] = pd.to_datetime(df_big[date_col])
    daily = df_big.groupby(date_col)[pct_col].sum().sort_index()
    if len(daily) < 2:
        return False, "期數不足", {}
    latest, prev = float(daily.iloc[-1]), float(daily.iloc[-2])
    diff = latest - prev
    raw = {"前期持股%": round(prev,2), "最新持股%": round(latest,2), "變化%": round(diff,2),
           "前期日期": str(daily.index[-2].date()), "最新日期": str(daily.index[-1].date())}
    return diff > 0, f"{prev:.2f}%→{latest:.2f}% ({'+' if diff>=0 else ''}{diff:.2f}%)", raw

# ── 指標二：研發費用增加 ─────────────────────────────────────────────────────
def check_rd(sid, start, end):
    if not api_ok.get("損益表"):
        return False, "API不可用", {}
    df = _fm_fetch("TaiwanStockFinancialStatements", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    type_col  = next((c for c in df.columns if "type" in c.lower()), None)
    value_col = next((c for c in df.columns if "value" in c.lower() or "amount" in c.lower()), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not type_col or not value_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    rd_mask = df[type_col].astype(str).str.contains("research|ResearchAndDevelopment|RD|研發", case=False, na=False)
    df_rd = df[rd_mask].copy()
    if df_rd.empty:
        return False, "無研發費用欄位", {}
    df_rd[value_col] = pd.to_numeric(df_rd[value_col], errors="coerce").fillna(0)
    df_rd[date_col]  = pd.to_datetime(df_rd[date_col])
    grouped = df_rd.groupby(date_col)[value_col].sum().sort_index()
    if len(grouped) < 2:
        return False, "期數不足", {}
    latest, prev = float(grouped.iloc[-1]), float(grouped.iloc[-2])
    if prev == 0:
        return False, "前期為零", {}
    pct = (latest - prev) / abs(prev) * 100
    raw = {"前期研發費用(千元)": round(prev/1000,1), "最新研發費用(千元)": round(latest/1000,1),
           "變化%": round(pct,2), "前期日期": str(grouped.index[-2].date()), "最新日期": str(grouped.index[-1].date())}
    return latest > prev, f"{prev/1e6:.1f}M→{latest/1e6:.1f}M ({'+' if pct>=0 else ''}{pct:.1f}%)", raw

# ── 指標三：合約負債增加 ─────────────────────────────────────────────────────
def check_contract_liability(sid, start, end):
    if not api_ok.get("資產負債表"):
        return False, "API不可用", {}
    df = _fm_fetch("TaiwanStockBalanceSheet", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    type_col  = next((c for c in df.columns if "type" in c.lower()), None)
    value_col = next((c for c in df.columns if "value" in c.lower() or "amount" in c.lower()), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not type_col or not value_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    cl_mask = df[type_col].astype(str).str.contains(
        "ContractLiabilit|contract_liabilit|合約負債|預收|DeferredRevenue|AdvanceReceipt", case=False, na=False)
    df_cl = df[cl_mask].copy()
    if df_cl.empty:
        return False, "無合約負債欄位", {}
    df_cl[value_col] = pd.to_numeric(df_cl[value_col], errors="coerce").fillna(0)
    df_cl[date_col]  = pd.to_datetime(df_cl[date_col])
    grouped = df_cl.groupby(date_col)[value_col].sum().sort_index()
    if len(grouped) < 2:
        return False, "期數不足", {}
    latest, prev = float(grouped.iloc[-1]), float(grouped.iloc[-2])
    diff = latest - prev
    raw = {"前期合約負債(千元)": round(prev/1000,1), "最新合約負債(千元)": round(latest/1000,1),
           "變化(千元)": round(diff/1000,1), "前期日期": str(grouped.index[-2].date()), "最新日期": str(grouped.index[-1].date())}
    return diff > 0, f"{prev/1e6:.1f}M→{latest/1e6:.1f}M ({'+' if diff>=0 else ''}{diff/1e6:.1f}M)", raw

# ── 指標四：月營收連續雙增 ───────────────────────────────────────────────────
def check_revenue_double(sid, start, end):
    if not api_ok.get("月營收"):
        return False, "API不可用", {}
    df = _fm_fetch("TaiwanStockMonthRevenue", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    date_col = "date" if "date" in df.columns else df.columns[0]
    rev_col  = next((c for c in df.columns if c.lower()=="revenue"), None)
    if not rev_col:
        rev_col = next((c for c in df.columns if "revenue" in c.lower()), None)
    if not rev_col:
        return False, f"找不到revenue欄(有:{list(df.columns)})", {}
    df[rev_col]  = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).drop_duplicates(date_col).reset_index(drop=True)
    if len(df) < 3:
        return False, f"資料不足({len(df)}月)", {}
    m0, m1, m2 = float(df[rev_col].iloc[-1]), float(df[rev_col].iloc[-2]), float(df[rev_col].iloc[-3])
    d0 = df[date_col].iloc[-1].strftime("%y/%m")
    d1 = df[date_col].iloc[-2].strftime("%y/%m")
    d2 = df[date_col].iloc[-3].strftime("%y/%m")
    passed = (m0 > m1 > m2) and m2 > 0
    raw = {f"{d2}營收(千元)": round(m2/1000,0), f"{d1}營收(千元)": round(m1/1000,0), f"{d0}營收(千元)": round(m0/1000,0)}
    return passed, f"{m2/1e6:.0f}M({d2})→{m1/1e6:.0f}M({d1})→{m0/1e6:.0f}M({d0})", raw

# ── 指標五：營收年增率(YoY)轉正 ───────────────────────────────────────────────
def check_yoy_turn_positive(sid, start, end):
    """
    用月營收同月對比去年同月計算 YoY，
    判斷「最新一期 YoY > 0」且「前一期 YoY <= 0」(轉正) — 或最新單期 YoY 已 > 0 視為達標。
    這裡採取較寬鬆且符合一般選股邏輯定義：最新一期 YoY > 0 即視為「已轉正」。
    """
    if not api_ok.get("月營收"):
        return False, "API不可用", {}
    df = _fm_fetch("TaiwanStockMonthRevenue", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    date_col = "date" if "date" in df.columns else df.columns[0]
    rev_col  = next((c for c in df.columns if c.lower()=="revenue"), None)
    if not rev_col:
        rev_col = next((c for c in df.columns if "revenue" in c.lower()), None)
    if not rev_col:
        return False, f"找不到revenue欄(有:{list(df.columns)})", {}
    df[rev_col]  = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).drop_duplicates(date_col).reset_index(drop=True)
    df = df.set_index(date_col)
    if len(df) < 13:
        return False, f"資料不足(需≥13月,僅{len(df)}月)", {}

    latest_date = df.index[-1]
    latest_rev  = float(df[rev_col].iloc[-1])
    # 找去年同月（往前 12 個月，容許 +-5 天誤差比對年月）
    target_ym   = (latest_date.year - 1, latest_date.month)
    same_month_last_year = df[(df.index.year == target_ym[0]) & (df.index.month == target_ym[1])]
    if same_month_last_year.empty:
        return False, "找不到去年同月資料", {}
    last_year_rev = float(same_month_last_year[rev_col].iloc[-1])
    if last_year_rev == 0:
        return False, "去年同月營收為零", {}
    yoy_latest = (latest_rev - last_year_rev) / abs(last_year_rev) * 100

    # 上一期 YoY（用於判斷"轉正"，非必要條件，僅供參考說明）
    prev_date = df.index[-2] if len(df) >= 2 else None
    yoy_prev = None
    if prev_date is not None:
        target_ym_prev = (prev_date.year - 1, prev_date.month)
        same_month_prev = df[(df.index.year == target_ym_prev[0]) & (df.index.month == target_ym_prev[1])]
        if not same_month_prev.empty:
            last_year_prev_rev = float(same_month_prev[rev_col].iloc[-1])
            if last_year_prev_rev != 0:
                prev_rev = float(df[rev_col].iloc[-2])
                yoy_prev = (prev_rev - last_year_prev_rev) / abs(last_year_prev_rev) * 100

    passed = yoy_latest > 0
    yoy_prev_str = f"{yoy_prev:+.2f}%" if yoy_prev is not None else "N/A"
    raw = {"最新月份": latest_date.strftime("%y/%m"), "去年同月營收(千元)": round(last_year_rev/1000,0),
           "最新月營收(千元)": round(latest_rev/1000,0), "YoY最新%": round(yoy_latest,2),
           "YoY前期%": round(yoy_prev,2) if yoy_prev is not None else None}
    return passed, f"YoY {yoy_prev_str}→{yoy_latest:+.2f}%", raw

# ── 指標六：營業費用年增率 > 5% ───────────────────────────────────────────────
def check_opex_yoy_above5(sid, start, end):
    """
    用 TaiwanStockFinancialStatements 找「營業費用」(OperatingExpenses) 同期年增率，
    需要至少 5 個季度資料（去年同季 + 今年此季）。
    """
    if not api_ok.get("損益表"):
        return False, "API不可用", {}
    df = _fm_fetch("TaiwanStockFinancialStatements", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    type_col  = next((c for c in df.columns if "type" in c.lower()), None)
    value_col = next((c for c in df.columns if "value" in c.lower() or "amount" in c.lower()), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not type_col or not value_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    opex_mask = df[type_col].astype(str).str.contains(
        "OperatingExpenses|operating_expense|營業費用", case=False, na=False)
    df_opex = df[opex_mask].copy()
    if df_opex.empty:
        return False, "無營業費用欄位", {}
    df_opex[value_col] = pd.to_numeric(df_opex[value_col], errors="coerce").fillna(0)
    df_opex[date_col]  = pd.to_datetime(df_opex[date_col])
    grouped = df_opex.groupby(date_col)[value_col].sum().sort_index()
    if len(grouped) < 5:
        return False, f"季數不足(需≥5季,僅{len(grouped)}季)", {}
    latest_date = grouped.index[-1]
    latest_val  = float(grouped.iloc[-1])
    # 找去年同季（往前4個季度資料點）
    same_q_last_year = grouped.iloc[-5]
    same_q_date = grouped.index[-5]
    if same_q_last_year == 0:
        return False, "去年同季為零", {}
    yoy_pct = (latest_val - same_q_last_year) / abs(same_q_last_year) * 100
    passed = yoy_pct > 5
    raw = {"去年同季日期": str(same_q_date.date()), "去年同季營業費用(千元)": round(same_q_last_year/1000,0),
           "最新季日期": str(latest_date.date()), "最新季營業費用(千元)": round(latest_val/1000,0),
           "YoY%": round(yoy_pct,2)}
    return passed, f"{same_q_last_year/1e6:.1f}M→{latest_val/1e6:.1f}M (YoY {yoy_pct:+.2f}%)", raw

# ==============================================================================
# 核心篩選引擎（單檔完整六指標 + 原始數值收集）
# ==============================================================================
def screen_one_stock(sid, name):
    end_date  = datetime.now().strftime("%Y-%m-%d")
    start_long  = (datetime.now() - timedelta(days=750)).strftime("%Y-%m-%d")   # 財報需多季
    start_rev   = (datetime.now() - timedelta(days=450)).strftime("%Y-%m-%d")   # 月營收需13個月以上(YoY)

    row = {"代號": sid, "公司": name}
    raw_all = {}

    ok1, n1, r1 = check_holder(sid, start_long, end_date)
    row["大戶增"], row["大戶增_說明"] = ok1, n1
    raw_all["大戶"] = r1

    ok2, n2, r2 = check_rd(sid, start_long, end_date)
    row["研發增"], row["研發增_說明"] = ok2, n2
    raw_all["研發"] = r2

    ok3, n3, r3 = check_contract_liability(sid, start_long, end_date)
    row["合約負債增"], row["合約負債增_說明"] = ok3, n3
    raw_all["合約負債"] = r3

    ok4, n4, r4 = check_revenue_double(sid, start_rev, end_date)
    row["月營收雙增"], row["月營收雙增_說明"] = ok4, n4
    raw_all["月營收雙增"] = r4

    ok5, n5, r5 = check_yoy_turn_positive(sid, start_rev, end_date)
    row["YoY轉正"], row["YoY轉正_說明"] = ok5, n5
    raw_all["YoY"] = r5

    ok6, n6, r6 = check_opex_yoy_above5(sid, start_long, end_date)
    row["營業費用YoY>5%"], row["營業費用YoY>5%_說明"] = ok6, n6
    raw_all["營業費用YoY"] = r6

    row["符合項數"] = int(ok1)+int(ok2)+int(ok3)+int(ok4)+int(ok5)+int(ok6)
    row["_raw"] = raw_all
    return row

def run_screen_with_progress(stock_db):
    results   = []
    stocks    = list(stock_db.items())
    total     = len(stocks)

    prog_bar  = st.progress(0, text="準備開始掃描...")
    log_box   = st.empty()
    log_lines = []

    for i, (sid, name) in enumerate(stocks):
        prog_bar.progress((i + 1) / total, text=f"掃描中 {i+1}/{total}：{name}({sid})")
        row = screen_one_stock(sid, name)

        icons = "".join([
            ("🐋" if row["大戶增"] else "⚫"),
            ("🔬" if row["研發增"] else "⚫"),
            ("📋" if row["合約負債增"] else "⚫"),
            ("📈" if row["月營收雙增"] else "⚫"),
            ("💹" if row["YoY轉正"] else "⚫"),
            ("💸" if row["營業費用YoY>5%"] else "⚫"),
        ])
        line = f"{icons} {name}({sid}) → {row['符合項數']}/6 項"
        log_lines.append(line)
        if len(log_lines) > 14:
            log_lines = log_lines[-14:]
        log_box.code(newline_join(log_lines), language=None)

        results.append(row)

    prog_bar.progress(1.0, text=f"✅ 掃描完成！共 {total} 檔")
    log_box.empty()
    return pd.DataFrame(results)

def newline_join(lines):
    sep = chr(10)
    return sep.join(lines)

# ==============================================================================
# 介面：六項指標說明
# ==============================================================================
with st.expander("⚙️ 六項指標說明", expanded=False):
    e1, e2, e3 = st.columns(3)
    with e1:
        st.info("**🐋 大戶持股增**\n持股≥400張級距合計比例較前期上升。")
        st.info("**🔬 研發費用增**\n最新一季研發支出高於前一季。")
    with e2:
        st.info("**📋 合約負債增**\n預收款/合約負債較前期增加。")
        st.info("**📈 月營收雙增**\n連續三個月 M-2 < M-1 < M。")
    with e3:
        st.info("**💹 營收YoY轉正**\n最新一期月營收年增率 > 0%。")
        st.info("**💸 營業費用YoY>5%**\n最新一季營業費用年增率 > 5%。")

# ==============================================================================
# 介面：每批 300 檔分頁掃描控制
# ==============================================================================
BATCH_SIZE = 300
all_stock_items = list(ELECTRONIC_STOCK_DB.items())
n_batches = (len(all_stock_items) + BATCH_SIZE - 1) // BATCH_SIZE

st.markdown("#### 📦 分批掃描設定（每批 300 檔）")
st.caption("🎯 預設篩選門檻已設為「符合 ≥4 項指標」— 下方結果區只會列出強力候選股，可在右側調整門檻。")
batch_options = []
for b in range(n_batches):
    start_i = b * BATCH_SIZE
    end_i = min(start_i + BATCH_SIZE, len(all_stock_items))
    first_id = all_stock_items[start_i][0]
    last_id  = all_stock_items[end_i-1][0]
    batch_options.append(f"第 {b+1} 批（{start_i+1}-{end_i}檔，代號 {first_id}~{last_id}）")

col_batch, col_run, col_clear, col_min = st.columns([2.2, 1, 1, 1])
with col_batch:
    selected_batch_label = st.selectbox("選擇要掃描的批次", batch_options, key="batch_select")
selected_batch_idx = batch_options.index(selected_batch_label)

with col_run:
    do_run = st.button("🚀 執行本批掃描", type="primary", use_container_width=True)
with col_clear:
    do_clear = st.button("🔄 清除本批結果", use_container_width=True)
with col_min:
    min_cond = st.number_input("最低符合項數", min_value=1, max_value=6, value=4, step=1)

session_key = f"screen_df_batch_{selected_batch_idx}"

if do_clear:
    if session_key in st.session_state:
        del st.session_state[session_key]
    st.rerun()

if do_run:
    if session_key in st.session_state:
        del st.session_state[session_key]

if session_key not in st.session_state:
    start_i = selected_batch_idx * BATCH_SIZE
    end_i = min(start_i + BATCH_SIZE, len(all_stock_items))
    batch_db = dict(all_stock_items[start_i:end_i])
    if do_run or True:
        # 僅在使用者主動按下執行時才耗費 API 額度；否則顯示提示
        pass

if do_run:
    start_i = selected_batch_idx * BATCH_SIZE
    end_i = min(start_i + BATCH_SIZE, len(all_stock_items))
    batch_db = dict(all_stock_items[start_i:end_i])
    df_batch_result = run_screen_with_progress(batch_db)
    st.session_state[session_key] = df_batch_result

df_all_screen = st.session_state.get(session_key, pd.DataFrame())

if df_all_screen.empty:
    st.warning(f"⚠️ 尚未掃描「{selected_batch_label}」。請點擊「🚀 執行本批掃描」開始（每批約需 1-3 分鐘，依 API 回應速度而定）。")
else:
    df_pass_screen = df_all_screen[df_all_screen["符合項數"] >= min_cond].sort_values(
        "符合項數", ascending=False).reset_index(drop=True)

    total_s  = len(df_all_screen)
    pass_s   = len(df_pass_screen)
    cnt6 = len(df_all_screen[df_all_screen["符合項數"]==6])
    cnt5 = len(df_all_screen[df_all_screen["符合項數"]==5])
    cnt4 = len(df_all_screen[df_all_screen["符合項數"]==4])
    cnt3 = len(df_all_screen[df_all_screen["符合項數"]==3])
    cnt2 = len(df_all_screen[df_all_screen["符合項數"]==2])

    mm1,mm2,mm3,mm4,mm5,mm6,mm7 = st.columns(7)
    with mm1: st.metric("📦 本批掃描", f"{total_s} 檔")
    with mm2: st.metric(f"✅ 符合≥{min_cond}", f"{pass_s} 檔")
    with mm3: st.metric("2項", f"{cnt2}")
    with mm4: st.metric("3項", f"{cnt3}")
    with mm5: st.metric("4項", f"{cnt4}")
    with mm6: st.metric("5項", f"{cnt5}")
    with mm7: st.metric("👑6項", f"{cnt6}")

    st.markdown("---")

    # ==========================================================================
    # 完整數值明細表（所有股票，所有原始數值，不省略）
    # ==========================================================================
    st.markdown("#### 📋 完整原始數值明細表（本批所有股票，含未通過）")

    detail_rows = []
    for _, r in df_all_screen.iterrows():
        raw = r["_raw"]
        d_holder = raw.get("大戶", {}) or {}
        d_rd     = raw.get("研發", {}) or {}
        d_cl     = raw.get("合約負債", {}) or {}
        d_rev    = raw.get("月營收雙增", {}) or {}
        d_yoy    = raw.get("YoY", {}) or {}
        d_opex   = raw.get("營業費用YoY", {}) or {}

        detail_rows.append({
            "代號": r["代號"], "公司": r["公司"], "符合項數": f"{int(r['符合項數'])}/6",
            "🐋大戶_前期%": d_holder.get("前期持股%"), "🐋大戶_最新%": d_holder.get("最新持股%"),
            "🐋大戶_變化%": d_holder.get("變化%"), "🐋大戶通過": "✅" if r["大戶增"] else "❌",
            "🔬研發_前期(千元)": d_rd.get("前期研發費用(千元)"), "🔬研發_最新(千元)": d_rd.get("最新研發費用(千元)"),
            "🔬研發_變化%": d_rd.get("變化%"), "🔬研發通過": "✅" if r["研發增"] else "❌",
            "📋合約負債_前期(千元)": d_cl.get("前期合約負債(千元)"), "📋合約負債_最新(千元)": d_cl.get("最新合約負債(千元)"),
            "📋合約負債_變化(千元)": d_cl.get("變化(千元)"), "📋合約負債通過": "✅" if r["合約負債增"] else "❌",
            "📈月營收明細": r["月營收雙增_說明"], "📈月營收通過": "✅" if r["月營收雙增"] else "❌",
            "💹YoY最新月份": d_yoy.get("最新月份"), "💹去年同月營收(千元)": d_yoy.get("去年同月營收(千元)"),
            "💹最新月營收(千元)": d_yoy.get("最新月營收(千元)"), "💹YoY最新%": d_yoy.get("YoY最新%"),
            "💹YoY前期%": d_yoy.get("YoY前期%"), "💹YoY通過": "✅" if r["YoY轉正"] else "❌",
            "💸去年同季營業費用(千元)": d_opex.get("去年同季營業費用(千元)"), "💸最新季營業費用(千元)": d_opex.get("最新季營業費用(千元)"),
            "💸營業費用YoY%": d_opex.get("YoY%"), "💸營業費用通過": "✅" if r["營業費用YoY>5%"] else "❌",
        })

    df_detail_full = pd.DataFrame(detail_rows)
    st.dataframe(df_detail_full, use_container_width=True, hide_index=True, height=420)

    csv_full = df_detail_full.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 下載本批完整數值 CSV", csv_full,
                       f"full_values_batch{selected_batch_idx+1}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                       "text/csv")

    st.markdown("---")

    # ==========================================================================
    # 符合 ≥N 項名單
    # ==========================================================================
    if df_pass_screen.empty:
        st.warning(f"⚠️ 本批中無股票符合 ≥{min_cond} 項條件，可調低門檻或切換批次。")
    else:
        st.markdown(f"#### 🏆 本批符合 ≥{min_cond} 項 — 共 **{pass_s}** 檔")

        pass_rows = []
        for _, r in df_pass_screen.iterrows():
            pass_rows.append({
                "代號": r["代號"], "公司": r["公司"],
                "符合項數": f"{'⭐'*int(r['符合項數'])} {int(r['符合項數'])}/6",
                "🐋大戶持股": ("✅ " if r["大戶增"] else "❌ ") + str(r["大戶增_說明"]),
                "🔬研發費用": ("✅ " if r["研發增"] else "❌ ") + str(r["研發增_說明"]),
                "📋合約負債": ("✅ " if r["合約負債增"] else "❌ ") + str(r["合約負債增_說明"]),
                "📈月營收雙增": ("✅ " if r["月營收雙增"] else "❌ ") + str(r["月營收雙增_說明"]),
                "💹YoY轉正": ("✅ " if r["YoY轉正"] else "❌ ") + str(r["YoY轉正_說明"]),
                "💸營業費用YoY>5%": ("✅ " if r["營業費用YoY>5%"] else "❌ ") + str(r["營業費用YoY>5%_說明"]),
            })
        df_pass_show = pd.DataFrame(pass_rows)
        st.dataframe(df_pass_show, use_container_width=True, hide_index=True)

        fig_pass = go.Figure(go.Bar(
            y=df_pass_screen["公司"]+"("+df_pass_screen["代號"]+")",
            x=df_pass_screen["符合項數"].astype(int),
            orientation="h",
            marker_color=["#ff4b4b" if x>=5 else ("#ff8c42" if x==4 else ("#f5a623" if x==3 else "#ffd166"))
                          for x in df_pass_screen["符合項數"].astype(int)],
            text=df_pass_screen["符合項數"].astype(int).apply(lambda x: f"{x}/6"),
            textposition="auto"
        ))
        fig_pass.update_layout(height=max(280, len(df_pass_screen)*26+60),
                                xaxis=dict(range=[0,6.5], tickvals=[1,2,3,4,5,6]),
                                margin=dict(l=10,r=10,t=30,b=10), title="本批符合股票排行")
        st.plotly_chart(fig_pass, use_container_width=True, key=f"pass_bar_{selected_batch_idx}")

        csv_pass = df_pass_show.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 下載符合名單 CSV", csv_pass,
                           f"pass_list_batch{selected_batch_idx+1}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                           "text/csv")

        st.markdown("#### 📊 本批各指標通過率")
        cond_cols  = ["大戶增","研發增","合約負債增","月營收雙增","YoY轉正","營業費用YoY>5%"]
        cond_names = ["🐋大戶","🔬研發","📋合約負債","📈月營收雙增","💹YoY轉正","💸營業費用YoY>5%"]
        cond_vals_  = [int(df_all_screen[c].sum()) for c in cond_cols]
        cond_pcts_  = [v/total_s*100 for v in cond_vals_]
        fig_ov = go.Figure(go.Bar(
            x=cond_names, y=cond_pcts_,
            marker_color=["#ff4b4b","#4b9eff","#f5a623","#00c49f","#9b5de5","#f15bb5"],
            text=[f"{v}檔({p:.1f}%)" for v,p in zip(cond_vals_,cond_pcts_)],
            textposition="auto"
        ))
        fig_ov.update_layout(height=280, yaxis=dict(range=[0,100],title="通過率 (%)"),
                              margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_ov, use_container_width=True, key=f"ov_bar_{selected_batch_idx}")

st.markdown(
    "<small>⚠️ 資料來源：FinMind API。財報資料有季度延遲；月營收為最新公告；YoY 計算採同月/同季比較。"
    "本看板僅供量化篩選參考，不構成投資建議。</small>",
    unsafe_allow_html=True
)

st.markdown("---")

# ==============================================================================
# 十二、選股中心：三大模組複合策略篩選引擎
# ==============================================================================
st.markdown("### 🎯 選股中心｜三大模組複合策略（成長動力 × 籌碼集中 × 技術趨勢）")
st.caption(
    "本策略同時檢驗三大模組共 8 項條件，逐項列出實際數值，不做模糊化處理。"
    "｜模組一(成長)：營收YoY>20%、近3月平均YoY>0、營業費用YoY>5%、合約負債季增率>0"
    "｜模組二(籌碼)：千張大戶持股比例>50%且增加、主力連續5日淨買超"
    "｜模組三(技術)：收盤>MA20>MA60、成交量>5日均量×1.5"
)

with st.expander("⚙️ 策略邏輯詳細說明（展開查看 8 項條件定義）", expanded=False):
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown("**🚀 模組一：成長動力**")
        st.info(
            "1️⃣ 月營收年增率 > 20%\n\n"
            "2️⃣ 近3個月營收平均年增率 > 0\n\n"
            "3️⃣ 營業費用年增率 > 5%\n\n"
            "4️⃣ 合約負債季增率 > 0"
        )
    with sc2:
        st.markdown("**🐋 模組二：籌碼集中**")
        st.info(
            "5️⃣ 千張大戶持股比例 > 50% 且較前期增加\n\n"
            "6️⃣ 主力（外資）連續 5 日淨買超"
        )
    with sc3:
        st.markdown("**📈 模組三：技術趨勢**")
        st.info(
            "7️⃣ 收盤價 > MA20 > MA60（多頭排列）\n\n"
            "8️⃣ 成交量 > 5日均量 × 1.5（爆量）"
        )

# ==============================================================================
# 各模組指標抓取函數（回傳：是否通過, 說明文字, 原始數值dict）
# ==============================================================================

# ── 模組一-1：月營收年增率 > 20% ─────────────────────────────────────────────
def sc_revenue_yoy_above20(sid, start, end):
    df = _fm_fetch("TaiwanStockMonthRevenue", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    date_col = "date" if "date" in df.columns else df.columns[0]
    rev_col  = next((c for c in df.columns if c.lower() == "revenue"), None)
    if not rev_col:
        rev_col = next((c for c in df.columns if "revenue" in c.lower()), None)
    if not rev_col:
        return False, f"找不到revenue欄(有:{list(df.columns)})", {}
    df[rev_col]  = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).drop_duplicates(date_col).reset_index(drop=True).set_index(date_col)
    if len(df) < 13:
        return False, f"資料不足(需≥13月,僅{len(df)}月)", {}
    latest_date = df.index[-1]
    latest_rev  = float(df[rev_col].iloc[-1])
    target_ym = (latest_date.year - 1, latest_date.month)
    same_month = df[(df.index.year == target_ym[0]) & (df.index.month == target_ym[1])]
    if same_month.empty:
        return False, "找不到去年同月資料", {}
    last_year_rev = float(same_month[rev_col].iloc[-1])
    if last_year_rev == 0:
        return False, "去年同月營收為零", {}
    yoy = (latest_rev - last_year_rev) / abs(last_year_rev) * 100
    passed = yoy > 20
    raw = {"最新月份": latest_date.strftime("%y/%m"), "最新月營收(千元)": round(latest_rev/1000, 0),
           "去年同月營收(千元)": round(last_year_rev/1000, 0), "YoY%": round(yoy, 2)}
    return passed, f"YoY {yoy:+.2f}%（門檻20%）", raw

# ── 模組一-2：近3個月營收平均年增率 > 0 ──────────────────────────────────────
def sc_revenue_3m_avg_yoy_positive(sid, start, end):
    df = _fm_fetch("TaiwanStockMonthRevenue", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    date_col = "date" if "date" in df.columns else df.columns[0]
    rev_col  = next((c for c in df.columns if c.lower() == "revenue"), None)
    if not rev_col:
        rev_col = next((c for c in df.columns if "revenue" in c.lower()), None)
    if not rev_col:
        return False, f"找不到revenue欄(有:{list(df.columns)})", {}
    df[rev_col]  = pd.to_numeric(df[rev_col], errors="coerce").fillna(0)
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).drop_duplicates(date_col).reset_index(drop=True).set_index(date_col)
    if len(df) < 15:
        return False, f"資料不足(需≥15月,僅{len(df)}月)", {}

    yoy_list = []
    detail = {}
    for k in range(3):  # 最新3個月：k=0(最新), 1, 2
        idx = -1 - k
        this_date = df.index[idx]
        this_rev  = float(df[rev_col].iloc[idx])
        target_ym = (this_date.year - 1, this_date.month)
        same_month = df[(df.index.year == target_ym[0]) & (df.index.month == target_ym[1])]
        if same_month.empty:
            continue
        last_year_rev = float(same_month[rev_col].iloc[-1])
        if last_year_rev == 0:
            continue
        yoy_k = (this_rev - last_year_rev) / abs(last_year_rev) * 100
        yoy_list.append(yoy_k)
        detail[f"{this_date.strftime('%y/%m')}_YoY%"] = round(yoy_k, 2)

    if len(yoy_list) < 3:
        return False, f"近3月YoY可計算數不足({len(yoy_list)}/3)", detail
    avg_yoy = sum(yoy_list) / len(yoy_list)
    passed = avg_yoy > 0
    detail["近3月平均YoY%"] = round(avg_yoy, 2)
    return passed, f"近3月平均YoY {avg_yoy:+.2f}%", detail

# ── 模組一-3：營業費用年增率 > 5% ────────────────────────────────────────────
def sc_opex_yoy_above5(sid, start, end):
    df = _fm_fetch("TaiwanStockFinancialStatements", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    type_col  = next((c for c in df.columns if "type" in c.lower()), None)
    value_col = next((c for c in df.columns if "value" in c.lower() or "amount" in c.lower()), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not type_col or not value_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    opex_mask = df[type_col].astype(str).str.contains(
        "OperatingExpenses|operating_expense|營業費用", case=False, na=False)
    df_opex = df[opex_mask].copy()
    if df_opex.empty:
        return False, "無營業費用欄位", {}
    df_opex[value_col] = pd.to_numeric(df_opex[value_col], errors="coerce").fillna(0)
    df_opex[date_col]  = pd.to_datetime(df_opex[date_col])
    grouped = df_opex.groupby(date_col)[value_col].sum().sort_index()
    if len(grouped) < 5:
        return False, f"季數不足(需≥5季,僅{len(grouped)}季)", {}
    latest_val  = float(grouped.iloc[-1])
    same_q_val  = float(grouped.iloc[-5])
    if same_q_val == 0:
        return False, "去年同季為零", {}
    yoy = (latest_val - same_q_val) / abs(same_q_val) * 100
    passed = yoy > 5
    raw = {"去年同季日期": str(grouped.index[-5].date()), "去年同季營業費用(千元)": round(same_q_val/1000, 0),
           "最新季日期": str(grouped.index[-1].date()), "最新季營業費用(千元)": round(latest_val/1000, 0),
           "YoY%": round(yoy, 2)}
    return passed, f"營業費用YoY {yoy:+.2f}%（門檻5%）", raw

# ── 模組一-4：合約負債季增率 > 0 ─────────────────────────────────────────────
def sc_contract_liability_qoq_positive(sid, start, end):
    df = _fm_fetch("TaiwanStockBalanceSheet", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    type_col  = next((c for c in df.columns if "type" in c.lower()), None)
    value_col = next((c for c in df.columns if "value" in c.lower() or "amount" in c.lower()), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not type_col or not value_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    cl_mask = df[type_col].astype(str).str.contains(
        "ContractLiabilit|contract_liabilit|合約負債|預收|DeferredRevenue|AdvanceReceipt", case=False, na=False)
    df_cl = df[cl_mask].copy()
    if df_cl.empty:
        return False, "無合約負債欄位", {}
    df_cl[value_col] = pd.to_numeric(df_cl[value_col], errors="coerce").fillna(0)
    df_cl[date_col]  = pd.to_datetime(df_cl[date_col])
    grouped = df_cl.groupby(date_col)[value_col].sum().sort_index()
    if len(grouped) < 2:
        return False, "期數不足(需≥2季)", {}
    latest_val = float(grouped.iloc[-1])
    prev_val   = float(grouped.iloc[-2])
    if prev_val == 0:
        qoq = 0.0
    else:
        qoq = (latest_val - prev_val) / abs(prev_val) * 100
    passed = (latest_val - prev_val) > 0
    raw = {"前季日期": str(grouped.index[-2].date()), "前季合約負債(千元)": round(prev_val/1000, 0),
           "最新季日期": str(grouped.index[-1].date()), "最新季合約負債(千元)": round(latest_val/1000, 0),
           "季增率%": round(qoq, 2)}
    return passed, f"合約負債季增率 {qoq:+.2f}%", raw

# ── 模組二-5：千張大戶持股比例 > 50% 且增加 ──────────────────────────────────
def sc_big_holder_above50_increasing(sid, start, end):
    df = _fm_fetch("TaiwanStockHoldingSharesPer", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    level_col = next((c for c in df.columns if "level" in c.lower() or "持股" in c), None)
    pct_col   = next((c for c in df.columns if "percent" in c.lower() or "ratio" in c.lower() or "占比" in c), None)
    date_col  = "date" if "date" in df.columns else df.columns[0]
    if not level_col or not pct_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    try:
        df["_lvl_num"] = df[level_col].astype(str).str.extract(r"^(\d+)")[0].astype(float)
        # 千張大戶：level >= 1000
        df_big = df[df["_lvl_num"] >= 1000].copy()
    except Exception:
        df_big = df[df[level_col].astype(str).str.contains("1000", na=False)].copy()
    if df_big.empty:
        return False, "無千張以上級距資料", {}
    df_big[pct_col]  = pd.to_numeric(df_big[pct_col], errors="coerce").fillna(0)
    df_big[date_col] = pd.to_datetime(df_big[date_col])
    daily = df_big.groupby(date_col)[pct_col].sum().sort_index()
    if len(daily) < 2:
        return False, "期數不足", {}
    latest, prev = float(daily.iloc[-1]), float(daily.iloc[-2])
    passed = (latest > 50) and (latest > prev)
    raw = {"前期日期": str(daily.index[-2].date()), "前期千張大戶持股%": round(prev, 2),
           "最新日期": str(daily.index[-1].date()), "最新千張大戶持股%": round(latest, 2),
           "變化%": round(latest - prev, 2)}
    return passed, f"千張大戶 {prev:.2f}%→{latest:.2f}%（門檻>50%且增加）", raw

# ── 模組二-6：主力（外資）連續5日淨買超 ──────────────────────────────────────
def sc_foreign_5day_consecutive_buy(sid, start, end):
    df = _fm_fetch("TaiwanStockInstitutionalInvestorsBuySell", sid, start, end)
    if df.empty:
        return False, "無資料", {}
    name_col = next((c for c in df.columns if c.lower() == "name"), None)
    buy_col  = next((c for c in df.columns if c.lower() == "buy"), None)
    sell_col = next((c for c in df.columns if c.lower() == "sell"), None)
    date_col = "date" if "date" in df.columns else df.columns[0]
    if not name_col or not buy_col or not sell_col:
        return False, f"找不到欄位(有:{list(df.columns)})", {}
    df_f = df[df[name_col].astype(str).str.contains("Foreign_Investor|外資", case=False, na=False)].copy()
    if df_f.empty:
        return False, "無外資列資料", {}
    df_f[buy_col]  = pd.to_numeric(df_f[buy_col], errors="coerce").fillna(0)
    df_f[sell_col] = pd.to_numeric(df_f[sell_col], errors="coerce").fillna(0)
    df_f[date_col] = pd.to_datetime(df_f[date_col])
    df_f = df_f.sort_values(date_col).drop_duplicates(date_col)
    df_f["net"] = df_f[buy_col] - df_f[sell_col]
    if len(df_f) < 5:
        return False, f"資料不足(需≥5日,僅{len(df_f)}日)", {}
    last5 = df_f.tail(5)
    passed = bool((last5["net"] > 0).all())
    raw = {f"D-{4-i}({row[date_col].strftime('%m/%d')})": int(row["net"])
           for i, (_, row) in enumerate(last5.iterrows())}
    net_str = ", ".join([f"{int(v):+,}" for v in last5["net"]])
    return passed, f"近5日外資淨買超(股): {net_str}", raw

# ── 模組三-7：收盤價 > MA20 > MA60 ───────────────────────────────────────────
def sc_ma_bullish_alignment(sid):
    try:
        hist = yf.Ticker(f"{sid}.TW").history(period="100d")
        if hist.empty or len(hist) < 60:
            return False, f"K線資料不足({len(hist)}天)", {}
        close = hist["Close"]
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        curr_close = float(close.iloc[-1])
        curr_ma20  = float(ma20.iloc[-1])
        curr_ma60  = float(ma60.iloc[-1])
        passed = (curr_close > curr_ma20) and (curr_ma20 > curr_ma60)
        raw = {"收盤價": round(curr_close, 2), "MA20": round(curr_ma20, 2), "MA60": round(curr_ma60, 2)}
        return passed, f"收盤{curr_close:.2f} / MA20={curr_ma20:.2f} / MA60={curr_ma60:.2f}", raw
    except Exception as e:
        return False, f"抓取失敗:{e}", {}

# ── 模組三-8：成交量 > 5日均量 × 1.5 ─────────────────────────────────────────
def sc_volume_breakout(sid):
    try:
        hist = yf.Ticker(f"{sid}.TW").history(period="20d")
        if hist.empty or len(hist) < 6:
            return False, f"成交量資料不足({len(hist)}天)", {}
        vol = hist["Volume"]
        curr_vol = float(vol.iloc[-1])
        ma5_vol_prior = float(vol.iloc[-6:-1].mean())  # 不含當日的前5日均量
        if ma5_vol_prior == 0:
            return False, "前5日均量為零", {}
        ratio = curr_vol / ma5_vol_prior
        passed = ratio > 1.5
        raw = {"當日成交量": int(curr_vol), "前5日均量": int(ma5_vol_prior), "倍數": round(ratio, 2)}
        return passed, f"當日量{int(curr_vol):,} / 前5日均量{int(ma5_vol_prior):,} = {ratio:.2f}倍（門檻1.5倍）", raw
    except Exception as e:
        return False, f"抓取失敗:{e}", {}

# ==============================================================================
# 單檔股票完整 8 條件掃描
# ==============================================================================
def sc_screen_one_stock(sid, name):
    end_date   = datetime.now().strftime("%Y-%m-%d")
    start_long = (datetime.now() - timedelta(days=750)).strftime("%Y-%m-%d")
    start_rev  = (datetime.now() - timedelta(days=480)).strftime("%Y-%m-%d")
    start_chip = (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d")

    row = {"代號": sid, "公司": name}
    raw_all = {}

    ok1, n1, r1 = sc_revenue_yoy_above20(sid, start_rev, end_date)
    row["營收YoY>20%"], row["營收YoY>20%_說明"] = ok1, n1
    raw_all["營收YoY20"] = r1

    ok2, n2, r2 = sc_revenue_3m_avg_yoy_positive(sid, start_rev, end_date)
    row["近3月均YoY>0"], row["近3月均YoY>0_說明"] = ok2, n2
    raw_all["近3月均YoY"] = r2

    ok3, n3, r3 = sc_opex_yoy_above5(sid, start_long, end_date)
    row["營業費用YoY>5%"], row["營業費用YoY>5%_說明"] = ok3, n3
    raw_all["營業費用YoY"] = r3

    ok4, n4, r4 = sc_contract_liability_qoq_positive(sid, start_long, end_date)
    row["合約負債季增>0"], row["合約負債季增>0_說明"] = ok4, n4
    raw_all["合約負債QoQ"] = r4

    ok5, n5, r5 = sc_big_holder_above50_increasing(sid, start_long, end_date)
    row["千張大戶>50%增"], row["千張大戶>50%增_說明"] = ok5, n5
    raw_all["千張大戶"] = r5

    ok6, n6, r6 = sc_foreign_5day_consecutive_buy(sid, start_chip, end_date)
    row["外資連5日買超"], row["外資連5日買超_說明"] = ok6, n6
    raw_all["外資連買"] = r6

    ok7, n7, r7 = sc_ma_bullish_alignment(sid)
    row["收盤>MA20>MA60"], row["收盤>MA20>MA60_說明"] = ok7, n7
    raw_all["均線排列"] = r7

    ok8, n8, r8 = sc_volume_breakout(sid)
    row["爆量>1.5倍"], row["爆量>1.5倍_說明"] = ok8, n8
    raw_all["爆量"] = r8

    row["符合項數"] = sum([ok1, ok2, ok3, ok4, ok5, ok6, ok7, ok8])
    row["_raw"] = raw_all
    return row

def sc_run_screen_with_progress(stock_db):
    results   = []
    stocks    = list(stock_db.items())
    total     = len(stocks)
    prog_bar  = st.progress(0, text="準備開始掃描...")
    log_box   = st.empty()
    log_lines = []
    nl = chr(10)

    for i, (sid, name) in enumerate(stocks):
        prog_bar.progress((i + 1) / total, text=f"掃描中 {i+1}/{total}：{name}({sid})")
        row = sc_screen_one_stock(sid, name)
        icons = "".join([
            ("📈" if row["營收YoY>20%"] else "⚫"),
            ("📊" if row["近3月均YoY>0"] else "⚫"),
            ("🔬" if row["營業費用YoY>5%"] else "⚫"),
            ("📋" if row["合約負債季增>0"] else "⚫"),
            ("🐋" if row["千張大戶>50%增"] else "⚫"),
            ("💰" if row["外資連5日買超"] else "⚫"),
            ("🟢" if row["收盤>MA20>MA60"] else "⚫"),
            ("🔥" if row["爆量>1.5倍"] else "⚫"),
        ])
        line = f"{icons} {name}({sid}) → {row['符合項數']}/8 項"
        log_lines.append(line)
        if len(log_lines) > 14:
            log_lines = log_lines[-14:]
        log_box.code(nl.join(log_lines), language=None)
        results.append(row)

    prog_bar.progress(1.0, text=f"✅ 掃描完成！共 {total} 檔")
    log_box.empty()
    return pd.DataFrame(results)

# ==============================================================================
# 介面：批次選擇 + 執行
# ==============================================================================
SC_BATCH_SIZE = 300
sc_all_items = list(ELECTRONIC_STOCK_DB.items())
sc_n_batches = (len(sc_all_items) + SC_BATCH_SIZE - 1) // SC_BATCH_SIZE

st.markdown("#### 📦 選股中心｜分批掃描設定（每批 300 檔）")
sc_batch_options = []
for b in range(sc_n_batches):
    s_i = b * SC_BATCH_SIZE
    e_i = min(s_i + SC_BATCH_SIZE, len(sc_all_items))
    sc_batch_options.append(f"第 {b+1} 批（{s_i+1}-{e_i}檔，代號 {sc_all_items[s_i][0]}~{sc_all_items[e_i-1][0]}）")

sc_col_batch, sc_col_run, sc_col_clear, sc_col_min = st.columns([2.2, 1, 1, 1])
with sc_col_batch:
    sc_selected_label = st.selectbox("選擇要掃描的批次", sc_batch_options, key="sc_batch_select")
sc_selected_idx = sc_batch_options.index(sc_selected_label)

with sc_col_run:
    sc_do_run = st.button("🚀 執行本批選股", type="primary", use_container_width=True, key="sc_run_btn")
with sc_col_clear:
    sc_do_clear = st.button("🔄 清除本批結果", use_container_width=True, key="sc_clear_btn")
with sc_col_min:
    sc_min_cond = st.number_input("最低符合項數", min_value=1, max_value=8, value=5, step=1, key="sc_min_cond")

sc_session_key = f"sc_screen_df_batch_{sc_selected_idx}"

if sc_do_clear:
    if sc_session_key in st.session_state:
        del st.session_state[sc_session_key]
    st.rerun()

if sc_do_run:
    s_i = sc_selected_idx * SC_BATCH_SIZE
    e_i = min(s_i + SC_BATCH_SIZE, len(sc_all_items))
    sc_batch_db = dict(sc_all_items[s_i:e_i])
    df_sc_result = sc_run_screen_with_progress(sc_batch_db)
    st.session_state[sc_session_key] = df_sc_result

df_sc_all = st.session_state.get(sc_session_key, pd.DataFrame())

if df_sc_all.empty:
    st.warning(f"⚠️ 尚未掃描「{sc_selected_label}」。點擊「🚀 執行本批選股」開始（每批約需 2-5 分鐘，因含技術指標+籌碼+財報多重 API 呼叫）。")
else:
    df_sc_pass = df_sc_all[df_sc_all["符合項數"] >= sc_min_cond].sort_values(
        "符合項數", ascending=False).reset_index(drop=True)

    sc_total = len(df_sc_all)
    sc_pass  = len(df_sc_pass)
    sc_cnt8  = len(df_sc_all[df_sc_all["符合項數"] == 8])
    sc_cnt7  = len(df_sc_all[df_sc_all["符合項數"] == 7])
    sc_cnt6  = len(df_sc_all[df_sc_all["符合項數"] == 6])
    sc_cnt5  = len(df_sc_all[df_sc_all["符合項數"] == 5])

    n1c, n2c, n3c, n4c, n5c, n6c = st.columns(6)
    with n1c: st.metric("📦 本批掃描", f"{sc_total} 檔")
    with n2c: st.metric(f"✅ 符合≥{sc_min_cond}", f"{sc_pass} 檔")
    with n3c: st.metric("5項", f"{sc_cnt5}")
    with n4c: st.metric("6項", f"{sc_cnt6}")
    with n5c: st.metric("7項", f"{sc_cnt7}")
    with n6c: st.metric("👑8項全中", f"{sc_cnt8}")

    st.markdown("---")

    # ── 完整原始數值明細表（所有股票，全部數值）──
    st.markdown("#### 📋 完整原始數值明細（本批所有股票，8 項條件全部數值）")
    sc_detail_rows = []
    for _, r in df_sc_all.iterrows():
        raw = r["_raw"]
        d1 = raw.get("營收YoY20", {}) or {}
        d2 = raw.get("近3月均YoY", {}) or {}
        d3 = raw.get("營業費用YoY", {}) or {}
        d4 = raw.get("合約負債QoQ", {}) or {}
        d5 = raw.get("千張大戶", {}) or {}
        d6 = raw.get("外資連買", {}) or {}
        d7 = raw.get("均線排列", {}) or {}
        d8 = raw.get("爆量", {}) or {}

        sc_detail_rows.append({
            "代號": r["代號"], "公司": r["公司"], "符合項數": f"{int(r['符合項數'])}/8",
            "📈YoY最新%": d1.get("YoY%"), "📈最新月營收(千元)": d1.get("最新月營收(千元)"),
            "📈去年同月營收(千元)": d1.get("去年同月營收(千元)"), "📈通過": "✅" if r["營收YoY>20%"] else "❌",
            "📊近3月均YoY%": d2.get("近3月平均YoY%"), "📊通過": "✅" if r["近3月均YoY>0"] else "❌",
            "🔬營業費用YoY%": d3.get("YoY%"), "🔬最新季營業費用(千元)": d3.get("最新季營業費用(千元)"),
            "🔬去年同季營業費用(千元)": d3.get("去年同季營業費用(千元)"), "🔬通過": "✅" if r["營業費用YoY>5%"] else "❌",
            "📋合約負債季增%": d4.get("季增率%"), "📋最新季合約負債(千元)": d4.get("最新季合約負債(千元)"),
            "📋前季合約負債(千元)": d4.get("前季合約負債(千元)"), "📋通過": "✅" if r["合約負債季增>0"] else "❌",
            "🐋千張大戶最新%": d5.get("最新千張大戶持股%"), "🐋千張大戶前期%": d5.get("前期千張大戶持股%"),
            "🐋變化%": d5.get("變化%"), "🐋通過": "✅" if r["千張大戶>50%增"] else "❌",
            "💰外資連買說明": r["外資連5日買超_說明"], "💰通過": "✅" if r["外資連5日買超"] else "❌",
            "🟢收盤價": d7.get("收盤價"), "🟢MA20": d7.get("MA20"), "🟢MA60": d7.get("MA60"),
            "🟢通過": "✅" if r["收盤>MA20>MA60"] else "❌",
            "🔥當日成交量": d8.get("當日成交量"), "🔥前5日均量": d8.get("前5日均量"), "🔥倍數": d8.get("倍數"),
            "🔥通過": "✅" if r["爆量>1.5倍"] else "❌",
        })
    df_sc_detail_full = pd.DataFrame(sc_detail_rows)
    st.dataframe(df_sc_detail_full, use_container_width=True, hide_index=True, height=450)

    sc_csv_full = df_sc_detail_full.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 下載本批完整數值 CSV", sc_csv_full,
                       f"strategy_full_values_batch{sc_selected_idx+1}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                       "text/csv", key="sc_dl_full")

    st.markdown("---")

    # ── 符合名單 ──
    if df_sc_pass.empty:
        st.warning(f"⚠️ 本批中無股票符合 ≥{sc_min_cond} 項條件，可調低門檻或切換批次。")
    else:
        st.markdown(f"#### 🏆 本批符合 ≥{sc_min_cond} 項複合策略 — 共 **{sc_pass}** 檔")

        sc_pass_rows = []
        for _, r in df_sc_pass.iterrows():
            sc_pass_rows.append({
                "代號": r["代號"], "公司": r["公司"],
                "符合項數": f"{'⭐'*int(r['符合項數'])} {int(r['符合項數'])}/8",
                "📈營收YoY>20%": ("✅ " if r["營收YoY>20%"] else "❌ ") + str(r["營收YoY>20%_說明"]),
                "📊近3月均YoY>0": ("✅ " if r["近3月均YoY>0"] else "❌ ") + str(r["近3月均YoY>0_說明"]),
                "🔬營業費用YoY>5%": ("✅ " if r["營業費用YoY>5%"] else "❌ ") + str(r["營業費用YoY>5%_說明"]),
                "📋合約負債季增>0": ("✅ " if r["合約負債季增>0"] else "❌ ") + str(r["合約負債季增>0_說明"]),
                "🐋千張大戶>50%增": ("✅ " if r["千張大戶>50%增"] else "❌ ") + str(r["千張大戶>50%增_說明"]),
                "💰外資連5日買超": ("✅ " if r["外資連5日買超"] else "❌ ") + str(r["外資連5日買超_說明"]),
                "🟢收盤>MA20>MA60": ("✅ " if r["收盤>MA20>MA60"] else "❌ ") + str(r["收盤>MA20>MA60_說明"]),
                "🔥爆量>1.5倍": ("✅ " if r["爆量>1.5倍"] else "❌ ") + str(r["爆量>1.5倍_說明"]),
            })
        df_sc_pass_show = pd.DataFrame(sc_pass_rows)
        st.dataframe(df_sc_pass_show, use_container_width=True, hide_index=True)

        sc_fig = go.Figure(go.Bar(
            y=df_sc_pass["公司"]+"("+df_sc_pass["代號"]+")",
            x=df_sc_pass["符合項數"].astype(int),
            orientation="h",
            marker_color=["#ff4b4b" if x>=7 else ("#ff8c42" if x==6 else "#f5a623")
                          for x in df_sc_pass["符合項數"].astype(int)],
            text=df_sc_pass["符合項數"].astype(int).apply(lambda x: f"{x}/8"),
            textposition="auto"
        ))
        sc_fig.update_layout(height=max(280, len(df_sc_pass)*26+60),
                              xaxis=dict(range=[0,8.5], tickvals=list(range(1,9))),
                              margin=dict(l=10,r=10,t=30,b=10), title="本批符合策略股票排行")
        st.plotly_chart(sc_fig, use_container_width=True, key=f"sc_pass_bar_{sc_selected_idx}")

        sc_csv_pass = df_sc_pass_show.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("📥 下載符合名單 CSV", sc_csv_pass,
                           f"strategy_pass_batch{sc_selected_idx+1}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                           "text/csv", key="sc_dl_pass")

        st.markdown("#### 📊 本批各條件通過率")
        sc_cond_cols  = ["營收YoY>20%","近3月均YoY>0","營業費用YoY>5%","合約負債季增>0",
                          "千張大戶>50%增","外資連5日買超","收盤>MA20>MA60","爆量>1.5倍"]
        sc_cond_names = ["📈營收YoY20%","📊近3月均YoY","🔬營業費用YoY5%","📋合約負債季增",
                          "🐋千張大戶50%","💰外資連買5日","🟢均線多排","🔥爆量1.5倍"]
        sc_cond_vals  = [int(df_sc_all[c].sum()) for c in sc_cond_cols]
        sc_cond_pcts  = [v/sc_total*100 for v in sc_cond_vals]
        sc_fig_ov = go.Figure(go.Bar(
            x=sc_cond_names, y=sc_cond_pcts,
            marker_color=["#ff4b4b","#ff8c42","#4b9eff","#f5a623","#9b5de5","#f15bb5","#00c49f","#06d6a0"],
            text=[f"{v}檔({p:.1f}%)" for v,p in zip(sc_cond_vals, sc_cond_pcts)],
            textposition="auto"
        ))
        sc_fig_ov.update_layout(height=300, yaxis=dict(range=[0,100], title="通過率 (%)"),
                                 margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(sc_fig_ov, use_container_width=True, key=f"sc_ov_bar_{sc_selected_idx}")

st.markdown(
    "<small>⚠️ 千張大戶與合約負債資料依 FinMind 財報/籌碼公告頻率更新，可能有數日至數週延遲；"
    "技術指標(MA/成交量)為最新交易日資料。本策略僅供量化篩選參考，不構成投資建議。</small>",
    unsafe_allow_html=True
)

# ==============================================================================
# 十三、網頁定時自動循環刷新機制
# ==============================================================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
