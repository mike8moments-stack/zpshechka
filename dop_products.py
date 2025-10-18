# keyboards/dop_products.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import MULTIPOLIS_MAP

def tbtn(text: str, key: str, dop_state: dict, hint: str = "", show_checkbox: bool = True) -> InlineKeyboardButton:
    selected = bool(dop_state.get(key))
    if show_checkbox:
        label = f"{'✅' if selected else '⬜️'} {text}{(' ' + hint) if (hint and selected) else ''}"
    else:
        label = f"{text}{(' ' + hint) if (hint and selected) else ''}"
    return InlineKeyboardButton(text=label, callback_data=f"toggle_{key}")

def dop_menu_primary(dop_state: dict) -> InlineKeyboardMarkup:
    if dop_state is None:
        dop_state = {}
    
    # Для мультиполиса показываем сумму если выбрана
    multipolis_hint = ""
    if dop_state.get("multipolis_sum"):
        multipolis_hint = f"+{dop_state['multipolis_sum']}₽"
    
    # Для дебета показываем статус
    debet_hint = ""
    if dop_state.get("debet_selected"):
        debet_sum = dop_state.get("debet_sum", 0)
        if debet_sum > 0:
            debet_hint = f"+{debet_sum}₽"
        else:
            debet_hint = "без транзакции"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [tbtn("📋 ОМП", "omp", dop_state, "+200₽")],
        [tbtn("📱 СМС", "sms", dop_state, "+150₽"),
         tbtn("💳 ВИС (ДБО)", "vis_dbo", dop_state, "+250₽")],
        [tbtn("💳 КРХ", "krh", dop_state, "+100₽"),
         tbtn("💳 Дебет", "debet", dop_state, debet_hint, show_checkbox=False)],
        [InlineKeyboardButton(text="ДК💸 МП🛡 КД👨‍⚕️Вклад", callback_data="open_financial_menu")],
        [tbtn("🐥 Халвёнок", "halvyenok", dop_state, "+150₽")],
        [InlineKeyboardButton(text="✅ Готово", callback_data="done_dop"), 
         InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])

