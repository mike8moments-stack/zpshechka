# handlers/views.py

import logging
import asyncio
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, timedelta
from calendar import monthrange, monthcalendar

from database import (
    db_get_user, db_get_user_records, get_db_session, close_db_session, 
    DailyRecord, User, db_delete_record, db_get_record_by_id, db_update_record,
    db_get_records_by_date_range
)
from keyboards.main import main_menu, home_back_kb
from utils.helpers import safe_send_or_edit, format_currency, issue_type_to_str, set_last_bot_message
from utils.calculations import calc_premia_and_breakdown, apply_regional_coefficient
from states import ZPForm

logger = logging.getLogger(__name__)
router = Router()

# Вспомогательные функции
def get_russian_month_name_nominative(month_number: int) -> str:
    """Возвращает русское название месяца в именительном падеже"""
    months = {
        1: "январь", 2: "февраль", 3: "март", 4: "апрель",
        5: "май", 6: "июнь", 7: "июль", 8: "август",
        9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"
    }
    return months.get(month_number, "")

def get_week_dates(year: int, month: int, week_num: int):
    """Получает даты начала и конца недели"""
    month_cal = monthcalendar(year, month)
    if week_num - 1 < len(month_cal):
        week_days = [day for day in month_cal[week_num - 1] if day != 0]
        if week_days:
            start_date = date(year, month, week_days[0])
            end_date = date(year, month, week_days[-1])
            return start_date, end_date
    return None, None

def get_total_weeks_in_month(year: int, month: int):
    """Получает общее количество недель в месяце"""
    month_cal = monthcalendar(year, month)
    return len([week for week in month_cal if any(week)])

def get_week_days_with_data(year: int, month: int, week_num: int, records):
    """Получает дни недели с данными о премиях"""
    start_date, end_date = get_week_dates(year, month, week_num)
    if not start_date:
        return []
    
    # Создаем список всех дней недели
    current_date = start_date
    week_days = []
    
    while current_date <= end_date:
        # Находим записи за этот день
        day_records = [r for r in records if r.date == current_date]
        day_total = sum(r.total for r in day_records)
        
        week_days.append({
            'date': current_date,
            'total_premia': day_total,
            'has_records': len(day_records) > 0
        })
        
        current_date += timedelta(days=1)
    
    return week_days

