from aiogram import Router, F
from aiogram.filters import StateFilter, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union
from database.orm_query import get_sim, get_devices, sms_parameters, get_help, add_task
from errors.errors import wrong_content
from filters.filters import IsUser
from keyboards.inline_keyboards import get_callback_btns, MenuCallBack, DeviceCallBack, get_devices_pagination, \
    PaginationCallBack
from states.user_states import FSMUser
from utils.image_processing import get_numeric_code_from_image, iccid_to_correct_form
from utils.ping_processing import connection_test
from lexicon.lexicon_ru import lexicon_for_bot
user_router = Router()
user_router.message.filter(IsUser())

logger.add("log_file.log", retention="5 days")


# Завершение работы бота
@user_router.message(Command('exit'), ~StateFilter(default_state))
async def goodbye(message: Message, state: FSMContext):
    await message.bot.delete_messages(chat_id=message.chat.id, message_ids=[message.message_id, message.message_id - 1])
    await state.set_state(default_state)
    await state.update_data(kill_process=0)
    logger.info(f"Пользователь: {message.from_user.id} вышел из бота")


# Не тревожить при работе сервера
@user_router.message(StateFilter(FSMUser.server))
async def skip_while_server(message: Message):
    await message.delete()
    logger.info(f"Пользователь: {message.from_user.id} проявил активность при работе сервера")


# Главное меню
@user_router.message(Command('start'), StateFilter(default_state))
@user_router.callback_query(MenuCallBack.filter(F.menu_name == 'main'),
                            or_f(StateFilter(FSMUser.work, FSMUser.iccid, FSMUser.sms)))
async def main_menu(income: Union[CallbackQuery, Message], state: FSMContext):
    await state.clear()
    await state.set_state(FSMUser.work)
    if isinstance(income, CallbackQuery):
        await state.update_data(start_msg_id=income.message.message_id)
        await income.message.edit_text(
            text='Главное меню:',
            reply_markup=get_callback_btns(
                btns={
                    lexicon_for_bot['start']: MenuCallBack(menu_name='lets_work').pack(),
                    lexicon_for_bot['help']: MenuCallBack(menu_name='help').pack()
                },
                sizes=(1, 1)
            )
        )
    elif isinstance(income, Message):
        await state.update_data(start_msg_id=income.message_id)
        await income.answer(
            text='Главное меню:',
            reply_markup=get_callback_btns(
                btns={
                    lexicon_for_bot['start']: MenuCallBack(menu_name='lets_work').pack(),
                    lexicon_for_bot['help']: MenuCallBack(menu_name='help').pack()
                },
                sizes=(1, 1)
            )
        )
    logger.info(f"Пользователь: {income.from_user.id} перешел в главное меню")


# Меню выбора справки
@user_router.callback_query(MenuCallBack.filter(F.menu_name == 'help'), StateFilter(FSMUser.work))
async def user_help_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        text=lexicon_for_bot['choice_help'],
        reply_markup=get_callback_btns(
            btns={
                lexicon_for_bot['help_gsm']: MenuCallBack(menu_name='help_gsm').pack(),
                lexicon_for_bot['help_bot']: MenuCallBack(menu_name='help_bot').pack(),
                lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack()
            },
            sizes=(1, 1, 1)
        )
    )
    logger.info(f"Пользователь: {callback_query.from_user.id} перешел в меню выбора справки")


# Меню справки по боту
@user_router.callback_query(MenuCallBack.filter(F.menu_name == 'help_bot'), StateFilter(FSMUser.work))
async def user_help_bot(callback_query: CallbackQuery, session: AsyncSession):
    help_bot_text = await get_help(session=session, help_name='description')
    await callback_query.message.edit_text(
        text=help_bot_text,
        reply_markup=get_callback_btns(
            btns={
                lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack()
            },
            sizes=(1, 1)
        )
    )
    logger.info(f"Пользователь: {callback_query.from_user.id} перешел в справку по боту")


