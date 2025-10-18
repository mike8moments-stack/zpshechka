# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///zp_bot.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Константы для расчетов
POS_DBO_BY_TERM = {"0-6": 150, "7-12": 150, "13-23": 200, "24-30": 200, "31-36": 250}

# ОБНОВЛЕННЫЕ ПРЕМИИ МУЛЬТИПОЛИСА
MULTIPOLIS_MAP = {
    1999: 200,
    2999: 400, 
    3999: 500,
    9999: 1000,
    14999: 1300,
    19999: 1500,
    24999: 1800,
    29999: 2000,
    39999: 2250,
    49999: 2500,
    59999: 3000,
    69999: 3500
}

RATE_OPTIONS = ["25", "26", "29.9", "32"]
MULTIPOLIS_CHOICES = [1999, 2999, 3999, 9999, 14999, 19999, 24999, 29999, 39999, 49999, 59999, 69999]

DK_TYPES = {
    "dk_dk_s_fz": "ДК с ФЗ",
    "dk_dk_mkk_no_fz": "ДК МКК (без ФЗ)",
    "dk_dk_mkk_with_fz": "ДК МКК (с ФЗ)",
    "dk_refinance_krh": "Рефинансирование КРХ",
    "dk_knk_lead_fz": "КНК через ЛИД с ФЗ",
    "dk_ipoteka_ref": "Ипотека/Реф ипотеки",
    "dk_dkpzn": "ДКПЗН",
    "dk_autocredit": "Автокредит/ДКПЗА",
}

# Новые константы для вкладов
VKLAD_TYPES = {
    "vklad_standard": "Оформление вклада",
    "vklad_care_1999": "Забота о вкладе (1 999 руб.)", 
    "vklad_care_2999": "Забота о вкладе (2 999 руб.)",
    "vklad_care_6999": "Забота о вкладе (6 999 руб.)",
}

VKLAD_REWARDS = {
    "vklad_standard": 200,
    "vklad_care_1999": 200,
    "vklad_care_2999": 300,
    "vklad_care_6999": 500,
}

# Константы для кредитного доктора
KD_TYPES = {
    "kd_4999": "КД 1 этап 4 999",
    "kd_9999": "КД 1 этап 9 999", 
    "kd_14999": "КД 1 этап 14 999",
}

KD_REWARDS = {
    "kd_4999": 500,
    "kd_9999": 1000,
    "kd_14999": 1500,
}