# Функции клавиатур
def week_selection_kb():
    """Клавиатура выбора недели для статистики"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from datetime import datetime
    
    current_year = datetime.now().year
    
    kb = []
    
    # Добавляем кнопки для 2025 года
    kb.append([InlineKeyboardButton(text="📅 2025 год", callback_data="select_year_2025")])
    
    # Добавляем кнопки для месяцев 2025 года
    months_2025 = [
        ("Январь 2025", "select_month_2025_1"),
        ("Февраль 2025", "select_month_2025_2"),
        ("Март 2025", "select_month_2025_3"),
        ("Апрель 2025", "select_month_2025_4"),
        ("Май 2025", "select_month_2025_5"),
        ("Июнь 2025", "select_month_2025_6"),
        ("Июль 2025", "select_month_2025_7"),
        ("Август 2025", "select_month_2025_8"),
        ("Сентябрь 2025", "select_month_2025_9"),
        ("Октябрь 2025", "select_month_2025_10"),
        ("Ноябрь 2025", "select_month_2025_11"),
        ("Декабрь 2025", "select_month_2025_12"),
    ]
    
    # Разбиваем на ряды по 3 месяца
    for i in range(0, len(months_2025), 3):
        row = []
        for month_text, callback_data in months_2025[i:i+3]:
            row.append(InlineKeyboardButton(text=month_text, callback_data=callback_data))
        kb.append(row)
    
    kb.append([InlineKeyboardButton(text="📊 Текущий месяц", callback_data="monthly_stats")])
    kb.append([InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def month_weeks_kb(year: int, month: int, total_weeks: int):
    """Клавиатура выбора недели в месяце"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = []
    month_name = get_russian_month_name_nominative(month)
    
    kb.append([InlineKeyboardButton(text=f"🗓️ {month_name} {year}", callback_data="current_month")])
    
    # Создаем кнопки для недель
    week_buttons = []
    for week_num in range(1, total_weeks + 1):
        week_buttons.append(InlineKeyboardButton(
            text=f"Неделя {week_num}", 
            callback_data=f"week_{year}_{month}_{week_num}"
        ))
    
    # Разбиваем на ряды по 2 недели
    for i in range(0, len(week_buttons), 2):
        row = week_buttons[i:i+2]
        kb.append(row)
    
    kb.append([InlineKeyboardButton(text="📅 Выбрать другой месяц", callback_data="select_year_2025")])
    kb.append([InlineKeyboardButton(text="📊 Текущий месяц", callback_data="monthly_stats")])
    kb.append([InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def week_days_kb(year: int, month: int, week_num: int, week_days):
    """Клавиатура с днями недели и премиями"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = []
    
    # Добавляем кнопки для каждого дня недели
    for day_data in week_days:
        day_date = day_data['date']
        day_name = day_date.strftime('%a')  # Сокращенное название дня
        day_formatted = day_date.strftime('%d.%m.%Y')
        premia = day_data['total_premia']
        
        if day_data['has_records']:
            button_text = f"{day_name} {day_formatted} - {format_currency(premia)}"
        else:
            button_text = f"{day_name} {day_formatted} - нет выдач"
        
        kb.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"day_detail_full_{day_date.strftime('%Y-%m-%d')}"
        )])
    
    # Кнопка добавления новой выдачи
    kb.append([InlineKeyboardButton(
        text="➕ Добавить выдачу за день",
        callback_data=f"add_issue_for_week_{year}_{month}_{week_num}"
    )])
    
    # Навигация
    kb.append([InlineKeyboardButton(text="↩️ Назад к неделям", callback_data=f"select_month_{year}_{month}")])
    kb.append([InlineKeyboardButton(text="📊 Общая статистика", callback_data="monthly_stats")])
    kb.append([InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def day_records_kb(day_date, records):
    """Клавиатура с записями за конкретный день"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    kb = []
    
    # Добавляем кнопки для каждой выдачи
    for i, record in enumerate(records, 1):
        kb.append([InlineKeyboardButton(
            text=f"Выдача {i} - {format_currency(record.total)}",
            callback_data=f"record_detail_{record.id}"
        )])
    
    # Кнопка добавления новой выдачи
    kb.append([InlineKeyboardButton(
        text="➕ Добавить выдачу",
        callback_data=f"add_issue_for_date_{day_date}"
    )])
    
    # Навигация
    year = day_date.year
    month = day_date.month
    # Находим номер недели для этого дня
    week_num = get_week_number_for_date(day_date)
    
    kb.append([InlineKeyboardButton(text="↩️ Назад к дням недели", callback_data=f"week_{year}_{month}_{week_num}")])
    kb.append([InlineKeyboardButton(text="📊 Общая статистика", callback_data="monthly_stats")])
    kb.append([InlineKeyboardButton(text="🏠 Домой", callback_data="home")])
    
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_week_number_for_date(target_date):
    """Определяет номер недели в месяце для даты"""
    month_cal = monthcalendar(target_date.year, target_date.month)
    for week_num, week in enumerate(month_cal, 1):
        if target_date.day in week:
            return week_num
    return 1

def record_detail_kb(record_id: int, day_date):
    """Клавиатура для детального просмотра записи"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    year = day_date.year
    month = day_date.month
    week_num = get_week_number_for_date(day_date)
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit_record_{record_id}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_record_{record_id}")],
        [InlineKeyboardButton(text="↩️ Назад к выдачам", callback_data=f"day_detail_full_{day_date.strftime('%Y-%m-%d')}")],
        [InlineKeyboardButton(text="📅 Назад к дням", callback_data=f"week_{year}_{month}_{week_num}")],
        [InlineKeyboardButton(text="🏠 Домой", callback_data="home")]
    ])

def confirm_delete_kb(record_id: int, back_callback: str):
    """Клавиатура подтверждения удаления"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{record_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=back_callback)]
    ])

