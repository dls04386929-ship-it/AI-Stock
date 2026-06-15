import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time
import plotly.graph_objects as go

# 設定網頁標題與寬度配置
st.set_page_config(page_title="美日韓 AI 龍頭股即時看板", layout="wide")

st.title("🌍 美日韓 AI 龍頭股即時動態儀表板")
st.markdown("本系統使用 Yahoo Finance API 進行跨國市場數據與匯率的即時監控。")

# 建立側邊欄設定
st.sidebar.header("🔄 控制面板")
refresh_interval = st.sidebar.slider("自動重新整理頻率 (秒)", min_value=5, max_value=60, value=10)
auto_refresh = st.sidebar.checkbox("啟用自動重新整理", value=True)

# 定義美、日、韓 AI 龍頭股清單
stock_config = {
    'NVDA': {'name': 'NVIDIA', 'market': '美股', 'currency': 'USD'},
    'AMD': {'name': 'AMD', 'market': '美股', 'currency': 'USD'},
    'MSFT': {'name': 'Microsoft', 'market': '美股', 'currency': 'USD'},
    'GOOGL': {'name': 'Alphabet', 'market': '美股', 'currency': 'USD'},
    '8035.T': {'name': '東京威力科創', 'market': '日股', 'currency': 'JPY'},
    '6857.T': {'name': 'Advantest', 'market': '日股', 'currency': 'JPY'},
    '9984.T': {'name': '軟銀集團', 'market': '日股', 'currency': 'JPY'},
    '005930.KS': {'name': '三星電子', 'market': '韓股', 'currency': 'KRW'},
    '000660.KS': {'name': 'SK 海力士', 'market': '韓股', 'currency': 'KRW'}
}

def get_data():
    # 獲取即時匯率
    try:
        forex = yf.download(['USDTWD=X', 'JPYTWD=X', 'KRWTWD=X'], period='1d', interval='1m', progress=False)
        usd_to_twd = forex['Close']['USDTWD=X'].iloc[-1]
        jpy_to_twd = forex['Close']['JPYTWD=X'].iloc[-1]
        krw_to_twd = forex['Close']['KRWTWD=X'].iloc[-1]
    except Exception:
        usd_to_twd, jpy_to_twd, krw_to_twd = 32.5, 0.21, 0.024

    rates = {'USD': usd_to_twd, 'JPY': jpy_to_twd, 'KRW': krw_to_twd}

    # 批量下載股票數據
    tickers_list = list(stock_config.keys())
    data = yf.download(tickers_list, period='1d', interval='1m', progress=False)

    results = []
    for ticker in tickers_list:
        try:
            ticker_close = data['Close'][ticker].dropna()
            ticker_open = data['Open'][ticker].dropna()

            if not ticker_close.empty:
                current_price = ticker_close.iloc[-1]
                open_price = ticker_open.iloc[0] if not ticker_open.empty else current_price
                change_pct = ((current_price - open_price) / open_price) * 100
                
                currency = stock_config[ticker]['currency']
                price_twd = current_price * rates[currency]

                results.append({
                    '市場': stock_config[ticker]['market'],
                    '代號': ticker,
                    '公司名稱': stock_config[ticker]['name'],
                    '當前股價': current_price,
                    '幣別': currency,
                    '今日漲跌幅': change_pct,
                    '換算台幣 (TWD)': price_twd
                })
        except Exception:
            pass
            
    df = pd.DataFrame(results)
    return df, rates

# 獲取資料
df_market, current_rates = get_data()

# 顯示參考匯率資訊卡
st.markdown("### 💱 參考匯率 (基準：TWD)")
cols_rates = st.columns(3)
cols_rates[0].metric("美元 / 台幣 (USD/TWD)", f"{current_rates['USD']:.2f}")
cols_rates[1].metric("日圓 / 台幣 (JPY/TWD)", f"{current_rates['JPY']:.4f}")
cols_rates[2].metric("韓元 / 台幣 (KRW/TWD)", f"{current_rates['KRW']:.4f}")

st.markdown("---")

# 顯示最吸金/跌幅最重區塊 (Market Overview Metrics)
if not df_market.empty:
    st.markdown("### 🚀 今日表現焦點")
    df_sorted = df_market.sort_values(by='今日漲跌幅', ascending=False)
    top_performer = df_sorted.iloc[0]
    worst_performer = df_sorted.iloc[-1]
    
    col_focus1, col_focus2 = st.columns(2)
    with col_focus1:
        st.success(f"📈 領漲龍頭：{top_performer['公司名稱']} ({top_performer['代號']})")
        st.metric(label="漲跌幅", value=f"{top_performer['今日漲跌幅']:+.2f}%", delta=f"{top_performer['今日漲跌幅']:+.2f}%")
    with col_focus2:
        st.error(f"📉 領跌弱勢：{worst_performer['公司名稱']} ({worst_performer['代號']})")
        st.metric(label="漲跌幅", value=f"{worst_performer['今日漲跌幅']:+.2f}%", delta=f"{worst_performer['今日漲跌幅']:+.2f}%")

st.markdown("---")

# 顯示主資料表格
st.markdown(f"### 📊 即時行情看板 (最後更新: {datetime.now().strftime('%H:%M:%S')})")

# 格式化輸出 DataFrame
df_display = df_market.copy()
df_display['當前股價'] = df_display.apply(lambda r: f"{r['當前股價']:,.2f} {r['幣別']}", axis=1)
df_display['今日漲跌幅'] = df_display['今日漲跌幅'].apply(lambda x: f"{x:+.2f}%")
df_display['換算台幣 (TWD)'] = df_display['換算台幣 (TWD)'].apply(lambda x: f"${x:,.1f} 元")
df_display = df_display.drop(columns=['幣別']).sort_values(by='市場')

st.dataframe(df_display, use_container_width=True, hide_index=True)

# 繪製視覺化圖表
if not df_market.empty:
    st.markdown("### 📈 跨國 AI 股今日漲跌幅橫向評比")
    df_chart = df_market.sort_values(by='今日漲跌幅', ascending=True)
    
    # 根據漲跌給予顏色
    colors = ['#g7717d' if x < 0 else '#5cc985' for x in df_chart['今日漲跌幅']]
    
    fig = go.Figure(go.Bar(
        x=df_chart['今日漲跌幅'],
        y=df_chart['公司名稱'] + " (" + df_chart['市場'] + ")",
        orientation='h',
        marker_color=['#ff4b4b' if x < 0 else '#00f574' for x in df_chart['今日漲跌幅']]
    ))
    fig.update_layout(
        xaxis_title="漲跌幅 (%)",
        yaxis_title="企業",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# 處理自動重新整理邏輯
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
