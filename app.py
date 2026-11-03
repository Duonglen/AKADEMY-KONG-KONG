import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Akademy Kong Kong", layout="wide")

# ====== HEADER ======
st.title("🏛️ Akademy Kong Kong")
st.subheader("Thông Tin Thị Trường")
st.caption("*Tham khảo thông minh — Quyết định tự tin*")

st.info("⚠️ **Dữ liệu chỉ tham khảo, có độ trễ. Không phải lời khuyên đầu tư nhé!**")

# ====== TÌM KIẾM ======
ticker = st.text_input("Nhập mã chứng khoán", value="AAPL")
period = st.selectbox("Khung thời gian", ["1 tháng", "3 tháng", "6 tháng", "1 năm"])

map_p = {"1 tháng":"1mo", "3 tháng":"3mo", "6 tháng":"6mo", "1 năm":"1y"}

# ====== LẤY DỮ LIỆU ======
@st.cache_data(ttl=600)
def get_data(sym, p):
    try:
        df = yf.Ticker(sym).history(period=p)
        return df if not df.empty else None
    except:
        return None

with st.spinner("Đang tải dữ liệu..."):
    df = get_data(ticker, map_p[period])

if df is None:
    st.error("❌ Không tìm thấy dữ liệu. Kiểm tra lại mã nhé!")
    st.stop()

# ====== CHỈ SỐ TÓM TẮT ======
latest = df.iloc[-1]
prev = df.iloc[-2]
change = latest['Close'] - prev['Close']
pct = (change / prev['Close']) * 100

c1, c2, c3 = st.columns(3)
c1.metric("Giá hiện tại", f"{latest['Close']:.2f}", f"{pct:+.2f}%")
c2.metric("Cao nhất", f"{df['High'].max():.2f}")
c3.metric("Thấp nhất", f"{df['Low'].min():.2f}")

# ====== TÍNH CHỈ BÁO ======
df['MA20'] = df['Close'].rolling(20).mean()
df['MA50'] = df['Close'].rolling(50).mean()

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = calculate_rsi(df)

# ====== BIỂU ĐỒ NẾN ======
st.subheader("📊 Biểu đồ Nến")
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High,
                             low=df.Low, close=df.Close, name="Giá"))
fig.add_trace(go.Scatter(x=df.index, y=df.MA20, name="MA20", 
                         line=dict(color='orange', width=1)))
fig.add_trace(go.Scatter(x=df.index, y=df.MA50, name="MA50", 
                         line=dict(color='blue', width=1)))
fig.update_layout(xaxis_rangeslider_visible=False, height=500, template='plotly_white')
st.plotly_chart(fig, use_container_width=True)

# ====== BIỂU ĐỒ RSI ======
st.subheader("📉 Chỉ báo RSI")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df.index, y=df.RSI, name="RSI", 
                             line=dict(color='purple')))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(height=200, template='plotly_white')
st.plotly_chart(fig_rsi, use_container_width=True)

# ====== FOOTER ======
st.caption("🏛️ Akademy Kong Kong — Dữ liệu chỉ tham khảo, có độ trễ. Không phải lời khuyên đầu tư.")