# ЯВНЫЕ ОБРАБОТЧИКИ ДЛЯ ВСЕХ CALLBACK_DATA СВЯЗАННЫХ С ПРОСМОТРОМ
@router.callback_query(lambda c: c.data in ["monthly_stats", "current_month", "view_day", "help"])
async def common_view_handlers(callback: types.CallbackQuery, state: FSMContext):
    """Общие обработчики для просмотра"""
    if callback.data == "monthly_stats":
        await monthly_stats(callback, state)
    elif callback.data == "current_month":
        await current_month_handler(callback, state)
    elif callback.data == "view_day":
        await view_day(callback, state)
    elif callback.data == "help":
        await help_cb(callback)

@router.callback_query(lambda c: c.data.startswith("select_year_"))
async def select_year_handler(callback: types.CallbackQuery):
    """Обработчик выбора года"""
    await select_year(callback)

@router.callback_query(lambda c: c.data.startswith("select_month_"))
async def select_month_handler(callback: types.CallbackQuery):
    """Обработчик выбора месяца"""
    await select_month(callback)

@router.callback_query(lambda c: c.data.startswith("week_"))
async def week_handler(callback: types.CallbackQuery):
    """Обработчик выбора недели"""
    await week_stats(callback)

@router.callback_query(lambda c: c.data.startswith("day_detail_full_"))
async def day_detail_full_handler(callback: types.CallbackQuery):
    """Обработчик детального просмотра дня"""
    await day_detail_full(callback)

@router.callback_query(lambda c: c.data.startswith("record_detail_"))
async def record_detail_handler(callback: types.CallbackQuery):
    """Обработчик детального просмотра записи"""
    await record_detail(callback)

@router.callback_query(lambda c: c.data.startswith("add_issue_for_date_"))
async def add_issue_for_date_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик добавления выдачи за дату"""
    await add_issue_for_date(callback, state)

@router.callback_query(lambda c: c.data.startswith("add_issue_for_week_"))
async def add_issue_for_week_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик добавления выдачи за неделю"""
    await add_issue_for_week(callback, state)

@router.callback_query(lambda c: c.data.startswith("delete_record_"))
async def delete_record_handler(callback: types.CallbackQuery):
    """Обработчик удаления записи"""
    await delete_record_confirm(callback)

@router.callback_query(lambda c: c.data.startswith("confirm_delete_"))
async def confirm_delete_handler(callback: types.CallbackQuery):
    """Обработчик подтверждения удаления"""
    await delete_record_execute(callback)

