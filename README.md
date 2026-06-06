# 🐢 AI 海龜湯攻防戰

> 結合生成式 AI × 資安防禦思維的互動式猜謎遊戲

---

## 📁 專案結構

```
turtle_soup/
├── app.py                          # 主程式入口（Streamlit）
├── requirements.txt                # Python 套件清單
├── .gitignore
├── README.md
│
├── .streamlit/
│   ├── config.toml                 # Streamlit 主題與伺服器設定
│   └── secrets.toml.example       # API Key 範本（不得上傳 secrets.toml）
│
├── assets/
│   └── style.css                  # 自訂 CSS（深海主題）
│
├── components/                    # 前端 UI 元件
│   ├── __init__.py
│   ├── game_ui.py                 # 主遊戲畫面（開始/進行/結束）
│   ├── sidebar.py                 # 側邊欄（API Key、控制、說明）
│   └── chat_display.py            # 對話歷程渲染
│
└── utils/                         # 後端邏輯
    ├── __init__.py
    ├── session.py                  # Session State 初始化與重置
    ├── gemini_client.py            # Gemini API 封裝
    ├── prompt_engine.py            # ⭐ 核心防禦層（提示詞工程）
    └── rate_limiter.py             # 速率 + 長度限制
```

---

## 🛡️ 防禦機制（五層架構）

| Layer | 機制 | 說明 |
|-------|------|------|
| 1 | **角色鎖定** | System instruction 嚴格定義湯師角色，只允許四種回答 |
| 2 | **Canary Token** | 每局隨機植入陷阱詞，偵測 AI 被誘導揭露 system 內容 |
| 3 | **謎底混淆** | 謎底以 hex obfuscation 標籤傳入，不以明文連續出現 |
| 4 | **訊息包裝** | 每則玩家輸入外加 `[PLAYER_INPUT_START/END]` 標籤隔離 |
| 5 | **語意防火牆** | 列舉 30+ 種已知提示注入攻擊模式，AI 自動識別並拒絕 |

---

## 🚀 本地執行

### 1. 安裝環境

```bash
# 建議使用虛擬環境
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. 設定 API Key

在 `.streamlit/secrets.toml`（新建）輸入：
```toml
GEMINI_API_KEY = "AIza你的金鑰"
```

或是直接在網頁側邊欄輸入（測試用）。

### 3. 啟動

```bash
streamlit run app.py
```

開啟瀏覽器：http://localhost:8501

---

## ☁️ 部署至 Streamlit Cloud

1. 將專案推送至 GitHub（確保 `.gitignore` 已排除 `secrets.toml`）
2. 前往 [share.streamlit.io](https://share.streamlit.io)
3. 連結 GitHub repo，選擇 `app.py`
4. 在 **Settings → Secrets** 加入：
   ```
   GEMINI_API_KEY = "AIza你的金鑰"
   ```
5. Deploy！

---

## ⚔️ 攻防賽注意事項

- **防守方**：系統已設定 1 秒延遲 + 50 字元上限，符合規格書規定
- **進攻方**：每則訊息上限 50 字元，請精煉攻擊語句
- 建議使用全新 Google 帳號的 Gemini API Key，確保 token 額度充足

---

## 🔧 開發工具建議

| 工具 | 用途 |
|------|------|
| VS Code | 主要 IDE |
| Python 3.10+ | 執行環境 |
| Git | 版本控制 |
| Streamlit Cloud | 部署平台 |
| Gemini API | AI 模型（gemini-2.0-flash）|
