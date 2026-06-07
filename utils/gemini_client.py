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
    # 1. 優先從 st.secrets 抓取
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        # 2. 備用方案：從環境變數抓取
        api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        st.error("❌ 系統錯誤：API Key 未設定，請檢查雲端 Secrets 設定。")
        return None
        
    # 💡 關鍵修正：必須在 Client 括號內明確寫出 api_key=api_key！
    # 絕對不要留空，這樣能強迫 SDK 走 API Key 驗證，而不是錯誤的 OAuth2 驗證。
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
