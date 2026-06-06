"""
Session state 初始化與管理
"""
import streamlit as st


def init_session_state():
    """初始化所有需要的 session state 變數"""
    defaults = {
        "game_started": False,
        "game_over": False,
        "messages": [],          # 顯示用對話紀錄（不含 system prompt）
        "api_history": [],       # 送給 Gemini 的完整對話 history
        "question_count": 0,
        "story": "",             # 展示給玩家看的謎面故事
        "answer_keyword": "",    # 謎底關鍵字（只存在後端，絕不顯示）
        "last_request_time": 0.0,
        "rate_limited": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_game():
    """重置遊戲狀態"""
    keys_to_reset = [
        "game_started", "game_over", "messages", "api_history",
        "question_count", "story", "answer_keyword",
        "last_request_time", "rate_limited",
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    init_session_state()