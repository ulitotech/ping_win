import serial
import serial.tools.list_ports
from loguru import logger
from asyncio import sleep
from database.orm_query import change_task_status
import html
from sys import platform

def define_com_port():
    ports = list(serial.tools.list_ports.comports())
    logger.info(f'Определены порты {[p for p in ports]}')
    if platform in ('linux', 'linux2',):
        for port in ports:
            return port.device
        return None
    else:
        for p in ports:
            if 'ch340' in p.description.lower() or 'ch341' in p.description.lower()\
                    or 'usb serial' in p.description.lower():
                return p.device
        return None


async def send_sms_via_gsm(text: str, number: str) -> bool:
    port = define_com_port()
    await sleep(0.5)
    cmnds = text.split('separator')
    if port is None:
        logger.info(f'GSM модуль не подключен')
        await change_task_status(3)
    else:
        logger.info(f'Идет отправка сообщения на номер {number}...')
        try:
            cmnds = text.split('separator')
            logger.info(f"Подготовлены команды {cmnds}")
            gms_logs = 0
            for cmnd in cmnds:
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
                text_sms = f'{html.unescape(cmnd)}\r\n'
                gsm_module.write(text_sms.rstrip().encode())
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
            if gms_logs == 0:
                logger.info(f'CМС отправлено на номер {number}')
                await change_task_status(2)
            else:
                await change_task_status(3)
                logger.info(f'Ошибка при выполнении АТ команд')
        except Exception as e:
            await change_task_status(3)
            logger.info(f'Ошибка при автоматической отправке СМС на номер {number}\n{e}')
