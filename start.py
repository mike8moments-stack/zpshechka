# handlers/start.py

import logging
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import db_get_user, db_create_user
from keyboards.main import main_menu
from utils.helpers import safe_send_or_edit, set_last_bot_message

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    user = await db_get_user(message.from_user.id)
    if not user:
        user = await db_create_user(message.from_user.id, message.from_user.full_name or str(message.from_user.id))
        logger.info(f"Создан новый пользователь: {user.name} (ID: {user.telegram_id})")
    
    welcome_text = (
        "👋 <b>Добро пожаловать в бот для учёта премий!</b>\n\n"
        "💼 <b>Основные возможности:</b>\n"
        "• 📝 Учёт выдач кредитов и допродаж\n"
        "• 💰 Автоматический расчёт премий\n"
        "• 📊 Детальная статистика по дням и неделям\n"
        "• 🔧 Управление записями (изменение, удаление)\n"
        "• 📈 Просмотр статистики за любой период\n\n"
        "🚀 <b>Начните работу:</b>\n"
        "• Нажмите <b>«Новая выдача»</b> для добавления записи\n"
        "• Используйте <b>«Статистика»</b> для просмотра отчётов\n"
        "• <b>«Помощь»</b> — подробное описание функций"
    )
    
    message = await safe_send_or_edit(message, welcome_text, main_menu())
    set_last_bot_message(message)

@router.message(Command("help"))
async def cmd_help(message: types.Message, state: FSMContext):
    await state.clear()
    
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
        "- Навигация по неделям 2025 года\n\n"
        "💡 <b>Советы:</b>\n"
        "- Всегда проверяйте итоговую сумму перед сохранением\n"
        "- Используйте статистику для анализа эффективности\n"
        "- Редактируйте записи при обнаружении ошибок"
    )
    
    message = await safe_send_or_edit(message, help_text, main_menu())
    set_last_bot_message(message)