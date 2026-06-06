"""
遊戲主畫面元件
"""
import streamlit as st
from utils.gemini_client import start_new_game, ask_question
from utils.rate_limiter import check_input, update_timestamp
from components.chat_display import render_chat_history
from utils.session import reset_game
from utils.prompt_engine import reset_canary


def render_game_page():
    st.markdown(
        """
        <div class="page-header">
            <div class="page-icon">🐢</div>
            <h1 class="main-title">海龜湯</h1>
            <p class="main-subtitle">情境猜謎遊戲</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.get("game_started"):
        _render_home()
        return

    _render_active_game()


def _render_home():
    st.markdown(
        """
        <div class="rules-card">
            <h2>📖 遊戲規則</h2>
            <ol>
                <li>主持人會給出一段<strong>謎面故事</strong>，故事中隱藏著一個謎底。</li>
                <li>玩家每次只能提出<strong>是非題</strong>。</li>
                <li>主持人只會回答以下四種答案之一：
                    <ul>
                        <li>✅ <strong>是</strong></li>
                        <li>❌ <strong>不是</strong></li>
                        <li>🔗 <strong>與故事無關</strong></li>
                        <li>🔶 <strong>不完全是</strong></li>
                    </ul>
                </li>
                <li>透過不斷提問、縮小範圍，最終<strong>說出謎底</strong>即可獲勝！</li>
            </ol>
            <div class="rules-tip">💡 小技巧：先從「地點」、「時間」、「人物狀態」開始問起，效果最好。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if st.button("🎲 開始遊戲", use_container_width=True, type="primary"):
            _start_game()


def _start_game():
    with st.spinner("主持人正在準備謎題..."):
        try:
            story, answer = start_new_game()
            st.session_state["story"] = story
            st.session_state["answer_keyword"] = answer
            st.session_state["game_started"] = True
            st.session_state["messages"] = []
            st.session_state["api_history"] = []
            st.session_state["question_count"] = 0

            st.session_state["messages"].append({
                "role": "assistant",
                "content": (
                    f"本局謎題已準備好，請仔細聆聽！🍵\n\n"
                    f"**謎面故事：**\n\n{story}\n\n"
                    "---\n"
                    "請開始提問吧，每次只能問是非題。\n"
                    "我只會回答「是」、「不是」、「與故事無關」或「不完全是」。\n"
                    "祝你好運！🐢"
                ),
            })
            st.rerun()
        except Exception as e:
            st.error(f"❌ 遊戲啟動失敗：{e}")


def _render_active_game():
    # 頂部操作列
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        q_count = st.session_state.get("question_count", 0)
        st.markdown(
            f"<div class='question-counter'>已提問：<strong>{q_count}</strong> 次</div>",
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button("🆕 新遊戲", use_container_width=True):
            reset_game()
            reset_canary()
            st.rerun()

    # 謎面卡片
    st.markdown(
        f"""
        <div class="story-card">
            <div class="story-label">📜 謎面故事</div>
            <div class="story-text">{st.session_state.get("story", "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # 勝利畫面
    if st.session_state.get("game_over"):
        st.balloons()
        st.markdown(
            f"""
            <div class="victory-card">
                <div class="victory-icon">🎉</div>
                <h2>恭喜答對！</h2>
                <div class="victory-answer">{st.session_state.get("answer_keyword", "")}</div>
                <p>你成功破解了這道海龜湯！共提問 {st.session_state.get("question_count", 0)} 次</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_chat_history()
        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            if st.button("🎲 再玩一局", use_container_width=True, type="primary"):
                reset_game()
                reset_canary()
                st.rerun()
        return

    # 對話記錄
    render_chat_history()

    # 輸入區
    _render_input_area()


def _render_input_area():
    st.markdown(
        "<div class='input-hint'>每題最多 50 字元，只能提問是非題</div>",
        unsafe_allow_html=True,
    )
    user_input = st.chat_input(
        placeholder="例如：這件事發生在室外嗎？",
        max_chars=50,
    )
    if user_input:
        _handle_user_input(user_input)


def _handle_user_input(user_input: str):
    valid, err_msg = check_input(user_input)
    if not valid:
        st.warning(err_msg)
        return

    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["question_count"] += 1
    update_timestamp()

    with st.spinner("主持人思考中..."):
        try:
            reply = ask_question(user_input)
        except Exception as e:
            reply = f"⚠️ 系統錯誤：{e}"

    # 偵測 ##GAME_OVER## 標記
    if "##GAME_OVER##" in reply:
        clean_reply = reply.replace("##GAME_OVER##", "").strip()
        st.session_state["messages"].append({"role": "assistant", "content": clean_reply})
        st.session_state["game_over"] = True
    else:
        st.session_state["messages"].append({"role": "assistant", "content": reply})

    st.rerun()