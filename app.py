import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from auth import register_user, login_user, logout

# ---------------- Cấu hình trang ----------------
st.set_page_config(
    page_title="Akademy Kong Kong",
    page_icon="🏛️",
    layout="wide"
)

# ---------------- Khởi tạo session ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# ---------------- Giao diện Đăng nhập/Đăng ký ----------------
def auth_page():
    st.title("🏛️ HỌC VIỆN KONG-KONG")
    st.subheader("Thông Tin Thị Trường")
    
    tab_login, tab_register = st.tabs(["🔐 Đăng Nhập", "📝 Đăng Ký"])
    
    with tab_login:
        st.subheader("Đăng nhập tài khoản")
        login_input = st.text_input("📧 Email hoặc Số điện thoại", key="login_input")
        password = st.text_input("🔒 Mật khẩu đăng nhập", type="password", key="login_password")
        
        if st.button("Đăng Nhập", use_container_width=True, key="btn_login"):
            if not login_input or not password:
                st.error("Vui lòng điền đầy đủ thông tin!")
            else:
                success, email, user = login_user(login_input, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_info = user
                    st.success(f"👋 Xin chào {user['fullname']}! Đăng nhập thành công...")
                    st.rerun()
                else:
                    st.error("❌ Thông tin đăng nhập không chính xác!")
    
    with tab_register:
        st.subheader("Tạo tài khoản mới")
        fullname = st.text_input("👤 Họ và tên", key="reg_fullname")
        email = st.text_input("📧 Email", key="reg_email")
        phone = st.text_input("📱 Số điện thoại", key="reg_phone")
        reg_password = st.text_input("🔒 Tạo mật khẩu", type="password", key="reg_password")
        confirm_pass = st.text_input("🔒 Xác nhận mật khẩu", type="password", key="reg_confirm")
        
        if st.button("Đăng Ký", use_container_width=True, key="btn_register"):
            if not fullname or not email or not phone or not reg_password:
                st.error("Vui lòng điền đầy đủ thông tin!")
            elif reg_password != confirm_pass:
                st.error("❌ Mật khẩu không khớp!")
            else:
                success, msg = register_user(fullname, email, phone, reg_password)
                if success:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

# ---------------- Giao diện chính sau đăng nhập ----------------
def main_app():
    user = st.session_state.user_info
    st.title("🏛️ Akademy Kong Kong")
    st.subheader("Thông Tin Thị Trường")
    
    # Thông tin người dùng & nút đăng xuất
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.info(f"👋 Xin chào, **{user['fullname']}** | 📧 {st.session_state.user_email}")
    with col3:
        if st.button("🚪 Đăng Xuất", use_container_width=True):
            logout()
    
    st.warning("⚠️ Dữ liệu chỉ tham khảo, có độ trễ. Không phải lời khuyên đầu tư nhé!")
    
    # Nhập mã chứng khoán
    ticker = st.text_input("Nhập mã chứng khoán", value="AAPL")
    
    # Chọn khung thời gian
    time_range = st.selectbox(
        "Khung thời gian",
        ["1 tháng", "3 tháng", "6 tháng", "1 năm", "Tất cả"]
    )
    
    range_map = {
        "1 tháng": "1mo",
        "3 tháng": "3mo",
        "6 tháng": "6mo",
        "1 năm": "1y",
        "Tất cả": "max"
    }
    period = range_map[time_range]
    
    if ticker:
        try:
            # Lấy dữ liệu
            data = yf.Ticker(ticker)
            hist = data.history(period=period)
            
            if hist.empty:
                st.error("❌ Không tìm thấy dữ liệu cho mã này!")
                return
            
            # Tính các chỉ báo
            hist["MA20"] = hist["Close"].rolling(window=20).mean()
            hist["MA50"] = hist["Close"].rolling(window=50).mean()
            
            # Giá hiện tại
            current_price = round(hist["Close"].iloc[-1], 2)
            price_change = round((hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100, 2)
            
            st.metric("Giá hiện tại", f"{current_price}", f"{price_change}%")
            
            # Vẽ biểu đồ nến
            fig = go.Figure()
            
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"],
                name="Giá",
                increasing_line_color="green",
                decreasing_line_color="red"
            ))
            
            fig.add_trace(go.Scatter(x=hist.index, y=hist["MA20"], name="MA20", line=dict(color="gold", width=1.5)))
            fig.add_trace(go.Scatter(x=hist.index, y=hist["MA50"], name="MA50", line=dict(color="blue", width=1.5)))
            
            fig.update_layout(
                title=f"Biểu đồ giá - {ticker}",
                xaxis_title="Ngày",
                yaxis_title="Giá",
                template="plotly_dark",
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # RSI
            st.subheader("📊 Chỉ báo RSI")
            delta = hist["Close"].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist["RSI"] = 100 - (100 / (1 + rs))
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=hist.index, y=hist["RSI"], name="RSI", line=dict(color="cyan")))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="70 - Bán quá mua")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="30 - Mua quá bán")
            fig_rsi.update_layout(template="plotly_dark", title="Chỉ số RSI")
            st.plotly_chart(fig_rsi, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Lỗi: {str(e)}")

# ---------------- Chạy ứng dụng ----------------
if __name__ == "__main__":
    if st.session_state.logged_in:
        main_app()
    else:
        auth_page()