# ОСНОВНЫЕ ФУНКЦИИ
async def monthly_stats(callback: types.CallbackQuery, state: FSMContext):
    """Улучшенная статистика за месяц с возможностью выбора недели"""
    await state.clear()
    user = await db_get_user(callback.from_user.id)
    if not user:
        await safe_send_or_edit(callback, "Нет данных — сначала /start", main_menu())
        await callback.answer()
        return
    
    current_date = date.today()
    year = current_date.year
    month = current_date.month
    
    # Получаем записи за текущий месяц
    def _fetch_monthly(uid, year, month):
        session = get_db_session()
        try:
            user = session.query(User).filter(User.id == uid).first()
            if not user:
                return []
            
            start_date = date(year, month, 1)
            end_date = date(year, month, monthrange(year, month)[1])
            
            return session.query(DailyRecord)\
                .filter(DailyRecord.user_id == user.id)\
                .filter(DailyRecord.date >= start_date)\
                .filter(DailyRecord.date <= end_date)\
                .order_by(DailyRecord.date)\
                .all()
        finally:
            close_db_session(session)
    
    records = await asyncio.to_thread(_fetch_monthly, user.id, year, month)
    
    if not records:
        month_name = get_russian_month_name_nominative(month)
        message_text = f"📊 Нет данных за {month_name} {year} года."
        kb = week_selection_kb()
        await safe_send_or_edit(callback, message_text, kb)
        await callback.answer()
        return
    
    # Собираем расширенную статистику
    total_issues = len(records)
    total_sum = sum(rec.summa for rec in records)
    total_prem = sum(rec.total for rec in records)
    total_prem_regional = apply_regional_coefficient(total_prem)
    
    # Статистика по продуктам
    krh_count = sum(1 for rec in records if rec.krh)
    krh_start_count = sum(1 for rec in records if rec.krh_start)
    debet_with_transaction = sum(1 for rec in records if rec.debet_sum and rec.debet_sum > 0)
    vis_dbo_count = sum(1 for rec in records if rec.vis_dbo)
    viv_krh_count = sum(1 for rec in records if rec.viv_krh)
    halvyenok_count = sum(1 for rec in records if rec.halvyenok)
    multipolis_count = sum(1 for rec in records if rec.multipolis_sum and rec.multipolis_sum > 0)
    omp_count = sum(1 for rec in records if rec.omp)
    sms_count = sum(1 for rec in records if rec.sms)
    ep_month_count = sum(1 for rec in records if rec.podpiska_god == False and (rec.omp or rec.sms))
    ep_year_count = sum(1 for rec in records if rec.podpiska_god)
    
    # Дополнительная статистика
    s_fz_count = sum(1 for rec in records if rec.s_fz)
    bez_fz_count = sum(1 for rec in records if not rec.s_fz and not rec.krh)
    dk_count = sum(1 for rec in records if rec.dk_sum and rec.dk_sum > 0)
    krh_oborot_total = sum(rec.krh_oborot_sum for rec in records if rec.krh_oborot_sum)
    ref_total = sum(rec.ref_sum for rec in records if rec.ref_sum)
    
    # Формируем подробное сообщение
    month_name = get_russian_month_name_nominative(month)
    lines = []
    lines.append(f"📈 Статистика за {month_name} {year} года")
    lines.append("")
    
    # Основные показатели
    lines.append("💰 Основные показатели:")
    lines.append(f"• Выдач: {total_issues}")
    lines.append(f"• Общая сумма: <code>{format_currency(total_sum)}</code>")
    lines.append(f"• Премия: <code>{format_currency(total_prem)}</code>")
    lines.append(f"• Премия с учётом регионального коэффициента (×1.3): <b><code>{format_currency(total_prem_regional)}</code></b>")
    lines.append("")
    
    # Типы выдач
    lines.append("🧾 Типы выдач:")
    lines.append(f"• Кредиты с ФЗ: {s_fz_count}")
    lines.append(f"• Кредиты без ФЗ: {bez_fz_count}")
    lines.append(f"• КРХ: {krh_count}")
    if dk_count > 0:
        lines.append(f"• ДК: {dk_count}")
    lines.append("")
    
    # Допродажи
    lines.append("🔧 Допродажи:")
    if krh_start_count > 0:
        lines.append(f"• КРХ старт: {krh_start_count}")
    if debet_with_transaction > 0:
        lines.append(f"• Дебет с транзакцией: {debet_with_transaction}")
    if vis_dbo_count > 0:
        lines.append(f"• ВИС (ДБО): {vis_dbo_count}")
    if viv_krh_count > 0:
        lines.append(f"• ВИВ (КРХ): {viv_krh_count}")
    if halvyenok_count > 0:
        lines.append(f"• Халвёнок: {halvyenok_count}")
    if multipolis_count > 0:
        lines.append(f"• Мультиполисы: {multipolis_count}")
    if omp_count > 0:
        lines.append(f"• ОМП: {omp_count}")
    if sms_count > 0:
        lines.append(f"• СМС: {sms_count}")
    if ep_month_count > 0:
        lines.append(f"• Подписок ежемесячных: {ep_month_count}")
    if ep_year_count > 0:
        lines.append(f"• Подписок годовых: {ep_year_count}")
    
    # Дополнительные суммы
    if krh_oborot_total > 0:
        lines.append(f"• Оборот КРХ: <code>{format_currency(krh_oborot_total)}</code>")
    if ref_total > 0:
        lines.append(f"• Рефинансирование: <code>{format_currency(ref_total)}</code>")
    
    # Если нет допродаж
    if all(count == 0 for count in [krh_start_count, debet_with_transaction, vis_dbo_count, viv_krh_count, 
                                   halvyenok_count, multipolis_count, omp_count, sms_count, ep_month_count, 
                                   ep_year_count, krh_oborot_total, ref_total]):
        lines.append("• Нет допродаж")
    
    message_text = "\n".join(lines)
    
    # Создаем клавиатуру с выбором недели
    total_weeks = get_total_weeks_in_month(year, month)
    kb = month_weeks_kb(year, month, total_weeks)
    
    await safe_send_or_edit(callback, message_text, kb)
    await callback.answer()

