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
st.set_page_config(page_title="全球 AI & 衛星與台股輪動全自動決策終端", layout="wide")
st.title("🌍 全球 AI、低軌衛星與台股【板塊輪動追蹤全自動看盤系統】")
st.markdown("本系統全面整合：**操作紀律、全球總經、每日盤後籌碼、全球大盤、跨國產業鏈估值，並新增『板塊輪動自動統計』功能**。")

# FinMind API Token
FINMIND_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiZGxzMDQzODY5MjlAZ21haWwuY29tIiwiZW1haWwiOiJkbHMwNDM4NjkyOUBnbWFpbC5jb20iLCJ0b2tlbl92ZXJzaW9uIjowfQ.XLHUQWa0QglCBjukX374bWUWeVaFLfwHhBMrtOrZ-0E"

# 側邊欄控制面板
st.sidebar.header("🔄 系統主控制")
refresh_interval = st.sidebar.slider("動態資料重新整理頻率 (秒)", min_value=10, max_value=120, value=30)
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
# 二、全球每日核心關注列表
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
# 三、自動串接台灣本土財經 API 函數
# ==============================================================================
def get_backup_chips_data():
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

@st.cache_data(ttl=1800)
def fetch_tw_chip_data_automated():
    url = "https://api.finmindtrade.com/api/v4/data"
    target_date = datetime.now()
    if target_date.hour < 16:
        target_date = target_date - timedelta(days=1)
    date_str = target_date.strftime("%Y-%m-%d")
    
    parameter = {
        "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
        "data_id": "", "start_date": date_str, "end_date": date_str, "token": FINMIND_TOKEN
    }
    try:
        response = requests.get(url, params=parameter, timeout=10)
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
        else:
            return get_backup_chips_data()
    except:
        return get_backup_chips_data()

df_automated_buy, df_automated_sell, chip_date_info = fetch_tw_chip_data_automated()

st.markdown(f"### 🎯 每日盤後大戶資金流向統計 (API 全自動即時更新 | 數據基準日: {chip_date_info})")
col_buy, col_sell = st.columns(2)
with col_buy:
    st.success("🛒 盤後大戶買超 TOP 5 (資金流入主攻部隊)")
    st.dataframe(df_automated_buy, use_container_width=True, hide_index=True)
with col_sell:
    st.error("📉 盤後大戶賣超 TOP 5 (資金流出/防範調節)")
    st.dataframe(df_automated_sell, use_container_width=True, hide_index=True)
st.markdown("---")

# ==============================================================================
# 四、全球大盤與個股代號配置
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
        'NVDA': {'name': 'NVIDIA', 'nation': '美'}, 'AMD': {'name': 'AMD', 'nation': '美'},
        '2330.TW': {'name': '台積電', 'nation': '台'}, '005930.KS': {'name': '三星電子', 'nation': '韓'}
    },
    '被動元件聚落': {
        '2327.TW': {'name': '國巨', 'nation': '台'}, '2492.TW': {'name': '華新科', 'nation': '台'},
        '2375.TW': {'name': '凱美', 'nation': '台'}, '3026.TW': {'name': '禾伸堂', 'nation': '台'},
        '3090.TW': {'name': '日電貿', 'nation': '台'}, '2478.TW': {'name': '大毅', 'nation': '台'},
        '6173.TW': {'name': '信昌電', 'nation': '台'}, '6449.TW': {'name': '鈺邦', 'nation': '台'},
        '8042.TW': {'name': '金山電', 'nation': '台'}, '8043.TW': {'name': '蜜望實', 'nation': '台'},
        '6175.TW': {'name': '立敦', 'nation': '台'}, '3624.TW': {'name': '光頡', 'nation': '台'},
        '3236.TW': {'name': '千如', 'nation': '台'}, '5328.TW': {'name': '華容', 'nation': '台'},
        '6155.TW': {'name': '鈞寶', 'nation': '台'}, '8121.TW': {'name': '越峰', 'nation': '台'}
    },
    '半導體矽晶圓': {
        '6488.TW': {'name': '環球晶', 'nation': '台'}, '5483.TW': {'name': '中美晶', 'nation': '台'},
        '6182.TW': {'name': '合晶', 'nation': '台'}, '3532.TW': {'name': '台勝科', 'nation': '台'},
        '3016.TW': {'name': '嘉晶', 'nation': '台'}, '2338.TW': {'name': '光罩', 'nation': '台'},
        '6139.TW': {'name': '亞翔', 'nation': '台'}
    },
    '記憶體與IC設計': {
        '000660.KS': {'name': 'SK 海力士', 'nation': '韓'}, 'MU': {'name': '美光科技', 'nation': '美'},
        '2344.TW': {'name': '華邦電', 'nation': '台'}, '4973.TW': {'name': '廣穎', 'nation': '台'},
        '3035.TW': {'name': '智原', 'nation': '台'}, '4919.TW': {'name': '新唐', 'nation': '台'},
        '2401.TW': {'name': '凌陽', 'nation': '台'}, '8096.TW': {'name': '擎亞', 'nation': '台'}
    },
    '光學鏡頭與光通訊': {
        '3008.TW': {'name': '大立光', 'nation': '台'}, '3406.TW': {'name': '玉晶光', 'nation': '台'},
        '3362.TW': {'name': '先進光', 'nation': '台'}, '4979.TW': {'name': '華星光', 'nation': '台'},
        'MRVL': {'name': 'Marvell', 'nation': '美'}, '2454.TW': {'name': '聯發科', 'nation': '台'},
        '4977.TW': {'name': '眾達-KY', 'nation': '台'}
    },
    'PCB與電子材料': {
        '1303.TW': {'name': '南亞', 'nation': '台'}, '1714.TW': {'name': '和桐', 'nation': '台'},
        '6274.TW': {'name': '台耀', 'nation': '台'}, '6153.TW': {'name': '嘉聯益', 'nation': '台'},
        '6191.TW': {'name': '精成科', 'nation': '台'}, '2484.TW': {'name': '希華', 'nation': '台'}
    },
    '低軌衛星設備': {
        'LHX': {'name': 'L3Harris', 'nation': '美'}, '6285.TW': {'name': '啟碁科技', 'nation': '台'},
        '2314.TW': {'name': '台揚科技', 'nation': '台'}, '3491.TW': {'name': '昇達科', 'nation': '台'}
    }
}

