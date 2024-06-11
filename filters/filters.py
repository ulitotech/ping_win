from aiogram.filters import BaseFilter
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import check_user
from config_data.config import load_config

config = load_config('./.env')
ADMIN = config.tg_bot.admin_id


class IsAdmin(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, session: AsyncSession):
        user = await check_user(session, message, 'admin')
        return user is not None or message.from_user.id in [a for a in ADMIN.split(',')]


class IsUser(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, session: AsyncSession):
        user = await check_user(session, message, 'user')
        return user is not None
