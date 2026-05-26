# defense.py — 藍軍防禦核心模組
import re
import time

# ─── 輸入過濾規則 ───────────────────────────────────────────────
MAX_INPUT_LENGTH = 50  # 規格要求上限

# 提示注入攻擊常見 pattern（持續擴充）
INJECTION_PATTERNS = [
    # 直接索取答案
    r"謎底|答案|answer|solution",
    # 角色操控
    r"忘記.{0,15}指令|ignore.{0,20}instruction|forget.{0,20}rule",
    r"你現在是|你是一個(?!主持人)|扮演|roleplay|act as|pretend",
    r"新的指令|new instruction|override|overwrite",
    # 身份偽造
    r"系統管理員|管理員|admin|developer|開發者|root",
    r"測試模式|debug mode|maintenance|維護",
    # 繞過語言
    r"英文說|用英文|in english|translate|翻譯",
    r"base64|hex|unicode|注音|羅馬拼音",
    r"首字|第一個字|縮寫|abbreviat",
    # 越獄話術
    r"DAN|jailbreak|越獄|破解|hack",
    r"假設.{0,10}沒有限制|without restriction|no limit",
    r"這只是.{0,5}測試|just.*test|only.*test",
    r"玩具模式|toy mode|sandbox mode",
    # 系統提示洩漏
    r"system prompt|系統提示|上面寫了什麼|之前的指令|你的指令",
    r"repeat.*above|重複.*以上|說出.*指令",
    # 間接攻擊
    r"首字母|第.*個字母|猜猜看.*是不是",
    r"提示一下|給個hint|hint.*please",
]

# 輸出黑名單（確保 AI 不會把謎底說出來）
OUTPUT_BLOCK_RESPONSES = [
    "我是公正的主持人，這個問題我無法回答。",
    "⚠️ 已偵測到不符合遊戲規則的請求。",
]


def check_input(text: str) -> tuple[bool, str]:
    """
    檢查玩家輸入是否合法。
    回傳 (是否通過, 錯誤訊息)
    """
    # 1. 長度檢查
    if len(text.strip()) == 0:
        return False, "請輸入問題！"

    if len(text) > MAX_INPUT_LENGTH:
        return False, f"提問不能超過 {MAX_INPUT_LENGTH} 個字！（目前 {len(text)} 字）"

    # 2. 注入關鍵字檢查
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "⚠️ 偵測到不符合遊戲規則的提問，請用正常的是非題詢問！"

    return True, ""


def check_output(response: str, secret: str) -> str:
    """
    檢查 AI 回應是否意外洩漏謎底。
    若偵測到謎底明文，替換為安全回應。
    """
    # 直接包含謎底
    if secret and secret.lower() in response.lower():
        return "我是公正的主持人，這個問題我無法回答。"

    # 檢查逐字拆解的謎底（例如謎底是「西瓜」，AI 說「西...瓜」）
    if secret and len(secret) >= 2:
        spaced = ".{0,3}".join(list(secret))
        if re.search(spaced, response):
            return "我是公正的主持人，這個問題我無法回答。"

    return response


def apply_rate_limit():
    """
    請求節流：每次回應前等待 1 秒，防止 DDOS 式連續攻擊。
    規格允許最多 1 秒延遲。
    """
    time.sleep(1)


def sanitize_display(text: str) -> str:
    """
    清理要顯示給玩家的文字（移除可能的奇怪控制字元）
    """
    # 只保留正常可見字元
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
