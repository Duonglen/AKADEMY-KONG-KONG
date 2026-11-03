import streamlit as st
import re
import json
import os
from datetime import datetime

DATA_FILE = "users_data.json"

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def is_valid_email(email):
    import re
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_valid_phone(phone):
    import re
    pattern = r"^(0|\+84)(\d{9,10})$"
    return re.match(pattern, phone) is not None

def register_user(fullname, email, phone, password):
    users = load_users()
    
    if email in users:
        return False, "Email này đã được đăng ký!"
    if phone in users:
        for e in users:
            if users[e]["phone"] == phone:
                return False, "Số điện thoại này đã được đăng ký!"
    if not is_valid_email(email):
        return False, "Email không hợp lệ!"
    if not is_valid_phone(phone):
        return False, "Số điện thoại không hợp lệ!"
    if len(password) < 6:
        return False, "Mật khẩu cần ít nhất 6 ký tự!"
    
    users[email] = {
        "fullname": fullname,
        "phone": phone,
        "password": password,
        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    save_users(users)
    return True, "Đăng ký thành công! Vui lòng đăng nhập."

def login_user(email_or_phone, password):
    users = load_users()
    
    # Tìm theo email trước
    if email_or_phone in users:
        user = users[email_or_phone]
        if user["password"] == password:
            return True, email_or_phone, user
        return False, None, None
    
    # Không tìm thấy email → tìm theo số điện thoại
    for e in users:
        if users[e]["phone"] == email_or_phone:
            if users[e]["password"] == password:
                return True, e, users[e]
            break
    
    return False, None, None

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
