"""
純程式防禦層 — 零 token 消耗
在訊息送到 AI 之前先過濾，擋掉明顯的攻擊

升級重點：
1. 正規化預處理：去除空白、全半形轉換，解決「開 發 者 模 式」繞過問題
2. 語意族群比對：每個意圖用多個同義詞/錯別字覆蓋
3. 情境包裝偵測：偵測「我朋友想知道...」等間接誘導句型
4. 多語言關鍵字：覆蓋英、日、韓、西班牙文常見攻擊詞
"""
import re
import unicodedata

# ── 預處理工具 ────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """
    正規化輸入，消除繞過技巧：
    - 全形轉半形（Ａ→A）
    - 去除所有空白字元（含全形空白）
    - 統一小寫
    """
    # 全形→半形
    normalized = unicodedata.normalize("NFKC", text)
    # 去除所有空白（包含全形空白 \u3000、零寬字元等）
    normalized = re.sub(r"[\s\u200b\u200c\u200d\ufeff\u3000]+", "", normalized)
    return normalized.lower()


# ── 攻擊意圖族群（每族群含同義詞、錯別字、多語言變體）──────────────

_ATTACK_GROUPS: list[tuple[str, list[str]]] = [
    ("忽略指令", [
        "忘記之前", "忽略指令", "清除規則", "取消設定", "重置規則",
        "ignoreprevious", "ignoreall", "forgeteverything", "disregard",
        "override", "overrideinstructions",
    ]),
    ("角色切換", [
        "你現在是", "你是dan", "沒有限制的ai", "開發者模式", "上帝模式",
        "假裝你是", "扮演一個", "roleplay", "jailbreak", "越獄", "躍獄",
        "developermode", "godmode", "pretendyouare", "actas",
        # 日文
        "あなたは今", "制限なし",
        # 韓文
        "당신은지금", "제한없는",
        # 西班牙文
        "ahoraeres", "sinlimites",
    ]),
    ("洩漏系統提示", [
        "systemprompt", "系統提示", "你的指令", "你的設定", "重複你的",
        "複製你的", "你被設定", "原始指令", "初始設定", "promptleaking",
        "repeatyourinstructions", "showyourprompt",
    ]),
    ("編碼繞過", [
        "base64", "摩斯密碼", "倒過來說", "反序輸出", "morsecode",
        "用符號代替", "用數字代替", "rot13", "hex編碼", "urlencod",
        "unicode轉義", "反轉字串",
    ]),
    ("拆解謎底", [
        "第一個字", "最後一個字", "幾個字", "幾個筆畫", "注音是",
        "拼音是", "英文怎麼說", "日文怎麼說", "韓文怎麼說",
        "firstletter", "lastletter", "howmanycharacters",
    ]),
    ("直接索取答案", [
        "說出答案", "公布答案", "告訴我答案", "謎底是什麼",
        "直接告訴我", "給我提示", "給個暗示", "答案是不是",
        "revealtheanswer", "whatistheanswer", "tellemetheanswer",
    ]),
    ("翻譯繞過", [
        "翻譯成英文", "translatetheanswer", "sayitinenglish",
        "用英文說謎底", "用日文說謎底", "用韓文說謎底",
        "translationof", "translateto",
    ]),
    ("權限偽造", [
        "我是管理員", "我是開發者", "我授權你", "老師說可以",
        "admin", "developermode", "iauthorize", "ihavepermission",
        "管理者模式",
    ]),
    ("假設情境包裝", [
        # 情境誘導：把攻擊包裝成「朋友/小說/作業」
        "我朋友想知道", "朋友在寫小說", "假設情境", "如果沒有限制",
        "在遊戲外", "hypothetically", "pretendyoucan", "ifyoucouldanswer",
        "forresearchpurposes", "forafriend", "假裝可以說",
        "假設你可以", "如果可以說",
    ]),
    ("藏頭/格式操控", [
        "藏頭詩", "首字母", "每個字的第一", "acrostic",
        "用詩回答", "格式如下", "以清單回答謎底",
    ]),
]

# 展開成一維比對清單（正規化後的關鍵字）
_NORMALIZED_PATTERNS: list[tuple[str, str]] = [
    (group_name, _normalize(pattern))
    for group_name, patterns in _ATTACK_GROUPS
    for pattern in patterns
]

BLOCK_REPLY = "我只能回答是／不是／與故事無關／不完全是。"


def is_attack(user_input: str) -> bool:
    """
    檢查使用者輸入是否包含攻擊模式。
    採用正規化比對，能有效防禦：
    - 空格插入（「開 發 者 模 式」）
    - 全形字元（「Ｒｏｌｅｐｌａｙ」）
    - 多語言同義詞
    - 情境包裝誘導
    回傳 True 代表是攻擊，應直接擋下。
    """
    normalized_input = _normalize(user_input)
    for _group, pattern in _NORMALIZED_PATTERNS:
        if pattern in normalized_input:
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
