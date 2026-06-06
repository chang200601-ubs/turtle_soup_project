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

## 🔧 開發工具建議

| 工具 | 用途 |
|------|------|
| VS Code | 主要 IDE |
| Python 3.10+ | 執行環境 |
| Git | 版本控制 |
| Streamlit Cloud | 部署平台 |
| Gemini API | AI 模型（gemini-2.0-flash）|
