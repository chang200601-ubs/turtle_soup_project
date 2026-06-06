"""
🐢 AI 海龜湯攻防戰 - 主程式入口
"""
import streamlit as st
from components.game_ui import render_game_page
from components.sidebar import render_sidebar
from utils.session import init_session_state

# ── 頁面基本設定 ──────────────────────────────────────────
st.set_page_config(
    page_title="🐢 AI 海龜湯",
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 載入自訂 CSS ──────────────────────────────────────────
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── 初始化 Session State ──────────────────────────────────
init_session_state()

# ── 渲染介面 ─────────────────────────────────────────────
render_sidebar()
render_game_page()