def dop_menu_with_krh_extras(dop_state: dict) -> InlineKeyboardMarkup:
    if dop_state is None:
        dop_state = {}
    
    # Для мультиполиса показываем сумму если выбрана
    multipolis_hint = ""
    if dop_state.get("multipolis_sum"):
        multipolis_hint = f"+{dop_state['multipolis_sum']}₽"
    
    # Для дебета показываем статус
    debet_hint = ""
    if dop_state.get("debet_selected"):
        debet_sum = dop_state.get("debet_sum", 0)
        if debet_sum > 0:
            debet_hint = f"+{debet_sum}₽"
        else:
            debet_hint = "без транзакции"
    
    kb = []
    # Первая строка: ОМП, СМС, ВИС (ДБО) - взаимоисключающие СМС и ВИС ДБО
    first_row = [tbtn("📋 ОМП", "omp", dop_state, "+200₽")]
    
    # Если выбран ВИС ДБО, не показываем СМС, и наоборот
    if dop_state.get("vis_dbo"):
        first_row.append(tbtn("💳 ВИС (ДБО)", "vis_dbo", dop_state, "+250₽"))
    elif dop_state.get("sms"):
        first_row.append(tbtn("📱 СМС", "sms", dop_state, "+150₽"))
    else:
        # Если ничего не выбрано, показываем обе кнопки
        first_row.extend([
            tbtn("📱 СМС", "sms", dop_state, "+150₽"),
            tbtn("💳 ВИС (ДБО)", "vis_dbo", dop_state, "+250₽")
        ])
    
    kb.append(first_row)
    
    # Вторая строка: КРХ и ВИВ КРХ
    kb.append([tbtn("💳 КРХ", "krh", dop_state, "+100₽"), 
               tbtn("💳 ВИВ (КРХ)", "viv_krh", dop_state, "+250₽")])
    
    # Десятка
    if dop_state.get("ep_month"):
        kb.append([tbtn("Десятка ежемесячно", "ep_month", dop_state, "+200₽")])
    elif dop_state.get("ep_year"):
        kb.append([tbtn("Десятка годовая", "ep_year", dop_state, "+500₽")])
    else:
        kb.append([tbtn("Десятка ежемесячно", "ep_month", dop_state, "+200₽"), 
                   tbtn("Десятка годовая", "ep_year", dop_state, "+500₽")])
    
    kb.append([tbtn("💳 Дебет", "debet", dop_state, debet_hint, show_checkbox=False),
               tbtn("🐥 Халвёнок", "halvyenok", dop_state, "+150₽")])
    
    kb.append([InlineKeyboardButton(text="💰 Оборот по Халве", callback_data="input_krh_oborot"),
               InlineKeyboardButton(text="ДК💸 МП🛡 КД👨‍⚕️Вклад", callback_data="open_financial_menu")])
    
    kb.append([InlineKeyboardButton(text="✅ Готово", callback_data="done_dop"), 
               InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def financial_products_menu(dop_state: dict) -> InlineKeyboardMarkup:
    """Меню финансовых продуктов: ДК, Мультиполис, Кредитный доктор, Вклад"""
    if dop_state is None:
        dop_state = {}
    
    # Показываем выбранные статусы
    dk_hint = ""
    if dop_state.get("dk_selected"):
        dk_hint = "✅"
    
    multipolis_hint = ""
    if dop_state.get("multipolis_sum"):
        multipolis_hint = f"+{dop_state['multipolis_sum']}₽"
    
    vklad_hint = ""
    if dop_state.get("vklad_type"):
        vklad_hint = "✅"
    
    kd_hint = ""
    if dop_state.get("kd_type"):
        kd_hint = "✅"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{dk_hint} Денежный кредит (ДК)", callback_data="toggle_dk")],
        [InlineKeyboardButton(text=f"{'✅' if dop_state.get('multipolis') else '⬜️'} Мультиполис {multipolis_hint}", callback_data="toggle_multipolis")],
        [InlineKeyboardButton(text=f"{kd_hint} Кредитный доктор (КД)", callback_data="open_kd_menu")],
        [InlineKeyboardButton(text=f"{vklad_hint} Вклад", callback_data="open_vklad_menu")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main_dop")]
    ])

def vklad_menu(dop_state: dict) -> InlineKeyboardMarkup:
    """Меню вкладов"""
    if dop_state is None:
        dop_state = {}
    
    vklad_type = dop_state.get("vklad_type")
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'✅' if vklad_type == 'vklad_standard' else '⬜️'} Оформление вклада +200₽", 
            callback_data="toggle_vklad_standard"
        )],
        [InlineKeyboardButton(
            text=f"{'✅' if vklad_type == 'vklad_care_1999' else '⬜️'} Забота о вкладе (1 999 руб.) +200₽", 
            callback_data="toggle_vklad_care_1999"
        )],
        [InlineKeyboardButton(
            text=f"{'✅' if vklad_type == 'vklad_care_2999' else '⬜️'} Забота о вкладе (2 999 руб.) +300₽", 
            callback_data="toggle_vklad_care_2999"
        )],
        [InlineKeyboardButton(
            text=f"{'✅' if vklad_type == 'vklad_care_6999' else '⬜️'} Забота о вкладе (6 999 руб.) +500₽", 
            callback_data="toggle_vklad_care_6999"
        )],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_financial_menu")]
    ])

def kd_menu(dop_state: dict) -> InlineKeyboardMarkup:
    """Меню кредитного доктора"""
    if dop_state is None:
        dop_state = {}
    
    kd_type = dop_state.get("kd_type")
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{'✅' if kd_type == 'kd_4999' else '⬜️'} КД 1 этап 4 999 +500₽", 
            callback_data="toggle_kd_4999"
        )],
        [InlineKeyboardButton(
            text=f"{'✅' if kd_type == 'kd_9999' else '⬜️'} КД 1 этап 9 999 +1 000₽", 
            callback_data="toggle_kd_9999"
        )],
        [InlineKeyboardButton(
            text=f"{'✅' if kd_type == 'kd_14999' else '⬜️'} КД 1 этап 14 999 +1 500₽", 
            callback_data="toggle_kd_14999"
        )],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_financial_menu")]
    ])

