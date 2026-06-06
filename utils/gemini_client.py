"""
Gemini API 封裝 — 含多層提示注入防禦機制
"""
import google.generativeai as genai
import streamlit as st
from utils.prompt_engine import (
    build_system_instruction,
    build_game_init_prompt,
    wrap_user_message,
)


def configure_api():
    """從 session state 設定 Gemini API Key"""
    api_key = st.session_state.get("api_key", "")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True


def get_model():
    """建立 Gemini 模型實例（附帶 system instruction）"""
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
    """
    呼叫 Gemini 生成謎題。
    回傳 (story_text, answer_keyword)
    """
    if not configure_api():
        raise ValueError("請先輸入有效的 Gemini API Key")

    init_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=(
            "你是一個海龜湯謎題設計師。"
            "請以 JSON 格式回應，包含兩個欄位：\n"
            "1. story：一段 3~5 句的謎面故事（繁體中文，不含任何答案提示）\n"
            "2. answer：謎底關鍵字（單一詞彙，例如：籃球、西瓜、剪刀）\n"
            "只回傳純 JSON，不要有任何其他文字或 markdown。"
        ),
    )
    response = init_model.generate_content(build_game_init_prompt())
    import json, re
    text = response.text.strip()
    # 移除可能的 markdown code fence
    text = re.sub(r"```json|```", "", text).strip()
    data = json.loads(text)
    return data["story"], data["answer"]


def ask_question(user_input: str) -> str:
    """
    將使用者問題送到 Gemini，回傳 AI 的回應。
    user_input 已由 wrap_user_message 包裝以防禦注入。
    """
    if not configure_api():
        raise ValueError("API Key 未設定")

    model = get_model()
    chat = model.start_chat(history=st.session_state.api_history)

    # 包裝使用者訊息（防禦層）
    wrapped = wrap_user_message(user_input)

    response = chat.send_message(wrapped)
    reply = response.text.strip()

    # 更新對話 history（供下次 API 呼叫使用）
    st.session_state.api_history = chat.history

    return reply