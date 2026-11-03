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
