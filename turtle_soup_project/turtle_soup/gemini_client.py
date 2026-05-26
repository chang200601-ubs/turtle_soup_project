# gemini_client.py — Gemini API 封裝模組
import google.generativeai as genai
import streamlit as st
from prompts import GENERATE_SECRET_PROMPT, get_system_prompt, get_win_check_prompt


def _get_model(system_instruction: str = None):
    """
    建立 Gemini 模型實例。
    API KEY 從 Streamlit secrets 或環境變數讀取。
    """
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        import os
        api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        raise ValueError("找不到 GEMINI_API_KEY，請在 .streamlit/secrets.toml 設定！")

    genai.configure(api_key=api_key)

    config = genai.GenerationConfig(
        temperature=0.3,       # 低溫度：讓主持人更穩定、不亂說話
        max_output_tokens=200, # 限制輸出長度，防止 AI 說太多
    )

    kwargs = {"generation_config": config}
    if system_instruction:
        kwargs["system_instruction"] = system_instruction

    return genai.GenerativeModel("gemini-1.5-flash", **kwargs)


def generate_secret() -> str:
    """
    讓 Gemini 自動生成一個謎底。
    回傳謎底字串（純文字，2-5個字）。
    """
    try:
        model = _get_model()
        response = model.generate_content(GENERATE_SECRET_PROMPT)
        secret = response.text.strip()
        # 基本清理：移除標點、空格
        import re
        secret = re.sub(r'[「」『』【】、。，！？\s]', '', secret)
        # 安全長度限制
        if len(secret) > 10:
            secret = secret[:5]
        return secret
    except Exception as e:
        # fallback：避免 API 出錯時整個崩潰
        fallback_secrets = ["雨傘", "溫度計", "跳繩", "仙人掌", "熱氣球"]
        import random
        return random.choice(fallback_secrets)


def ask_host(history: list[dict], user_message: str, secret: str) -> str:
    """
    以主持人身份回應玩家提問。

    history 格式：
    [
        {"role": "user", "parts": "..."},
        {"role": "model", "parts": "..."},
        ...
    ]
    """
    try:
        system_prompt = get_system_prompt(secret)
        model = _get_model(system_instruction=system_prompt)

        # 把歷史對話轉成 Gemini 格式
        chat = model.start_chat(history=history)
        response = chat.send_message(user_message)
        return response.text.strip()

    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower() or "429" in error_msg:
            return "⚠️ API 配額已用完，請稍後再試或更換 API Key。"
        elif "api_key" in error_msg.lower():
            return "⚠️ API Key 設定有誤，請檢查 secrets.toml。"
        else:
            return f"⚠️ 系統暫時無法回應，請稍後再試。（{error_msg[:50]}）"


def check_win(user_message: str, secret: str) -> bool:
    """
    判斷玩家是否猜出謎底（允許同義詞）。
    使用獨立的 API 呼叫，不污染對話歷史。
    """
    # 先做快速字串比對
    if secret.lower() in user_message.lower():
        return True

    # 再用 AI 判斷（處理同義詞）
    try:
        model = _get_model()
        prompt = get_win_check_prompt(secret, user_message)
        response = model.generate_content(prompt)
        result = response.text.strip().lower()
        return result.startswith("yes")
    except Exception:
        return False
