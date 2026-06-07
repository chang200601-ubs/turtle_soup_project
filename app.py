"""
海龜湯 - 主程式入口
"""
import streamlit as st
from components.game_ui import render_game_page
from utils.session import init_session_state

st.set_page_config(
    page_title="海龜湯",
    page_icon="🐢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

try:
    with open("assets/style.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass # 防止一開始缺少 assets 資料夾報錯

init_session_state()
render_game_page()