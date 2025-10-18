from aiogram.fsm.state import State, StatesGroup

class ZPForm(StatesGroup):
    waiting_for_name = State()
    choose_issue_type = State()
    choose_term = State()
    choose_rate = State()
    waiting_for_amount = State()
    in_dopprodazhi = State()
    waiting_for_krh_oborot = State()
    waiting_for_dk_sum = State()
    waiting_for_ref_sum = State()
    waiting_for_multipolis_sum = State()