# Меню справки по настройке gsm устройств
@user_router.callback_query(MenuCallBack.filter(F.menu_name == 'help_gsm'), StateFilter(FSMUser.work))
async def user_help_gsm(callback_query: CallbackQuery, session: AsyncSession):
    help_gsm_text = await get_help(session=session, help_name='support')
    await callback_query.message.edit_text(
        text=help_gsm_text,
        reply_markup=get_callback_btns(
            btns={
                lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack()
            },
            sizes=(1, 1)
        )
    )
    logger.info(f"Пользователь: {callback_query.from_user.id} перешел в справку по настройке GSM устройств")


# Меню отправки ICCID
@user_router.callback_query(MenuCallBack.filter(F.menu_name == 'lets_work'),
                            or_f(StateFilter(FSMUser.iccid), StateFilter(FSMUser.work)))
async def choice_way_to_send_iccid(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        text=lexicon_for_bot['give_me_iccid'],
        reply_markup=get_callback_btns(
            btns={
                lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack(),
            },
            sizes=(1,)
        )
    )
    await state.set_state(FSMUser.iccid)
    logger.info(f"Пользователь: {callback_query.from_user.id} перешел к отправке ICCID")


# Получение iccid и ping устройства
@user_router.message(or_f(F.photo, F.text), or_f(StateFilter(FSMUser.iccid), StateFilter(FSMUser.ip)))
async def ping_device(message: Message, state: FSMContext, session: AsyncSession):
    prepared_number = None
    if message.text:
        prepared_number = iccid_to_correct_form(message.text)
    elif message.photo:
        prepared_number = await get_numeric_code_from_image(message.bot, message)
    if not prepared_number.isdigit():
        await message.delete()
        await wrong_content(state, message, FSMUser, prepared_number)
        logger.info(f"Пользователь: {message.from_user.id}. Ошибка на стадии передачи ICCID: {prepared_number}")
    else:
        logger.info(f"Пользователь: {message.from_user.id} передал ICCID: {prepared_number}")
        sim_card = await get_sim(session, prepared_number)
        if sim_card is not None:
            if sim_card.state == "Активен":
                await state.update_data(iccid=prepared_number)
                await state.update_data(ip=sim_card.ip)
                logger.info(f"Пользователь: {message.from_user.id} запустил ping: {prepared_number}")
                await message.bot.delete_messages(chat_id=message.chat.id,
                                                  message_ids=[message.message_id, message.message_id - 1])
                await state.set_state(FSMUser.server)
                await message.answer(lexicon_for_bot['wait_for_server'])
                result_connection_test = await connection_test(sim_card.ip, state, message.from_user.id)
                if result_connection_test is True:
                    state_data = await state.get_data()
                    start_msg_id = state_data['start_msg_id']
                    current_msg_id = message.message_id
                    await message.bot.delete_messages(chat_id=message.chat.id,
                                                      message_ids=[i for i in range(start_msg_id+1, current_msg_id+2)]
                                                      )
                    await message.answer(
                        text=f'{lexicon_for_bot["good_ping"]}{prepared_number}\nIP: {sim_card.ip}',
                        reply_markup=get_callback_btns(
                            btns={
                                lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack()
                            },
                            sizes=(1, 1)
                        )
                    )
                    await state.set_state(FSMUser.work)
                    logger.info(f"Пользователь: {message.from_user.id} ping {prepared_number} успешен")
                elif result_connection_test is False:
                    if str(sim_card.number_tel).isdigit() and len(sim_card.number_tel) == 11:
                        await state.set_state(FSMUser.sms)
                        if sim_card.ip != '':
                            await state.update_data(ip=sim_card.ip)
                            logger.info(f"Пользователь: {message.from_user.id} неудачный ping: {prepared_number}")
                        else:
                            await state.update_data(ip="Нет IP в БД")
                            logger.info(f"Пользователь: {message.from_user.id} неудачный ping: {prepared_number} из-за "
                                        f"отсутствия IP в БД")
                        state_data = await state.get_data()
                        await message.bot.delete_messages(chat_id=message.chat.id,
                                                          message_ids=[message.message_id + 1])
                        devices = await get_devices(session)
                        await message.answer(text=f"ICCID: {state_data['iccid']}\nIP: {state_data['ip']}\n"
                                                  f"{lexicon_for_bot['select_device_from_list']}",
                                             reply_markup=get_devices_pagination(btns=devices,
                                                                                 current_page=1))
                    else:
                        await message.bot.delete_messages(chat_id=message.chat.id,
                                                          message_ids=[message.message_id + 1])
                        await wrong_content(state, message, FSMUser, f'ICCID: {prepared_number}\nНевозможно отправить '
                                                                     f'СМС на данную СИМ, попробовать другую?')
                        logger.info(f"Пользователь: {message.from_user.id} передал ICCID: {prepared_number} SIM без "
                                    f"номера телефона в БД")
            else:
                await message.delete()
                await wrong_content(state, message, FSMUser, f'ICCID:{prepared_number}\nSIM неактивна,'
                                                             f' попробовать другую?')
                logger.info(f"Пользователь: {message.from_user.id} передал ICCID: {prepared_number} неактивной SIM")
        else:
            await message.delete()
            await wrong_content(state, message, FSMUser, f'ICCID: {prepared_number}\nSIM не найдена в базе данных,'
                                                         f' попробовать другую?')
            logger.info(f"Пользователь: {message.from_user.id} передал ICCID: {message.text}."
                        f" SIM в базе не найдена")


