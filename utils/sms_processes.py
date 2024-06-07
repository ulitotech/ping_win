import serial
import serial.tools.list_ports
from loguru import logger
from asyncio import sleep
from database.orm_query import change_task_status
import html


def define_com_port():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if 'CH340' in p.description:
            return p.device
            break


async def send_sms_via_gsm(text: str, number: str) -> bool:
    port = define_com_port()
    await sleep(1)
    if port is None:
        logger.info(f'Устройство не подключено')
        await change_task_status(3)
    else:
        logger.info(f'Идет отправка сообщения на номер {number}...')
        try:
            gms_logs = 0
            gsm_module = serial.Serial(port, 9600)
            await sleep(1)
            cmd = "AT\r\n"
            gsm_module.write(cmd.encode())
            await sleep(0.5)
            answer = gsm_module.read_all().decode()
            if 'error' in answer.lower():
                gms_logs += 1
            cmd = "AT+CMGF=1\r\n"
            gsm_module.write(cmd.encode())
            await sleep(0.5)
            answer = gsm_module.read_all().decode()
            if 'error' in answer.lower():
                gms_logs += 1
            cmd = f'AT+CMGS="{number}"\r\n'
            gsm_module.write(cmd.encode())
            await sleep(0.5)
            answer = gsm_module.read_all().decode()
            if 'error' in answer.lower():
                gms_logs += 1
            text_sms = f'{html.unescape(text)}\r\n'
            gsm_module.write(text_sms.encode())
            await sleep(2)
            answer = gsm_module.read_all().decode()
            if 'error' in answer.lower():
                gms_logs += 1
            sms = '\r\n'
            gsm_module.write(sms.encode())
            await sleep(0.5)
            answer = gsm_module.read_all().decode()
            if 'error' in answer.lower():
                gms_logs += 1
            await change_task_status(2)
            if gms_logs == 0:
                logger.info(f'CМС отправлено на номер {number}')
            else:
                await change_task_status(3)
                logger.info(f'Ошибка при выполнении АТ комманд')
        except Exception as e:
            await change_task_status(3)
            logger.info(f'Ошибка при автоматической отправке СМС на номер {number}\n{e}')