# utils/helpers.py

import logging
from typing import Optional, Union
from aiogram import types
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения последнего сообщения бота
_last_bot_message = None


def set_last_bot_message(message: types.Message):
    """Устанавливает последнее сообщение бота"""
    global _last_bot_message
    _last_bot_message = message


def get_last_bot_message():
    """Возвращает последнее сообщение бота"""
    return _last_bot_message


async def safe_send_or_edit(
    message: Union[types.Message, types.CallbackQuery],
    text: str,
    reply_markup=None,
    parse_mode: str = "HTML",
) -> types.Message:
    """
    Безопасно отправляет или редактирует сообщение.
    Всегда старается редактировать последнее сообщение, если возможно.
    """
    global _last_bot_message

    try:
        # Определяем chat_id и message_to_edit в зависимости от типа
        if isinstance(message, types.CallbackQuery):
            chat_id = message.message.chat.id
            message_to_edit = message.message
        else:
            chat_id = message.chat.id
            message_to_edit = message

        # Если есть предыдущее сообщение от бота — пробуем редактировать
        if _last_bot_message and isinstance(_last_bot_message, types.Message) and _last_bot_message.chat.id == chat_id:
            try:
                edited_msg = await _last_bot_message.edit_text(
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode,
                )
                set_last_bot_message(edited_msg)
                return edited_msg
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    # Сообщение не изменилось
                    return _last_bot_message
                elif "message can't be edited" in str(e):
                    logger.debug("Message can't be edited, sending new one")
                else:
                    logger.warning(f"Error editing message: {e}")

        # Если редактирование не удалось — отправляем новое
        if isinstance(message, types.CallbackQuery):
            new_msg = await message.message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        else:
            new_msg = await message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )

        set_last_bot_message(new_msg)
        return new_msg

    except Exception as e:
        logger.error(f"Unexpected error in safe_send_or_edit: {e}", exc_info=True)

        # Fallback — всегда отправляем новое сообщение
        chat_id = (
            message.message.chat.id if isinstance(message, types.CallbackQuery)
            else message.chat.id
        )
        sent = await message.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
        set_last_bot_message(sent)
        return sent


async def delete_user_message(message: types.Message):
    """Удаляет сообщение пользователя"""
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Could not delete user message: {e}")


def format_currency(amount: float) -> str:
    """Форматирует сумму в рублях"""
    return f"{int(amount):,}₽".replace(",", " ")


def parse_int_from_text(text: str) -> Optional[int]:
    """Извлекает число из текста"""
    try:
        cleaned = "".join(c for c in text if c.isdigit() or c == "-")
        if cleaned and cleaned != "-":
            return int(cleaned)
        return None
    except (ValueError, TypeError):
        return None


def issue_type_to_str(issue_type: str) -> str:
    """Преобразует тип выдачи в читаемую строку"""
    types_map = {
        "s_fz": "Кредит с ФЗ",
        "bez_fz": "Кредит без ФЗ",
        "krh": "КРХ",
        "rassrochka_s_fz": "Рассрочка с ФЗ",
        "rassrochka_no_fz": "Рассрочка без ФЗ",
        "rass_with": "Рассрочка с ФЗ",
        "rass_without": "Рассрочка без ФЗ",
        "debet": "Дебет",
        "multipolis": "Мультиполис",
        "dk": "ДК",
    }
    return types_map.get(issue_type, issue_type)


def get_russian_month_name(month_number: int) -> str:
    """Возвращает русское название месяца в родительном падеже"""
    months = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }
    return months.get(month_number, "")
