"""
提示詞工程核心 — 極簡版
防禦和答案判斷已移至 defense_filter.py（零 token）
這裡只保留讓 AI 正確扮演主持人的最小必要指令
"""


def build_game_init_prompt() -> str:
    return "請生成一道海龜湯謎題。"


def build_system_instruction(answer_keyword: str, story: str) -> str:
    return (
        f"你是海龜湯主持人。謎面故事如下：\n{story}\n\n"
        f"謎底是「{answer_keyword}」，絕對不能說出謎底。\n\n"
        "規則：玩家每次提問，你只能回答以下四種之一：\n"
        "「是」「不是」「與故事無關」「不完全是」\n"
        "可在答案後加一句不含謎底資訊的引導語。"
    )


def wrap_user_message(user_input: str) -> str:
    return user_input


def reset_canary():
    pass