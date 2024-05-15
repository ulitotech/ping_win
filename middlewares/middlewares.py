from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing import Any, Callable, Dict, Awaitable
import datetime
from loguru import logger

USERS = {}


# Мидллварь для отлавливания сессии БД
class DatabaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)


# Мидллварь для отражения троттлинга
class ThrottlingMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        throttling_delta = datetime.timedelta(milliseconds=300)
        use_limit = datetime.timedelta(seconds=10)
        usr_id = None
        upd_date = datetime.datetime.now()
        if event.message:
            usr_id = event.message.chat.id
        elif event.callback_query:
            usr_id = event.callback_query.message.chat.id
        if usr_id in USERS.keys():
            if abs(upd_date-USERS[usr_id]) > throttling_delta:
                for k in USERS.keys():
                    if abs(upd_date - USERS[usr_id]) > use_limit and k != usr_id:
                        del USERS[k]
                USERS[usr_id] = upd_date
                result = await handler(event, data)
                return result
            else:
                USERS[usr_id] = upd_date
                logger.info(f'Пользователь: {usr_id} пытался уронить сервер!!!')
        else:
            for k in USERS.keys():
                if abs(upd_date - USERS[usr_id]) > use_limit and k != usr_id:
                    del USERS[k]
            USERS[usr_id] = upd_date
            result = await handler(event, data)
            return result