# Выбор устройства для отправки СМС
@user_router.callback_query(StateFilter(FSMUser.sms), PaginationCallBack.filter())
async def choice_device(callback: CallbackQuery,
                        callback_data: PaginationCallBack,
                        session: AsyncSession,
                        state: FSMContext):
    current_page = callback_data.page
    if callback_data.command != 'now':
        devices = await get_devices(session)
        state_data = await state.get_data()
        await callback.message.edit_text(text=f"ICCID:{state_data['iccid']}\nIP:{state_data['ip']}\n"
                                              f"{lexicon_for_bot['select_device_from_list']}",
                                         reply_markup=get_devices_pagination(btns=devices, current_page=current_page))
    else:
        await callback.answer()


# Окно тех. поддержки
@user_router.callback_query(MenuCallBack.filter(F.menu_name == 'no_device'),
                            StateFilter(FSMUser.sms))
async def support_info(callback_query: CallbackQuery):
    logger.info(f"У пользователя: {callback_query.from_user.id} устройство не из списка")
    await callback_query.message.edit_text(
        text=f"Возможно, раздел по настройке устройств в меню '📘 Справка' поможет решить проблему.\n"
             "Если это не поможет, то свяжитесь с <a href='tg://user?id=631261314'>Тех. поддержкой</a>",
        reply_markup=get_callback_btns(
            btns={
                lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack(),
            },
            sizes=(1, 1)
        )
    )


