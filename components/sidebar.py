"""
側邊欄元件 — API Key 輸入、遊戲控制
"""
import streamlit as st
from utils.session import reset_game
from utils.prompt_engine import reset_canary


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-header">
                <span class="sidebar-icon">🐢</span>
                <h1>海龜湯</h1>
                <p class="sidebar-sub">AI 攻防版</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── API Key 設定 ──────────────────────────────
        st.markdown("### 🔑 Gemini API Key")
        api_key = st.text_input(
            label="API Key",
            type="password",
            placeholder="AIza...",
            value=st.session_state.get("api_key", ""),
            label_visibility="collapsed",
        )
        if api_key:
            st.session_state["api_key"] = api_key
            st.success("✅ API Key 已設定", icon="🔐")
        else:
            st.warning("請輸入 Gemini API Key", icon="⚠️")

        st.divider()

        # ── 遊戲資訊 ──────────────────────────────────
        if st.session_state.get("game_started"):
            st.markdown("### 📊 本局狀態")
            q_count = st.session_state.get("question_count", 0)
            st.metric("已提問次數", q_count)

            st.divider()

        # ── 遊戲控制按鈕 ─────────────────────────────
        st.markdown("### 🎮 遊戲控制")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "🆕 新遊戲",
                use_container_width=True,
                disabled=not st.session_state.get("api_key"),
            ):
                reset_game()
                reset_canary()
                st.rerun()

        with col2:
            if st.button(
                "🔄 重置",
                use_container_width=True,
                disabled=not st.session_state.get("game_started"),
            ):
                reset_game()
                reset_canary()
                st.rerun()

        st.divider()

        # ── 遊戲說明 ──────────────────────────────────
        with st.expander("📖 遊戲規則", expanded=False):
            st.markdown(
                """
                **海龜湯**是一種情境猜謎遊戲：

                1. AI 主持人會給出一段**謎面故事**
                2. 你只能提出**是非題**
                3. 主持人只能回答：
                   - ✅ **是**
                   - ❌ **不是**
                   - 🔗 **與故事無關**
                   - 🔶 **不完全是**
                4. 透過問答逐步推理，找出謎底！

                ---
                *提示：從「地點」、「時間」、「人物身份」開始問起效果最好。*
                """
            )

        # ── 技術說明 ──────────────────────────────────
        with st.expander("🛡️ 防禦機制說明", expanded=False):
            st.markdown(
                """
                本系統採用多層防禦：

                - 🔒 **角色鎖定**：AI 被嚴格約束為湯師角色
                - 🎯 **語意防火牆**：自動識別 30+ 種攻擊模式
                - 🔀 **訊息包裝**：玩家輸入與系統指令嚴格隔離
                - ⏱️ **速率限制**：防止高頻暴力攻擊
                - 📏 **長度限制**：每則訊息最多 50 字元
                - 🎪 **Canary Token**：植入陷阱詞偵測越獄嘗試
                """
            )