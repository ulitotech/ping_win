from aiogram import Router, F
from aiogram.types import Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import add_users, add_operators, add_sims, add_devices, add_projects, add_helps, add_user,\
    get_users, drop_sim_table
from filters.filters import IsAdmin
from sqlalchemy import exc
from lexicon.lexicon_ru import lexicon_for_bot
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
admin_router = Router()
admin_router.message.filter(IsAdmin())


# Загрузка excel в базу
@admin_router.message(F.document)
async def add_to_database(message: Message, session: AsyncSession):
    if '.xlsx' in message.document.file_name:
        if 'help' in message.document.file_name:
            await message.delete()
            await message.answer(lexicon_for_bot['loading'])
            try:
                addition_info = await add_helps(session, message)
                await message.answer(f"{lexicon_for_bot['added_help']}\n[{addition_info}]")
                await message.bot.delete_message(message.chat.id, message_id=message.message_id + 1)
                logger.info(f"Пользователь: {message.from_user.id} загрузил справку в базу")
            except exc.SQLAlchemyError as e:
                await message.answer(lexicon_for_bot['check_loaded_base'])
                logger.info(f"Пользователь: {message.from_user.id} попытался загрузить в базу данные с ошибкой")

        if 'operator' in message.document.file_name:
            await message.delete()
            await message.answer(lexicon_for_bot['loading'])
            try:
                addition_info = await add_operators(session, message)
                await message.answer(f"{lexicon_for_bot['added_operators']}\n[{addition_info}]")
                await message.bot.delete_message(message.chat.id, message_id=message.message_id + 1)
                logger.info(f"Пользователь: {message.from_user.id} загрузил операторов в базу")
            except exc.SQLAlchemyError as e:
                await message.answer(lexicon_for_bot['check_loaded_base'])
                logger.info(f"Пользователь: {message.from_user.id} попытался загрузить в базу данные с ошибкой")

        if 'device' in message.document.file_name:
            await message.delete()
            await message.answer(lexicon_for_bot['loading'])
            try:
                addition_info = await add_devices(session, message)
                await message.answer(f"{lexicon_for_bot['added_devices']}\n[{addition_info}]")
                await message.bot.delete_message(message.chat.id, message_id=message.message_id + 1)
                logger.info(f"Пользователь: {message.from_user.id} загрузил устройства в базу")
            except exc.SQLAlchemyError:
                await message.answer(lexicon_for_bot['check_loaded_base'])
                logger.info(f"Пользователь: {message.from_user.id} попытался загрузить в базу данные с ошибкой")

        if 'user' in message.document.file_name:
            await message.delete()
            await message.answer(lexicon_for_bot['loading'])
            try:
                addition_info = await add_users(session, message)
                await message.answer(f"{lexicon_for_bot['added_users']}\n[{addition_info}]")
                await message.bot.delete_message(message.chat.id, message_id=message.message_id + 1)
                logger.info(f"Пользователь: {message.from_user.id} загрузил других пользователей в базу")
            except exc.SQLAlchemyError:
                await message.answer(lexicon_for_bot['check_loaded_base'])
                logger.info(f"Пользователь: {message.from_user.id} попытался загрузить в базу данные с ошибкой")

        if 'sim' in message.document.file_name:
            await message.delete()
            await message.answer(lexicon_for_bot['loading'])
            try:
                addition_info = await add_sims(session, message)
                await message.answer(f"{lexicon_for_bot['added_sims']}\n[{addition_info}]")
                await message.bot.delete_message(message.chat.id, message_id=message.message_id + 1)
                logger.info(f"Пользователь: {message.from_user.id} загрузил СИМ в базу")
            except exc.SQLAlchemyError:
                await message.answer(lexicon_for_bot['check_loaded_base'])
                logger.info(f"Пользователь: {message.from_user.id} попытался загрузить в базу данные с ошибкой")

        if 'project' in message.document.file_name:
            await message.delete()
            await message.answer(lexicon_for_bot['loading'])
            try:
                addition_info = await add_projects(session, message)
                await message.answer(f'👍Проекты добавлены\n[{addition_info}]')
                logger.info(f"Пользователь: {message.from_user.id} загрузил проекты в базу")
            except exc.SQLAlchemyError as e:
                await message.answer(lexicon_for_bot['check_loaded_base'])
                logger.info(f"Пользователь: {message.from_user.id} попытался загрузить в базу данные с ошибкой")


# Добавить пользователя
@admin_router.message(lambda message: 'add_user_' in message.text, StateFilter(default_state))
async def adding_user(message: Message, session: AsyncSession):
    await message.delete()
    result = await add_user(session, message)
    await message.answer(result)


# Получить полный список пользователей
@admin_router.message(F.text == 'get_users', StateFilter(default_state))
async def getting_user(message: Message, session: AsyncSession):
    await message.delete()
    users = await get_users(session, message)
    result = '\n'.join([f'🙍🏼‍♂️{u.telegram_id}|{u.status}' for u in users])
    await message.answer(result)


# Дропнуть таблицу СИМ
@admin_router.message(F.text == 'drop_sim', StateFilter(default_state))
async def dropping_sim(message: Message, session: AsyncSession):
    await message.delete()
    result = await drop_sim_table(session, message)
    await message.answer(result)

