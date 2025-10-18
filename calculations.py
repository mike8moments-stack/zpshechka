# utils/calculations.py
from typing import List, Tuple, Optional, Dict, Any
from config import POS_DBO_BY_TERM, MULTIPOLIS_MAP
from .helpers import format_currency

def calc_premia_and_breakdown(summa: int, dop: dict, term: Optional[str], 
                             rate: Optional[str], data: dict) -> Tuple[float, List[Tuple[str, float]]]:
    premia = 0.0
    breakdown = []
    issue_type = data.get("issue_type")
    
    # Базовая премия
    if issue_type in ("s_fz", "bez_fz"):
        base_prem = min(summa * 0.02, 5000)
    elif issue_type == "krh":
        base_prem = 100 if (dop.get("krh_selected") or dop.get("krh")) else 0
    elif issue_type in ("rassrochka_s_fz", "rass_with"):
        base_prem = min(summa * 0.01, 5000)
    elif issue_type in ("rassrochka_no_fz", "rass_without"):
        base_prem = 0
    else:
        base_prem = 0
        
    if base_prem:
        premia += base_prem
        breakdown.append(("Базовая премия", base_prem))
    
    # Фиксированные допы
    fixed_dops = [
        ("omp", "ОМП", 200),
        ("sms", "СМС", 150),
        ("vis_dbo", "ВИС (ДБО)", 250),
        ("viv_krh", "ВИВ (КРХ)", 250),
        ("komp", "Комплект/КРХ", 200),
        ("ep_month", "Десятка ежемесячно", 200),
        ("ep_year", "Десятка годовая", 500),
        ("vse_vezde", "Всё и везде", 200),
        ("sticker", "Стикер", 50),
        ("halvyenok", "Халвёнок", 150),
    ]
    
    for key, name, amount in fixed_dops:
        if dop.get(key):
            premia += amount
            breakdown.append((name, amount))
    
    # Дебет
    if dop.get("debet_selected"):
        debet_sum = int(dop.get("debet_sum", 0) or 0)
        if debet_sum:
            premia += debet_sum
            breakdown.append(("Дебет", debet_sum))
        else:
            breakdown.append(("Дебет (без транзакции)", 0))
    
    # POS-DBO
    if (dop.get("krh_selected") or dop.get("krh") or dop.get("komp")) and term:
        pos_reward = POS_DBO_BY_TERM.get(term, 0)
        if pos_reward:
            premia += pos_reward
            breakdown.append((f"POS-DBO (по сроку {term})", pos_reward))
    
    # Оборот КРХ
    if dop.get("krh_oborot_sum"):
        krh_ob = dop["krh_oborot_sum"]
        add = min(krh_ob * 0.02, 1000)
        premia += add
        breakdown.append(("Оборот КРХ (2%)", add))
        
        if krh_ob >= 2000:
            premia += 450
            breakdown.append(("Стартовая премия КРХ (>=2000)", 450))
    
    # ДК
    dk_type = dop.get("dk_type")
    if dk_type:
        dk_sum_val = int(dop.get("dk_sum", 0) or 0)
        
        dk_calculations = {
            "dk_dk_s_fz": ("ДК с ФЗ (1.5%)", min(dk_sum_val * 0.015, 5000)),
            "dk_knk_lead_fz": ("КНК через ЛИД (0.5%)", min(dk_sum_val * 0.005, 5000)),
            "dk_dk_mkk_with_fz": ("ДК МКК (с ФЗ)", 1500),
            "dk_dk_mkk_no_fz": ("ДК МКК (без ФЗ)", 1000),
            "dk_ipoteka_ref": ("Ипотека/Реф ипотеки", 7000),
            "dk_dkpzn": ("ДКПЗН", 2000),
            "dk_autocredit": ("Автокредит/ДКПЗА", 1250),
        }
        
        if dk_type in dk_calculations:
            name, add = dk_calculations[dk_type]
            premia += add
            breakdown.append((name, add))
        elif dk_type == "dk_refinance_krh":
            ref_sum_val = int(data.get("ref_sum", 0) or 0)
            add = min(ref_sum_val * 0.01, 350)
            premia += add
            breakdown.append(("Рефинансирование (1%)", add))
    
    # Мультиполис
    multipolis_sum = int(dop.get("multipolis_sum", 0) or 0)
    if multipolis_sum:
        for k in sorted(MULTIPOLIS_MAP.keys()):
            if multipolis_sum >= k:
                multipolis_reward = MULTIPOLIS_MAP[k]
                premia += multipolis_reward
                breakdown.append(("Мультиполис", multipolis_reward))
                break
    
    # Вклад (новый функционал)
    vklad_type = dop.get("vklad_type")
    if vklad_type:
        vklad_calculations = {
            "vklad_standard": ("Оформление вклада", 200),
            "vklad_care_1999": ("Забота о вкладе (1 999 руб.)", 200),
            "vklad_care_2999": ("Забота о вкладе (2 999 руб.)", 300),
            "vklad_care_6999": ("Забота о вкладе (6 999 руб.)", 500),
        }
        if vklad_type in vklad_calculations:
            name, add = vklad_calculations[vklad_type]
            premia += add
            breakdown.append((name, add))
    
    # Кредитный доктор (новый функционал)
    kd_type = dop.get("kd_type")
    if kd_type:
        kd_calculations = {
            "kd_4999": ("КД 1 этап 4 999", 500),
            "kd_9999": ("КД 1 этап 9 999", 1000),
            "kd_14999": ("КД 1 этап 14 999", 1500),
        }
        if kd_type in kd_calculations:
            name, add = kd_calculations[kd_type]
            premia += add
            breakdown.append((name, add))
    
    return premia, breakdown

def build_summary_text(summa: int, dop: dict, term: Optional[str], rate: Optional[str], data: dict) -> str:
    from .helpers import format_currency, issue_type_to_str
    
    premia, breakdown = calc_premia_and_breakdown(summa, dop, term, rate, data)
    
    lines = []
    lines.append("💠 <b>Основная информация</b>")
    lines.append(f"📌 Сумма: <code>{format_currency(summa)}</code>")
    
    if data.get("issue_type"):
        it = data.get("issue_type")
        lines.append(f"🧾 Продукт: {issue_type_to_str(it)}")
    
    if term:
        lines.append(f"⏳ Срок: {term} мес")
    if rate:
        lines.append(f"📈 Ставка: {rate}%")
    
    lines.append("")
    lines.append("🔧 <b>Доп. продукты и суммы</b>")
    
    if breakdown:
        for name, amt in breakdown:
            lines.append(f"• {name} → <code>+{format_currency(amt)}</code>")
    else:
        lines.append("• — Пока нет доп. продуктов")
    
    lines.append("")
    lines.append("💰 <b>Текущая премия:</b> <code>{}</code>".format(format_currency(premia)))
    
    return "\n".join(lines)

def apply_regional_coefficient(amount: float, coefficient: float = 1.3) -> float:
    return amount * coefficient

def format_with_regional_coefficient(amount: float, coefficient: float = 1.3) -> str:
    regional_amount = apply_regional_coefficient(amount, coefficient)
    return f"{format_currency(amount)} × {coefficient} = {format_currency(regional_amount)}"