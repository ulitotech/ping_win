import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config_data import load_config, Config
from loguru import logger
from handlers import other_handlers, user_handlers, admin_handlers
from aiogram.fsm.storage.memory import MemoryStorage
from database.engine import create_db, drop_db, session_maker, drop_task_table
from middlewares.middlewares import DatabaseSession, ThrottlingMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils.working_with_task import check_task_table
ALLOWED_UPDATES = ['message', 'callback_query']

# Создание расписания
scheduler = AsyncIOScheduler(job_defaults={'max_instances': 20})


# Создание/удаление БД
async def on_startup():
    run_param = False
    if run_param:
        await drop_db()
        logger.info('База данных удалилась')
    logger.info('Подключение базы данных...')
    await create_db()
    logger.info('База данных подключилась')
    await drop_task_table()
    logger.info('Задачи для GSM ощичены...')


async def on_shutdown():
    scheduler.shutdown()
    logger.info("Бот выключился")


async def main():
    logger.info('Запуск бота...')
    config: Config = load_config('./.env')
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    logger.info('Подключение FSM...')
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DatabaseSession(session_pool=session_maker))
    dp.update.outer_middleware(ThrottlingMiddleware())

    logger.info('Подключение роутеров...')

    dp.include_router(admin_handlers.admin_router)
    dp.include_router(user_handlers.user_router)
    dp.include_router(other_handlers.other_router)

    logger.info('Запуск scheduler...')
    scheduler.add_job(check_task_table, "interval", seconds=1, args=())
    scheduler.start()

    logger.info('Бот работает...')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt as ke:
        logger.exception(f"Выключение при нажатии клавиши:\n{ke}")
    except Exception as e:
        logger.exception(f"Произошла ошибка:\n{e}")
