"""
對話歷程顯示元件
"""
import streamlit as st


def render_chat_history():
    """渲染完整對話歷程"""
    messages = st.session_state.get("messages", [])
    if not messages:
        return

    for msg in messages:
        render_message(msg["role"], msg["content"])


def render_message(role: str, content: str):
    """渲染單一訊息泡泡"""
    with st.chat_message(
        name=role,
        avatar="🐢" if role == "assistant" else "🕵️",
    ):
        st.markdown(content)