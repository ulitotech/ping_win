from database.orm_query import change_task_status, get_task
from utils.sms_processes import send_sms_via_gsm
from loguru import logger


async def check_task_table():
    task = await get_task()
    if task is not None and task.status == 0:
        logger.info(f'В списке есть задание на отправку СМС через модуль на номер {task.phone_number}')
        await change_task_status(1)
        logger.info(f'Задание по отправке СМС на номер {task.phone_number} принято в работу')
        await send_sms_via_gsm(task.text, task.phone_number)