async def current_month_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик для кнопки текущего месяца"""
    await monthly_stats(callback, state)

async def select_year(callback: types.CallbackQuery):
    """Обработчик выбора года"""
    year = int(callback.data.split("_")[-1])
    
    if year == 2025:
        kb = week_selection_kb()
        await safe_send_or_edit(callback, f"📅 Выберите месяц {year} года:", kb)
    else:
        await callback.answer("Доступен только 2025 год")
    
    await callback.answer()

async def select_month(callback: types.CallbackQuery):
    """Обработчик выбора месяца"""
    parts = callback.data.split("_")
    year = int(parts[2])
    month = int(parts[3])
    
    total_weeks = get_total_weeks_in_month(year, month)
    month_name = get_russian_month_name_nominative(month)
    
    kb = month_weeks_kb(year, month, total_weeks)
    await safe_send_or_edit(callback, f"🗓️ Выберите неделю в {month_name} {year}:", kb)
    await callback.answer()

async def week_stats(callback: types.CallbackQuery):
    """Отображение дней недели с премиями"""
    parts = callback.data.split("_")
    year = int(parts[1])
    month = int(parts[2])
    week_num = int(parts[3])
    
    user = await db_get_user(callback.from_user.id)
    if not user:
        await callback.answer("Нет данных")
        return
    
    start_date, end_date = get_week_dates(year, month, week_num)
    if not start_date:
        await callback.answer("Неделя не найдена")
        return
    
    # Получаем записи за эту неделю
    records = await db_get_records_by_date_range(callback.from_user.id, start_date, end_date)
    
    # Получаем дни недели с данными
    week_days = get_week_days_with_data(year, month, week_num, records)
    
    month_name = get_russian_month_name_nominative(month)
    lines = []
    lines.append(f"📊 Неделя {week_num} ({month_name} {year})")
    lines.append(f"📅 Период: {start_date.strftime('%d.%m')} - {end_date.strftime('%d.%m.%Y')}")
    lines.append("")
    lines.append("Выберите день для просмотра деталей:")
    
    # Добавляем информацию по дням
    for day_data in week_days:
        day_date = day_data['date']
        day_name = day_date.strftime('%a')
        day_formatted = day_date.strftime('%d.%m.%Y')
        
        if day_data['has_records']:
            lines.append(f"• {day_name} {day_formatted} - {format_currency(day_data['total_premia'])}")
        else:
            lines.append(f"• {day_name} {day_formatted} - нет выдач")
    
    total_weeks = get_total_weeks_in_month(year, month)
    kb = week_days_kb(year, month, week_num, week_days)
    
    await safe_send_or_edit(callback, "\n".join(lines), kb)
    await callback.answer()

async def day_detail_full(callback: types.CallbackQuery):
    """Детальный просмотр всех выдач за день"""
    day_str = callback.data.replace("day_detail_full_", "")
    
    user = await db_get_user(callback.from_user.id)
    if not user:
        await callback.answer("Нет данных")
        return
    
    def _fetch_day(uid, day_str):
        session = get_db_session()
        try:
            user = session.query(User).filter(User.id == uid).first()
            if not user:
                return []
            
            target_date = datetime.strptime(day_str, "%Y-%m-%d").date()
            return session.query(DailyRecord)\
                .filter(DailyRecord.user_id == user.id)\
                .filter(DailyRecord.date == target_date)\
                .order_by(DailyRecord.id)\
                .all()
        finally:
            close_db_session(session)
    
    records = await asyncio.to_thread(_fetch_day, user.id, day_str)
    day_date = datetime.strptime(day_str, "%Y-%m-%d").date()
    
    lines = []
    lines.append(f"📅 {day_date.strftime('%d.%m.%Y')}")
    lines.append("")
    
    if not records:
        lines.append("📭 Выдач за этот день нет")
        lines.append("")
        lines.append("Нажмите '➕ Добавить выдачу' чтобы создать первую запись за этот день")
    else:
        total_premia = sum(rec.total for rec in records)
        total_premia_regional = apply_regional_coefficient(total_premia)
        
        lines.append(f"💰 Общая премия за день: <b><code>{format_currency(total_premia)}</code></b>")
        lines.append(f"💰 С коэффициентом: <b><code>{format_currency(total_premia_regional)}</code></b>")
        lines.append("")
        lines.append("📋 Список выдач:")
        
        for i, rec in enumerate(records, 1):
            product_type = "КРХ" if rec.krh else "Кредит (С ФЗ)" if rec.s_fz else "Кредит (Без ФЗ)"
            lines.append(f"{i}. {product_type} - {format_currency(rec.summa)} → {format_currency(rec.total)}")
    
    kb = day_records_kb(day_date, records)
    await safe_send_or_edit(callback, "\n".join(lines), kb)
    await callback.answer()

async def record_detail(callback: types.CallbackQuery):
    """Детальный просмотр одной выдачи"""
    record_id = int(callback.data.split("_")[-1])
    
    rec = await db_get_record_by_id(record_id)
    if not rec:
        await callback.answer("Запись не найдена")
        return
    
    lines = []
    lines.append(f"📅 {rec.date.strftime('%d.%m.%Y')}")
    lines.append("")
    
    # Тип продукта
    if rec.krh:
        product_type = "КРХ"
    elif rec.s_fz:
        product_type = "Кредит (С ФЗ)"
    else:
        product_type = "Кредит (Без ФЗ)"
    
    lines.append(f"🧾 <b>Тип выдачи:</b> {product_type}")
    lines.append(f"💸 <b>Сумма:</b> <code>{format_currency(rec.summa)}</code>")
    lines.append("")
    
    # Допродажи
    lines.append("🔧 <b>Допродажи:</b>")
    
    dop_products = []
    if rec.omp: dop_products.append(("ОМП", 200))
    if rec.sms: dop_products.append(("СМС", 150))
    if rec.vis_dbo: dop_products.append(("ВИС (ДБО)", 250))
    if rec.viv_krh: dop_products.append(("ВИВ (КРХ)", 250))
    if rec.krh_vydacha: dop_products.append(("КРХ как доп. продажа", 100))
    if rec.krh_start: dop_products.append(("Стартовая премия КРХ", 450))
    if rec.krh_oborot_sum > 0: dop_products.append((f"Оборот КРХ ({rec.krh_oborot_sum}₽)", min(rec.krh_oborot_sum * 0.02, 1000)))
    if rec.podpiska_god: dop_products.append(("Подписка годовая", 500))
    if rec.komp: dop_products.append(("Комплект/КРХ", 200))
    if rec.vse_vezde: dop_products.append(("Всё и везде", 200))
    if rec.sticker: dop_products.append(("Стикер", 50))
    if rec.ref_sum > 0: dop_products.append((f"Рефинансирование ({rec.ref_sum}₽)", min(rec.ref_sum * 0.01, 350)))
    if rec.dk_sum > 0: dop_products.append((f"ДК ({rec.dk_type})", rec.dk_sum))
    if rec.multipolis_sum > 0: 
        from config import MULTIPOLIS_MAP
        multipolis_reward = 0
        for k in sorted(MULTIPOLIS_MAP.keys()):
            if rec.multipolis_sum >= k:
                multipolis_reward = MULTIPOLIS_MAP[k]
        dop_products.append((f"Мультиполис ({rec.multipolis_sum}₽)", multipolis_reward))
    if rec.debet_sum > 0: dop_products.append((f"Дебет ({rec.debet_type})", rec.debet_sum))
    if rec.halvyenok: dop_products.append(("Халвёнок", 150))
    
    if dop_products:
        for name, amount in dop_products:
            lines.append(f"• {name} → <code>+{format_currency(amount)}</code>")
    else:
        lines.append("• Нет допродаж")
    
    lines.append("")
    lines.append(f"💰 <b>ИТОГО ПРЕМИИ:</b> <code>{format_currency(rec.total)}</code>")
    lines.append(f"💰 <b>С коэффициентом:</b> <code>{format_currency(apply_regional_coefficient(rec.total))}</code>")
    
    kb = record_detail_kb(record_id, rec.date)
    await safe_send_or_edit(callback, "\n".join(lines), kb)
    await callback.answer()

async def add_issue_for_date(callback: types.CallbackQuery, state: FSMContext):
    """Добавление выдачи за конкретную дату"""
    day_str = callback.data.replace("add_issue_for_date_", "")
    target_date = datetime.strptime(day_str, "%Y-%m-%d").date()
    
    # Сохраняем дату в состоянии
    await state.update_data(target_date=target_date)
    
    from handlers.issues import new_issue
    await new_issue(callback, state)

async def add_issue_for_week(callback: types.CallbackQuery, state: FSMContext):
    """Добавление выдачи за текущий день (сегодня) при нажатии из недели"""
    parts = callback.data.split("_")
    year = int(parts[3])
    month = int(parts[4])
    week_num = int(parts[5])
    
    # Используем сегодняшнюю дату
    target_date = date.today()
    
    # Сохраняем дату в состоянии
    await state.update_data(target_date=target_date)
    
    from handlers.issues import new_issue
    await new_issue(callback, state)

async def delete_record_confirm(callback: types.CallbackQuery):
    """Подтверждение удаления записи"""
    record_id = int(callback.data.split("_")[-1])
    
    rec = await db_get_record_by_id(record_id)
    if not rec:
        await callback.answer("Запись не найдена")
        return
    
    # Определяем callback для возврата
    back_callback = f"record_detail_{record_id}"
    
    lines = []
    lines.append("❓ <b>Подтверждение удаления</b>")
    lines.append(f"📅 {rec.date.strftime('%d.%m.%Y')}")
    lines.append(f"💸 Сумма: <code>{format_currency(rec.summa)}</code>")
    lines.append(f"💰 Премия: <code>{format_currency(rec.total)}</code>")
    lines.append("")
    lines.append("Вы уверены, что хотите удалить эту запись?")
    
    kb = confirm_delete_kb(record_id, back_callback)
    await safe_send_or_edit(callback.message, "\n".join(lines), kb)
    await callback.answer()

async def delete_record_execute(callback: types.CallbackQuery):
    """Выполнение удаления записи"""
    record_id = int(callback.data.split("_")[-1])
    
    # Получаем запись перед удалением чтобы знать дату
    rec = await db_get_record_by_id(record_id)
    if not rec:
        await callback.answer("Запись не найдена")
        return
    
    success = await db_delete_record(record_id)
    
    if success:
        await callback.answer("✅ Запись удалена")
        # Возвращаем к списку выдач за день
        await day_detail_full(callback)
    else:
        await callback.answer("❌ Ошибка при удалении")

async def view_day(callback: types.CallbackQuery, state: FSMContext):
    """Просмотр дней с записями (старая функция для совместимости)"""
    await state.clear()
    user = await db_get_user(callback.from_user.id)
    if not user:
        await safe_send_or_edit(callback, "Нет данных — сначала /start", main_menu())
        await callback.answer()
        return
        
    # Перенаправляем на выбор недели
    kb = week_selection_kb()
    await safe_send_or_edit(callback, "📊 Выберите период для просмотра:", kb)
    await callback.answer()

async def help_cb(callback: types.CallbackQuery):
    """Помощь"""
    help_text = (
        "ℹ️ <b>Помощь по боту</b>\n\n"
        "📝 <b>Создание выдачи:</b>\n"
        "- Нажмите 'Новая выдача' и следуйте шагам\n"
        "- Введите суммы цифрами (например: 150000)\n"
        "- Рассрочка: при выборе с ФЗ — +1% от суммы рассрочки; без ФЗ — 0%\n"
        "- Дебет доступен и в выборе типа, и в меню доп. продуктов\n\n"
        "📊 <b>Статистика:</b>\n"
        "- Просмотр статистики за месяц и недели\n"
        "- Детализация по дням и отдельным выдачам\n"
        "- Редактирование и удаление записей\n\n"
        "🔧 <b>Управление:</b>\n"
        "- Изменение суммы, типа и допродуктов\n"
        "- Удаление ошибочных записей\n"
        "- Навигация по неделям 2025 года"
    )
    
    await safe_send_or_edit(callback, help_text, main_menu())
    await callback.answer()