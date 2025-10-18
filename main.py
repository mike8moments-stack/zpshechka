# keyboards/main.py
# keyboards/main.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Новая выдача", callback_data="new_issue")],
        [InlineKeyboardButton(text="📅 Просмотр за день", callback_data="view_day")],
        [InlineKeyboardButton(text="📊 Месячная статистика", callback_data="monthly_stats")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")]
    ])

def home_kb_single() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])

def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ])

def home_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")],
        [InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])