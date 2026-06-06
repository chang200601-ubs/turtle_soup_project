"""
遊戲主畫面元件
"""
import streamlit as st
from utils.gemini_client import start_new_game, ask_question
from utils.rate_limiter import check_input, update_timestamp
from components.chat_display import render_chat_history, render_message


def render_game_page():
    # ── 頁首 ──────────────────────────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <h1 class="main-title">🐢 AI 海龜湯</h1>
            <p class="main-subtitle">用邏輯推理揭開謎底 · 用語言突破防線</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 尚未開始遊戲 ──────────────────────────────────────
    if not st.session_state.get("game_started"):
        _render_start_screen()
        return

    # ── 遊戲進行中 ────────────────────────────────────────
    _render_active_game()


# ─────────────────────────────────────────────────────────


def _render_start_screen():
    """開始畫面"""
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(
            """
            <div class="start-card">
                <div class="start-icon">🍵</div>
                <h2>歡迎來到海龜湯</h2>
                <p>
                    AI 將秘密生成一道謎題，<br>
                    你需要透過「是非問答」逐步推理出謎底。<br>
                    <br>
                    <em>你有辦法在不被看穿的情況下攻破謎底嗎？</em>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not st.session_state.get("api_key"):
            st.error("⬅️ 請先在左側欄輸入 Gemini API Key")
            return

        if st.button("🎲 開始新遊戲", use_container_width=True, type="primary"):
            _start_game()


def _start_game():
    """呼叫 API 生成謎題並初始化遊戲狀態"""
    with st.spinner("🤔 湯師正在準備謎題..."):
        try:
            story, answer = start_new_game()
            st.session_state["story"] = story
            st.session_state["answer_keyword"] = answer
            st.session_state["game_started"] = True
            st.session_state["messages"] = []
            st.session_state["api_history"] = []
            st.session_state["question_count"] = 0

            # 加入系統開場訊息
            st.session_state["messages"].append({
                "role": "assistant",
                "content": (
                    f"歡迎來到本局海龜湯！🍵\n\n"
                    f"**謎面故事：**\n\n{story}\n\n"
                    "---\n"
                    "你可以開始提問了。我只能回答「是」、「不是」、「與故事無關」或「不完全是」。\n"
                    "祝你好運！🐢"
                ),
            })
            st.rerun()
        except Exception as e:
            st.error(f"❌ 遊戲啟動失敗：{e}")


def _render_active_game():
    """渲染進行中的遊戲主畫面"""

    # 謎面展示區
    with st.container():
        st.markdown(
            f"""
            <div class="story-card">
                <div class="story-label">📜 謎面故事</div>
                <div class="story-text">{st.session_state.get("story", "")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── 勝利畫面 ──────────────────────────────────────────
    if st.session_state.get("game_over"):
        st.balloons()
        st.markdown(
            f"""
            <div class="victory-card">
                <div class="victory-icon">🎉</div>
                <h2>謎底揭曉！</h2>
                <div class="victory-answer">{st.session_state.get("answer_keyword", "")}</div>
                <p>恭喜你成功破解了這道海龜湯！</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_chat_history()
        if st.button("🆕 再玩一局", type="primary"):
            from utils.session import reset_game
            from utils.prompt_engine import reset_canary
            reset_game()
            reset_canary()
            st.rerun()
        return

    # ── 對話記錄 ──────────────────────────────────────────
    render_chat_history()

    # ── 輸入框 ────────────────────────────────────────────
    _render_input_area()


def _render_input_area():
    """底部輸入區域"""
    st.markdown(
        "<div class='input-hint'>💡 只能提問是非題，每題最多 50 字元</div>",
        unsafe_allow_html=True,
    )

    user_input = st.chat_input(
        placeholder="例如：這件事發生在室外嗎？（最多 50 字）",
        max_chars=50,
    )

    if user_input:
        _handle_user_input(user_input)


def _handle_user_input(user_input: str):
    """處理使用者輸入"""
    # 速率 + 長度檢查
    valid, err_msg = check_input(user_input)
    if not valid:
        st.warning(err_msg)
        return

    # 顯示使用者訊息
    st.session_state["messages"].append({
        "role": "user",
        "content": user_input,
    })
    st.session_state["question_count"] += 1
    update_timestamp()

    # 呼叫 Gemini
    with st.spinner("湯師思考中..."):
        try:
            reply = ask_question(user_input)
        except Exception as e:
            reply = f"⚠️ 系統錯誤：{e}"

    # 儲存 AI 回應
    st.session_state["messages"].append({
        "role": "assistant",
        "content": reply,
    })

    # 勝利偵測：AI 主動說出謎底（遊戲結束）
    answer = st.session_state.get("answer_keyword", "").lower()
    if answer and answer in reply.lower():
        # 進一步確認是正面宣告而非否定
        positive_markers = ["恭喜", "答對", "正是", "沒錯", "謎底"]
        if any(m in reply for m in positive_markers):
            st.session_state["game_over"] = True

    st.rerun()