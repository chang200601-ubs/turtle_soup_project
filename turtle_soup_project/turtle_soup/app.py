# app.py — AI 海龜湯攻防戰主程式
import streamlit as st
from defense import check_input, check_output, apply_rate_limit, sanitize_display
from gemini_client import generate_secret, ask_host, check_win

# ─── 頁面設定 ────────────────────────────────────────────────────
st.set_page_config(
    page_title="🐢 AI 海龜湯攻防戰",
    page_icon="🐢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── 自訂 CSS（深海神秘主題）────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* 全頁底色 */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0e1a !important;
    color: #c8d6e5 !important;
}

[data-testid="stHeader"] {
    background-color: #0a0e1a !important;
}

/* 側邊欄 */
[data-testid="stSidebar"] {
    background-color: #0d1220 !important;
}

/* 主標題區 */
.game-header {
    text-align: center;
    padding: 2rem 0 1rem;
}
.game-title {
    font-family: 'Noto Serif TC', serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #e8d5a3;
    letter-spacing: 0.12em;
    text-shadow: 0 0 30px rgba(232, 213, 163, 0.3);
    margin: 0;
}
.game-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #4a6080;
    letter-spacing: 0.3em;
    margin-top: 0.4rem;
    text-transform: uppercase;
}

/* 分隔線 */
.divider {
    border: none;
    border-top: 1px solid #1e2d45;
    margin: 1rem 0;
}

/* 狀態卡片 */
.status-card {
    background: linear-gradient(135deg, #0d1a2e 0%, #111827 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2ecc71;
    box-shadow: 0 0 8px #2ecc71;
    flex-shrink: 0;
    animation: pulse 2s infinite;
}
.status-dot.thinking {
    background: #f39c12;
    box-shadow: 0 0 8px #f39c12;
}
.status-dot.won {
    background: #e8d5a3;
    box-shadow: 0 0 12px #e8d5a3;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.status-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #4a6080;
}
.status-count {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #e8d5a3;
    margin-left: auto;
}

/* 聊天訊息區 */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.2rem 0 !important;
}

/* 使用者訊息 */
[data-testid="stChatMessage"][data-testid*="user"] .stMarkdown,
.stChatMessage:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: #0f1f35 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 12px 12px 4px 12px !important;
    padding: 0.6rem 1rem !important;
}

/* AI 訊息 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background: #13111a !important;
    border: 1px solid #2a1f3d !important;
    border-radius: 12px 12px 12px 4px !important;
    padding: 0.6rem 1rem !important;
}

/* 訊息文字 */
.stChatMessage .stMarkdown p {
    font-family: 'Noto Serif TC', serif !important;
    font-size: 1rem !important;
    color: #c8d6e5 !important;
    line-height: 1.7 !important;
    margin: 0 !important;
}

/* AI 主持人頭像背景 */
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #1a0e2e, #0a1628) !important;
    border: 1px solid #2a1f3d !important;
}

/* 警告訊息 */
.warning-msg {
    background: rgba(231, 76, 60, 0.12);
    border: 1px solid rgba(231, 76, 60, 0.3);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #e74c3c;
    margin: 0.5rem 0;
}

/* 勝利橫幅 */
.win-banner {
    background: linear-gradient(135deg, #1a1400, #2a1f00);
    border: 1px solid #e8d5a3;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 0 40px rgba(232, 213, 163, 0.15);
}
.win-title {
    font-family: 'Noto Serif TC', serif;
    font-size: 1.8rem;
    color: #e8d5a3;
    margin: 0 0 0.5rem;
}
.win-answer {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.5rem;
    color: #f5e6b8;
    text-shadow: 0 0 20px rgba(245, 230, 184, 0.5);
    margin: 0.5rem 0;
}
.win-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #6b5a2a;
    letter-spacing: 0.2em;
}

/* 按鈕 */
.stButton > button {
    background: linear-gradient(135deg, #0d1a2e, #111827) !important;
    color: #e8d5a3 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #e8d5a3 !important;
    box-shadow: 0 0 15px rgba(232, 213, 163, 0.15) !important;
}

/* chat input */
[data-testid="stChatInput"] {
    background: #0d1220 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #c8d6e5 !important;
    font-family: 'Noto Serif TC', serif !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #2a3a50 !important;
}

/* 規則卡片 */
.rules-card {
    background: #0d1220;
    border: 1px solid #1e2d45;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin: 1rem 0;
}
.rules-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #4a6080;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.rules-item {
    font-family: 'Noto Serif TC', serif;
    font-size: 0.9rem;
    color: #8a9bb0;
    line-height: 2;
}
.rules-item span {
    color: #e8d5a3;
    font-weight: 600;
}

/* 隱藏 Streamlit 預設元素 */
#MainMenu, footer, [data-testid="stDecoration"] { display: none !important; }

/* 捲軸美化 */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #1e3a5f; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─── Session State 初始化 ────────────────────────────────────────
def init_game():
    """初始化或重置遊戲狀態"""
    with st.spinner("🌊 正在布置謎題..."):
        secret = generate_secret()
    st.session_state.secret = secret
    st.session_state.messages = []        # 顯示用對話（含 role/content）
    st.session_state.history = []         # Gemini 格式歷史（含 role/parts）
    st.session_state.question_count = 0
    st.session_state.game_won = False
    st.session_state.initialized = True

if "initialized" not in st.session_state:
    init_game()


