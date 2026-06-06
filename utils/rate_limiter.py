"""
速率限制器 — 防 DDOS / 惡意高頻攻擊
規格書允許：
  - 最多 1 秒延遲
  - 每則訊息最多 50 個字元
"""
import time
import streamlit as st

MAX_CHARS = 50          # 最大輸入字元數
MIN_INTERVAL = 1.0      # 最短請求間隔（秒）


def check_input(user_input: str) -> tuple[bool, str]:
    """
    檢查輸入合法性。
    回傳 (is_valid, error_message)
    """
    # 1. 長度限制
    if len(user_input.strip()) == 0:
        return False, "請輸入問題。"

    if len(user_input) > MAX_CHARS:
        return False, f"❌ 問題長度不能超過 {MAX_CHARS} 個字元（目前：{len(user_input)}）"

    # 2. 速率限制
    now = time.time()
    last = st.session_state.get("last_request_time", 0.0)
    elapsed = now - last

    if elapsed < MIN_INTERVAL:
        wait = MIN_INTERVAL - elapsed
        return False, f"⏳ 請稍候 {wait:.1f} 秒再提問..."

    return True, ""


def update_timestamp():
    """成功送出請求後更新時間戳"""
    st.session_state["last_request_time"] = time.time()