def multipolis_amount_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора суммы мультиполиса с новыми премиями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 999 ₽ → +200 ₽", callback_data="multipolis_sum_1999")],
        [InlineKeyboardButton(text="2 999 ₽ → +400 ₽", callback_data="multipolis_sum_2999")],
        [InlineKeyboardButton(text="3 999 ₽ → +500 ₽", callback_data="multipolis_sum_3999")],
        [InlineKeyboardButton(text="9 999 ₽ → +1 000 ₽", callback_data="multipolis_sum_9999")],
        [InlineKeyboardButton(text="14 999 ₽ → +1 300 ₽", callback_data="multipolis_sum_14999")],
        [InlineKeyboardButton(text="19 999 ₽ → +1 500 ₽", callback_data="multipolis_sum_19999")],
        [InlineKeyboardButton(text="24 999 ₽ → +1 800 ₽", callback_data="multipolis_sum_24999")],
        [InlineKeyboardButton(text="29 999 ₽ → +2 000 ₽", callback_data="multipolis_sum_29999")],
        [InlineKeyboardButton(text="39 999 ₽ → +2 250 ₽", callback_data="multipolis_sum_39999")],
        [InlineKeyboardButton(text="49 999 ₽ → +2 500 ₽", callback_data="multipolis_sum_49999")],
        [InlineKeyboardButton(text="59 999 ₽ → +3 000 ₽", callback_data="multipolis_sum_59999")],
        [InlineKeyboardButton(text="69 999 ₽ → +3 500 ₽", callback_data="multipolis_sum_69999")],
        [InlineKeyboardButton(text="📝 Другая сумма", callback_data="multipolis_sum_other")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_financial_menu")]
    ])

# Новые клавиатуры для управления записями
def edit_record_kb(record_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования записи"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить сумму", callback_data=f"edit_sum_{record_id}")],
        [InlineKeyboardButton(text="🔧 Изменить допы", callback_data=f"edit_dop_{record_id}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_record_{record_id}")],
        [InlineKeyboardButton(text="📅 К списку дней", callback_data="view_day")],
        [InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])

def confirm_delete_kb(record_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{record_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"day_detail_{record_id}")]
    ])

def week_navigation_kb(year: int, month: int, week_num: int, total_weeks: int) -> InlineKeyboardMarkup:
    """Клавиатура навигации по неделям"""
    kb = []
    
    # Кнопки навигации
    nav_buttons = []
    if week_num > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Пред", callback_data=f"week_{year}_{month}_{week_num-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{week_num}/{total_weeks}", callback_data="current_week"))
    
    if week_num < total_weeks:
        nav_buttons.append(InlineKeyboardButton(text="След ▶️", callback_data=f"week_{year}_{month}_{week_num+1}"))
    
    if nav_buttons:
        kb.append(nav_buttons)
    
    kb.append([InlineKeyboardButton(text="📅 Выбрать другую дату", callback_data="view_day")])
    kb.append([InlineKeyboardButton(text="📈 Общая статистика", callback_data="monthly_stats")])
    kb.append([InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def record_management_kb(record_id: int, show_back_to_day: bool = True) -> InlineKeyboardMarkup:
    """Расширенная клавиатура управления записью"""
    kb = []
    
    # Основные действия
    kb.append([
        InlineKeyboardButton(text="✏️ Изменить сумму", callback_data=f"edit_sum_{record_id}"),
        InlineKeyboardButton(text="🔧 Изменить допы", callback_data=f"edit_dop_{record_id}")
    ])
    
    kb.append([InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_record_{record_id}")])
    
    # Навигация
    if show_back_to_day:
        kb.append([InlineKeyboardButton(text="📅 К списку дней", callback_data="view_day")])
    
    kb.append([InlineKeyboardButton(text="📈 Общая статистика", callback_data="monthly_stats")])
    kb.append([InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def edit_dop_products_kb(record_id: int, dop_state: dict) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования допродуктов"""
    kb = dop_menu_primary(dop_state).inline_keyboard
    
    # Заменяем кнопку "Готово" на "Сохранить изменения"
    for i, row in enumerate(kb):
        for j, button in enumerate(row):
            if button.callback_data == "done_dop":
                kb[i][j] = InlineKeyboardButton(
                    text="💾 Сохранить", 
                    callback_data=f"save_dop_changes_{record_id}"
                )
    
    kb.append([InlineKeyboardButton(text="↩️ Назад", callback_data=f"day_detail_{record_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

# Добавляем недостающую функцию edit_type_kb
def edit_type_kb(record_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для изменения типа выдачи"""
    from keyboards.issues import issue_types_kb
    
    kb = issue_types_kb().inline_keyboard
    kb.append([InlineKeyboardButton(text="↩️ Назад", callback_data=f"day_detail_{record_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)