# ==============================================================================
# 五、動態數據同步與【輪動大數據量化統計邏輯】
# ==============================================================================
@st.cache_data(ttl=15)
def fetch_and_calculate_rotation_data():
    index_tickers = list(INDEX_CONFIG.keys())
    all_stock_tickers = []
    for s in STOCK_CONFIG.values():
        all_stock_tickers.extend(s.keys())
    all_stock_tickers = list(set(all_stock_tickers))
    
    # 同步下載全球市場數據
    idx_data = yf.download(index_tickers, period='2d', interval='1m', progress=False)
    stock_data = yf.download(all_stock_tickers, period='1d', interval='1m', progress=False)
    
    # 處理大盤
    index_results = []
    for t in index_tickers:
        try:
            close_s = idx_data['Close'][t].dropna()
            if not close_s.empty:
                index_results.append({
                    '項目': INDEX_CONFIG[t]['name'], '型態': INDEX_CONFIG[t]['type'],
                    '當前點數': f"{close_s.iloc[-1]:,.2f}", '今日漲跌幅': ((close_s.iloc[-1] - close_s.iloc[0]) / close_s.iloc[0]) * 100
                })
        except: pass

    # 處理個股與族群輪動統計
    stock_results = []
    rotation_summary = []
    
    for group, stocks in STOCK_CONFIG.items():
        group_changes = []
        up_count = 0
        total_count = 0
        
        for t, info in stocks.items():
            try:
                close_s = stock_data['Close'][t].dropna()
                open_s = stock_data['Open'][t].dropna()
                if not close_s.empty:
                    curr = close_s.iloc[-1]
                    op = open_s.iloc[0] if not open_s.empty else curr
                    pct = ((curr - op) / op) * 100 if op != 0 else 0.0
                    
                    group_changes.append(pct)
                    total_count += 1
                    if pct > 0: up_count += 1
                    
                    # 獲取法人財務數據
                    t_obj = yf.Ticker(t)
                    t_info = t_obj.info
                    
                    stock_results.append({
                        '產業分組': group, '國家': info['nation'], '代號': t, '公司名稱': info['name'],
                        '當前股價': curr, '幣別': t_info.get('currency', ''), '今日漲跌幅': pct,
                        '法人預估本益比 (Forward PE)': t_info.get('forwardPE', None), '法人預估明年 EPS': t_info.get('forwardEps', None)
                    })
            except: pass
            
        # 計算群組平均指標 (即時輪動核心)
        if group_changes:
            avg_pct = sum(group_changes) / len(group_changes)
            up_ratio = (up_count / total_count) * 100 if total_count > 0 else 0
            rotation_summary.append({
                '族群': group,
                '平均漲跌幅': avg_pct,
                '上漲家數比': f"{up_count}/{total_count} ({up_ratio:.0f}%)"
            })
            
    return pd.DataFrame(index_results), pd.DataFrame(stock_results), pd.DataFrame(rotation_summary)

# 執行同步運算
with st.spinner('正在計算台股各大強勢板塊即時資金輪動動向...'):
    df_index, df_stocks, df_rotation = fetch_and_calculate_rotation_data()

