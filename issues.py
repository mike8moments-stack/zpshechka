# keyboards/issues.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import RATE_OPTIONS, MULTIPOLIS_CHOICES, DK_TYPES

def issue_types_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Кредит (С ФЗ)", callback_data="issue_s_fz"),
         InlineKeyboardButton(text="💼 Кредит (Без ФЗ)", callback_data="issue_bez_fz")],  # Одинаковые эмоджи
        [InlineKeyboardButton(text="💳 КРХ", callback_data="issue_krh"),
         InlineKeyboardButton(text="💳 Дебет", callback_data="issue_debet")],
        [InlineKeyboardButton(text="🧾 Рассрочка", callback_data="issue_rassrochka"),
         InlineKeyboardButton(text="🛡️ Мультиполис", callback_data="issue_multipolis")],
        [InlineKeyboardButton(text="🔐 ДК", callback_data="issue_dk")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back"),
         InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])

def term_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="0-6", callback_data="term_0-6"), 
         InlineKeyboardButton(text="7-12", callback_data="term_7-12")],
        [InlineKeyboardButton(text="13-23", callback_data="term_13-23"), 
         InlineKeyboardButton(text="24-30", callback_data="term_24-30")],
        [InlineKeyboardButton(text="31-36", callback_data="term_31-36")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back"),
         InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])

def rate_kb() -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(RATE_OPTIONS), 2):
        row = [InlineKeyboardButton(text=RATE_OPTIONS[i] + "%", callback_data=f"rate_{RATE_OPTIONS[i]}")]
        if i + 1 < len(RATE_OPTIONS):
            row.append(InlineKeyboardButton(text=RATE_OPTIONS[i + 1] + "%", callback_data=f"rate_{RATE_OPTIONS[i+1]}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="↩️ Назад", callback_data="back"),
                 InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def multipolis_amount_kb() -> InlineKeyboardMarkup:
    from utils.helpers import format_currency
    rows = []
    for val in MULTIPOLIS_CHOICES:
        rows.append([InlineKeyboardButton(text=f"🛡️ {format_currency(val)}", callback_data=f"multipolis_sum_{val}")])
    rows.append([InlineKeyboardButton(text="↩️ Назад", callback_data="back"),
                 InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def dk_types_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ДК с ФЗ", callback_data="dk_dk_s_fz"),
         InlineKeyboardButton(text="ДК МКК (без ФЗ)", callback_data="dk_dk_mkk_no_fz")],
        [InlineKeyboardButton(text="ДК МКК (с ФЗ)", callback_data="dk_dk_mkk_with_fz"),
         InlineKeyboardButton(text="Рефинансирование КРХ", callback_data="dk_refinance_krh")],
        [InlineKeyboardButton(text="КНК через ЛИД с ФЗ", callback_data="dk_knk_lead_fz"),
         InlineKeyboardButton(text="Ипотека/Реф ипотеки", callback_data="dk_ipoteka_ref")],
        [InlineKeyboardButton(text="ДКПЗН", callback_data="dk_dkpzn"),
         InlineKeyboardButton(text="Автокредит/ДКПЗА", callback_data="dk_autocredit")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back"),
         InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])
    return kb

def rassrochka_choice_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Рассрочка с ФЗ", callback_data="issue_rass_with"),
         InlineKeyboardButton(text="⚪ Рассрочка без ФЗ", callback_data="issue_rass_without")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ])

def debet_choice_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, выдал(а) % на остаток", callback_data="debet_percent")],
        [InlineKeyboardButton(text="Да, выдал(а) 2% кэшбэк", callback_data="debet_cashback")],
        [InlineKeyboardButton(text="Без транзакции", callback_data="debet_none")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ])