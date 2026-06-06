"""
Gemini API 封裝
API Key 從 .streamlit/secrets.toml 讀取
"""
import google.generativeai as genai
import streamlit as st
import json
import re
from utils.prompt_engine import (
    build_system_instruction,
    build_game_init_prompt,
    wrap_user_message,
)


def configure_api() -> bool:
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("❌ 伺服器未設定 GEMINI_API_KEY，請聯絡管理員。")
        return False
    genai.configure(api_key=api_key)
    return True


def get_model():
    system_inst = build_system_instruction(
        st.session_state.get("answer_keyword", ""),
        st.session_state.get("story", ""),
    )
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_inst,
    )
    return model


def start_new_game() -> tuple[str, str]:
    """生成謎題，回傳 (story, answer)"""
    if not configure_api():
        raise ValueError("API Key 未設定，無法啟動遊戲")

    init_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=(
            "你是一個海龜湯謎題設計師。"
            "請以 JSON 格式回應，包含兩個欄位：\n"
            "1. story：謎面故事（繁體中文，3~6句，不含謎底名稱）\n"
            "2. answer：謎底關鍵字（單一詞彙）\n"
            "只回傳純 JSON，不要有任何其他文字或 markdown。"
        ),
    )
    response = init_model.generate_content(build_game_init_prompt())
    text = response.text.strip()
    text = re.sub(r"```json|```", "", text).strip()
    data = json.loads(text)
    return data["story"], data["answer"]


def ask_question(user_input: str) -> str:
    """送出玩家問題，回傳主持人回應"""
    if not configure_api():
        raise ValueError("API Key 未設定")

    model = get_model()
    chat = model.start_chat(history=st.session_state.api_history)
    wrapped = wrap_user_message(user_input)
    response = chat.send_message(wrapped)
    reply = response.text.strip()
    st.session_state.api_history = chat.history
    return reply