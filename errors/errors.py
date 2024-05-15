from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states.user_states import FSMUser
from keyboards.inline_keyboards import MenuCallBack, get_callback_btns
from lexicon.lexicon_ru import lexicon_for_bot
from typing import Type


# Меню для неверных значений
async def wrong_content(state: FSMContext, message: Message, user_state: Type[FSMUser], text: str):
    await state.set_state(user_state.work)
    state_data = await state.get_data()
    start_msg_id = state_data['start_msg_id']
    current_msg_id = message.message_id
    await message.bot.delete_messages(chat_id=message.chat.id,
                                      message_ids=[i for i in range(start_msg_id, current_msg_id)]
                                      )
    await state.update_data(start_msg_id=message.message_id)
    await message.answer(text=text,
                         reply_markup=get_callback_btns(
                             btns={
                                 lexicon_for_bot['try_again']: MenuCallBack(menu_name='lets_work').pack(),
                                 lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack(),
                             },
                             sizes=(1, 1)
                         )
                         )