# ==============================================================================
# 六、【新亮點呈現】今日台股資金輪動強弱榜 (直接顯示在最上層面板)
# ==============================================================================
st.markdown("### 🔥 今日台股主流資金輪動強弱榜 (即時量化統計)")
if not df_rotation.empty:
    # 按照平均漲跌幅排序，抓出多頭與空頭領頭羊
    df_rotation_sorted = df_rotation.sort_values(by='平均漲跌幅', ascending=False)
    
    col_lead1, col_lead2, col_lead3 = st.columns(3)
    with col_lead1:
        st.metric(
            label=f"🥇 今日多頭總司令：{df_rotation_sorted.iloc[0]['族群']}",
            value=f"{df_rotation_sorted.iloc[0]['平均漲跌幅']:+.2f}%",
            delta=f"上漲比例 {df_rotation_sorted.iloc[0]['上漲家數比']}"
        )
    with col_lead2:
        st.metric(
            label=f"🥈 次強主流板塊：{df_rotation_sorted.iloc[1]['族群']}",
            value=f"{df_rotation_sorted.iloc[1]['平均漲跌幅']:+.2f}%",
            delta=f"上漲比例 {df_rotation_sorted.iloc[1]['上漲家數比']}"
        )
    with col_lead3:
        # 顯示最後一名，防範弱勢族群
        st.metric(
            label=f"⚠️ 今日相對弱勢族群：{df_rotation_sorted.iloc[-1]['族群']}",
            value=f"{df_rotation_sorted.iloc[-1]['平均漲跌幅']:+.2f}%",
            delta=f"上漲比例 {df_rotation_sorted.iloc[-1]['上漲家數比']}",
            delta_color="inverse"
        )
        
    # 繪製產業輪動橫向直觀長條圖
    fig_rot = go.Figure(go.Bar(
        y=df_rotation_sorted['族群'],
        x=df_rotation_sorted['平均漲跌幅'],
        orientation='h',
        marker_color=['#00f574' if x >= 0 else '#ff4b4b' for x in df_rotation_sorted['平均漲跌幅']]
    ))
    fig_rot.update_layout(
        xaxis_title="族群平均漲跌幅 (%)", yaxis_title="關注產業聚落",
        height=280, margin=dict(l=20, r=20, t=10, b=10)
    )
    st.plotly_chart(fig_rot, use_container_width=True, key="industry_rotation_chart")
else:
    st.warning("暫時無法取得輪動統計數據。")

st.markdown("---")

# ==============================================================================
# 七、全球主要大盤與個股分頁呈現
# ==============================================================================
st.markdown("### 📊 全球主要大盤 & 台指夜盤即時監控")
if not df_index.empty:
    cols = st.columns(len(df_index))
    for idx, row in df_index.iterrows():
        with cols[idx]:
            st.metric(label=f"{row['型態']} | {row['項目']}", value=row['當前點數'], delta=f"{row['今日漲跌幅']:+.2f}%")
st.markdown("---")

st.markdown(f"### 🚀 全球 AI & 低軌衛星暨台股強勢板塊鏈觀測站 (系統刷新時間: {datetime.now().strftime('%H:%M:%S')})")
if not df_stocks.empty:
    categories = list(STOCK_CONFIG.keys())
    tabs = st.tabs(categories)
    for i, cat in enumerate(categories):
        with tabs[i]:
            st.markdown(f"#### 🎯 當前關注群組：{cat}")
            df_sub = df_stocks[df_stocks['產業分組'] == cat].copy()
            
            df_display = df_sub.copy()
            df_display['當前股價'] = df_display.apply(lambda r: f"{r['當前股價']:,.2f} {r['幣別']}" if r['當前股價'] > 0 else "未開盤", axis=1)
            df_display['今日漲跌幅'] = df_display['今日漲跌幅'].apply(lambda x: f"{x:+.2f}%")
            df_display['法人預估本益比 (Forward PE)'] = df_display['法人預估本益比 (Forward PE)'].apply(lambda x: f"{x:.2f} 倍" if pd.notnull(x) else "無資料")
            df_display['法人預估明年 EPS'] = df_display['法人預估明年 EPS'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "無資料")
            
            df_display = df_display.drop(columns=['產業分組', '幣別'])
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            fig = go.Figure(go.Bar(
                x=df_sub['公司名稱'] + " (" + df_sub['國家'] + ")", y=df_sub['今日漲跌幅'],
                marker_color=['#ff4b4b' if x < 0 else '#00f574' for x in df_sub['今日漲跌幅']]
            ))
            fig.update_layout(yaxis_title="今日漲跌幅 (%)", xaxis_title="企業成員", height=280, margin=dict(l=20, r=20, t=15, b=15))
            st.plotly_chart(fig, use_container_width=True, key=f"chart_rot_group_{i}")

# ==============================================================================
# 八、網頁定時自動循環刷新機制
# ==============================================================================
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