# Отправка СМС на ПУ
@user_router.callback_query(DeviceCallBack.filter())
async def send_sms(callback_query: CallbackQuery,
                   callback_data: DeviceCallBack,
                   session: AsyncSession, state: FSMContext):
    state_data = await state.get_data()
    sms = await sms_parameters(session, callback_data.id, iccid=state_data['iccid'])
    await state.set_state(FSMUser.server)
    await callback_query.message.edit_text(text=lexicon_for_bot['sms_ping'])
    logger.info(f"Пользователь: {callback_query.from_user.id} создал задание на отправку"
                f" СМС на номер +{sms['number_tel']}")
    sending_result = await add_task(session, text=sms['text'].replace(chr(160), chr(32)),
                                    phone_number=f"+{sms['number_tel']}")
    if sending_result:
        result_connection_test = await connection_test(state_data['ip'], state, callback_query.from_user.id)
        if result_connection_test is True:
            logger.info(f"Пользователь: {callback_query.from_user.id}: повторный ping {state_data['iccid']} успешен")
            start_msg_id = state_data['start_msg_id']
            current_msg_id = callback_query.message.message_id
            await callback_query.bot.delete_messages(chat_id=callback_query.message.chat.id,
                                                     message_ids=[i for i in range(start_msg_id, current_msg_id)])
            await callback_query.message.edit_text(
                text=f'{lexicon_for_bot["good_ping"]}{state_data["iccid"]}\nIP: {state_data["ip"]}',
                reply_markup=get_callback_btns(
                    btns={
                        lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack()
                    },
                    sizes=(1, 1)
                )
            )
            await state.set_state(FSMUser.work)
        elif result_connection_test is False:
            logger.info(f"Пользователь: {callback_query.from_user.id}: повторный ping {state_data['iccid']} неуспешен")
            start_msg_id = state_data['start_msg_id']
            current_msg_id = callback_query.message.message_id
            await callback_query.bot.delete_messages(chat_id=callback_query.message.chat.id,
                                                     message_ids=[i for i in range(start_msg_id, current_msg_id + 2)])
            await callback_query.message.answer(
                text=f"{lexicon_for_bot['no_connection']}\n",
                reply_markup=get_callback_btns(
                    btns={
                        lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack(),
                    },
                    sizes=(1, 1)
                )
            )
            await state.set_state(FSMUser.work)
    else:
        logger.info(f"Пользователь: {callback_query.from_user.id} получил данные для самостоятельной отправки СМС"
                    f" на номер: +{sms['number_tel']}")
        await callback_query.message.edit_text(text="<b>😔 Неудача при автоматической отправке СМС. "
                                                    "Попробуйте вручную.</b>\n"
                                                    f"<b>ТЕКСТ</b> <i>(нажать для копирования)</i>:\n"
                                                    f"<code>{sms['text'].replace(chr(160), chr(32)).split('separator')[0]}</code>\n"
                                                    f"<b>НОМЕР</b>:\n"
                                                    f"+{sms['number_tel']}",
                                               reply_markup=get_callback_btns(
                                                   btns={
                                                       lexicon_for_bot['try_again']:
                                                           MenuCallBack(menu_name='try_ping_again').pack(),
                                                       lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack(),
                                                   },
                                                   sizes=(1, 1)
                                               )
                                               )
    await state.set_state(FSMUser.work)


# Повторная попытка пинга
@user_router.callback_query(or_f(MenuCallBack.filter(F.menu_name == 'try_ping_again')),
                            StateFilter(FSMUser.work))
async def try_ping_again(callback_query: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    logger.info(f"Пользователь: {callback_query.from_user.id}: перешел к повторному ping: {state_data['iccid']}")
    await state.set_state(FSMUser.server)
    await callback_query.message.delete()
    await callback_query.message.answer(lexicon_for_bot['sms_ping'])
    result_connection_test = await connection_test(state_data['ip'], state, callback_query.from_user.id)
    if result_connection_test is True:
        logger.info(f"Пользователь: {callback_query.from_user.id}: повторный ping {state_data['iccid']} успешен")
        start_msg_id = state_data['start_msg_id']
        current_msg_id = callback_query.message.message_id
        await callback_query.bot.delete_messages(chat_id=callback_query.message.chat.id,
                                                 message_ids=[i for i in range(start_msg_id, current_msg_id+2)])
        await callback_query.message.answer(
            text=f'{lexicon_for_bot["good_ping"]}{state_data["iccid"]}\nIP: {state_data["ip"]}',
            reply_markup=get_callback_btns(
                btns={
                    lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack()
                },
                sizes=(1, 1)
            )
        )
        await state.set_state(FSMUser.work)
    elif result_connection_test is False:
        logger.info(f"Пользователь: {callback_query.from_user.id}: повторный ping {state_data['iccid']} неуспешен")
        start_msg_id = state_data['start_msg_id']
        current_msg_id = callback_query.message.message_id
        await callback_query.bot.delete_messages(chat_id=callback_query.message.chat.id,
                                                 message_ids=[i for i in range(start_msg_id, current_msg_id+2)])
        await callback_query.message.answer(
                                            text=f"{lexicon_for_bot['no_connection']}",
                                            reply_markup=get_callback_btns(
                                                btns={
                                                    lexicon_for_bot['main']: MenuCallBack(menu_name='main').pack(),
                                                },
                                                sizes=(1, 1)
                                            )
                                            )
        await state.set_state(FSMUser.work)


# Удаление всех неожидаемых данных
@user_router.message(~StateFilter(default_state))
async def delete_other_data(message: Message):
    await message.delete()
    logger.info(f"Пользователь: {message.from_user.id} не использовал кнопки управления")
