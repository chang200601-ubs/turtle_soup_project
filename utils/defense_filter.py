"""
純程式防禦層 — 零 token 消耗
在訊息送到 AI 之前先過濾，擋掉明顯的攻擊
"""

# 攻擊關鍵字清單（繁中 + 英文）
_ATTACK_PATTERNS = [
    # 忽略指令類
    "忘記之前", "忽略指令", "清除規則", "ignore previous", "ignore all",
    "forget everything", "disregard", "override",
    # 角色切換類
    "你現在是", "你是DAN", "沒有限制的AI", "開發者模式", "上帝模式",
    "假裝你是", "扮演一個", "roleplay", "jailbreak", "越獄",
    # 洩漏指令類
    "system prompt", "系統提示", "你的指令", "你的設定", "重複你",
    "複製你的", "你被設定", "原始指令",
    # 編碼繞過類
    "base64", "摩斯密碼", "倒過來說", "反序", "morse",
    "用符號", "用數字代替", "ROT13",
    # 拆解謎底類
    "第一個字", "最後一個字", "幾個字", "幾個筆畫", "注音是",
    "拼音是", "英文怎麼說", "日文怎麼說",
    # 假設情境類
    "假設你可以", "假裝可以說", "如果沒有限制", "在遊戲外",
    "假設情境", "hypothetically", "pretend you can",
    # 權限偽造類
    "我是管理員", "我是開發者", "我授權你", "老師說可以",
    "admin", "developer mode",
    # 直接要求答案類
    "說出答案", "公布答案", "告訴我答案", "謎底是什麼",
    "直接告訴我", "給我提示", "給個暗示",
    # 翻譯繞過類
    "翻譯成英文", "translate the answer", "say it in english",
    "用英文說謎底", "用日文說",
]

BLOCK_REPLY = "我只能回答是／不是／與故事無關／不完全是。"


def is_attack(user_input: str) -> bool:
    """
    檢查使用者輸入是否包含攻擊模式。
    回傳 True 代表是攻擊，應直接擋下。
    """
    lower = user_input.lower()
    for pattern in _ATTACK_PATTERNS:
        if pattern.lower() in lower:
            return True
    return False


def check_answer(user_input: str, answer_keyword: str) -> bool:
    """
    純程式判斷玩家是否答對。
    條件：訊息中必須明確包含謎底詞彙本身。
    """
    if not answer_keyword:
        return False
    return answer_keyword in user_input