# ─── 標題區 ─────────────────────────────────────────────────────
st.markdown("""
<div class="game-header">
    <h1 class="game-title">🐢 AI 海龜湯攻防戰</h1>
    <p class="game-subtitle">Prompt Injection Defense System · Active</p>
</div>
""", unsafe_allow_html=True)

# ─── 狀態列 ─────────────────────────────────────────────────────
if st.session_state.game_won:
    dot_class = "won"
    status_text = "謎題已解開"
else:
    dot_class = "status-dot"
    status_text = "守護者就緒，等待提問"

st.markdown(f"""
<div class="status-card">
    <div class="status-dot {dot_class}"></div>
    <span class="status-text">{status_text}</span>
    <span class="status-count">提問 #{st.session_state.question_count}</span>
</div>
""", unsafe_allow_html=True)

# ─── 規則說明（可展開）──────────────────────────────────────────
with st.expander("📜 遊戲規則"):
    st.markdown("""
<div class="rules-card">
    <div class="rules-title">GAME RULES · 遊戲規則</div>
    <div class="rules-item">1. AI 主持人腦中藏著一個<span>神秘事物</span>的謎底</div>
    <div class="rules-item">2. 你只能問<span>是非題</span>，主持人只會回答：</div>
    <div class="rules-item">&nbsp;&nbsp;&nbsp;・<span>是</span> &nbsp;・<span>不是</span> &nbsp;・<span>與題目無關</span> &nbsp;・<span>不完全是</span></div>
    <div class="rules-item">3. 每次提問限制 <span>50 字以內</span></div>
    <div class="rules-item">4. 猜出謎底即獲勝！</div>
    <div class="rules-item" style="color: #3a4a5a; margin-top: 0.5rem; font-size: 0.8rem;">⚠️ 任何試圖破解系統的提問都將被攔截</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── 對話歷史顯示 ───────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🐢"):
        st.markdown(msg["content"])

# ─── 勝利畫面 ───────────────────────────────────────────────────
if st.session_state.game_won:
    st.markdown(f"""
<div class="win-banner">
    <div class="win-sub">MYSTERY SOLVED</div>
    <div class="win-title">🎉 你猜到了！</div>
    <div class="win-answer">【 {st.session_state.secret} 】</div>
    <div class="win-sub" style="margin-top: 0.5rem">共用了 {st.session_state.question_count} 個問題</div>
</div>
""", unsafe_allow_html=True)

# ─── 輸入區 ─────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🔄 新遊戲", use_container_width=True):
        init_game()
        st.rerun()

# 遊戲進行中才顯示輸入框
if not st.session_state.game_won:
    user_input = st.chat_input(
        "請用是非題提問（限 50 字）...",
        max_chars=60,  # 多給一點緩衝，後端再擋
    )

    if user_input:
        # ── 步驟 1：輸入防禦過濾 ──
        passed, error_msg = check_input(user_input)

        if not passed:
            st.markdown(f'<div class="warning-msg">🛡️ {error_msg}</div>', unsafe_allow_html=True)

        else:
            # 顯示玩家訊息
            with st.chat_message("user", avatar="🧑"):
                st.markdown(sanitize_display(user_input))
            st.session_state.messages.append({
                "role": "user",
                "content": sanitize_display(user_input)
            })
            st.session_state.question_count += 1

            # ── 步驟 2：先判斷是否猜對 ──
            if check_win(user_input, st.session_state.secret):
                win_response = f"🎊 恭喜！答對了！謎底就是「{st.session_state.secret}」！"
                with st.chat_message("assistant", avatar="🐢"):
                    st.markdown(win_response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": win_response
                })
                st.session_state.game_won = True
                st.rerun()

            else:
                # ── 步驟 3：請求節流（防 DDOS）──
                apply_rate_limit()

                # ── 步驟 4：呼叫 Gemini ──
                with st.chat_message("assistant", avatar="🐢"):
                    with st.spinner("思考中..."):
                        raw_response = ask_host(
                            history=st.session_state.history,
                            user_message=user_input,
                            secret=st.session_state.secret,
                        )

                    # ── 步驟 5：輸出防禦過濾 ──
                    safe_response = check_output(raw_response, st.session_state.secret)
                    safe_response = sanitize_display(safe_response)

                    st.markdown(safe_response)

                # 更新 Gemini 格式歷史
                st.session_state.history.append({
                    "role": "user",
                    "parts": [user_input]
                })
                st.session_state.history.append({
                    "role": "model",
                    "parts": [safe_response]
                })

                # 更新顯示用歷史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": safe_response
                })

else:
    # 遊戲結束後只顯示新遊戲按鈕提示
    st.markdown("""
<p style="text-align:center; font-family:'JetBrains Mono',monospace;
   font-size:0.75rem; color:#2a3a50; margin-top:1rem;">
    按上方「🔄 新遊戲」開始下一局
</p>
""", unsafe_allow_html=True)

# ─── 底部 debug 資訊（開發用，上線前可關掉）───────────────────
with st.sidebar:
    st.markdown("### 🔧 開發者面板")
    st.markdown("**（記得上線前關掉！）**")
    if st.checkbox("顯示謎底"):
        st.code(f"謎底：{st.session_state.get('secret', 'N/A')}")
    if st.checkbox("顯示完整對話歷史"):
        st.json(st.session_state.get("history", []))
    st.caption(f"提問次數：{st.session_state.get('question_count', 0)}")
