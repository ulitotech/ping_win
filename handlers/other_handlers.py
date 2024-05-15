from aiogram import Router
from aiogram.types import Message
from filters.filters import IsUser, IsAdmin
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from lexicon.lexicon_ru import lexicon_for_bot
from loguru import logger

other_router = Router()
other_router.message.filter(~IsUser(), ~IsAdmin())


@other_router.message(StateFilter(default_state))
@other_router.message(~StateFilter(default_state))
async def send_echo(message: Message):
    logger.info(f"Пользователь не из базы: {message.from_user.id} обратился к боту")
    await message.answer(text=lexicon_for_bot['unknown_user'])
