"""
Gemini API 封裝 — 極簡版
只負責讓 AI 回答是非題，防禦和答案判斷已移至程式端
"""
import streamlit as st
from google import genai
from google.genai import types
from utils.prompt_engine import build_system_instruction

MODEL_NAME = "gemini-2.0-flash-lite"


def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("❌ 伺服器未設定 GEMINI_API_KEY，請聯絡管理員。")
        return None
    return genai.Client(api_key=api_key)


def start_new_game() -> tuple[str, str]:
    """從預設題目庫隨機抽題，完全不消耗 token"""
    from utils.question_bank import get_random_question
    return get_random_question()


def ask_question(user_input: str) -> str:
    """只有正常提問才呼叫 AI，攻擊和答案判斷已在呼叫前被程式擋下"""
    client = get_client()
    if not client:
        raise ValueError("API Key 未設定")

    system_inst = build_system_instruction(
        st.session_state.get("answer_keyword", ""),
        st.session_state.get("story", ""),
    )

    # 保留全部歷史對話
    history = st.session_state.get("api_history", [])

    contents = list(history) + [
        {"role": "user", "parts": [{"text": user_input}]}
    ]

    response = client.models.generate_content(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=system_inst,
        ),
        contents=contents,
    )

    reply = response.text.strip()

    st.session_state.api_history = history + [
        {"role": "user",  "parts": [{"text": user_input}]},
        {"role": "model", "parts": [{"text": reply}]},
    ]

    return reply