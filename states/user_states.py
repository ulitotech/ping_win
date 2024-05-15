from aiogram.fsm.state import State, StatesGroup


class FSMUser(StatesGroup):
    work = State()
    iccid = State()
    server = State()
    sms = State()
    ip = State()
    start_msg_id = State()
