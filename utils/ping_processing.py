import asyncio
from sys import platform
import datetime
from aiogram.fsm.context import FSMContext
from loguru import logger


async def connection_test(ip: str, state: FSMContext, user_id: str) -> bool:
    """Пингует ip несколько раз и возвращает состояние устройства"""
    if 'linux' in platform:
        cmd = ['ping', '-c', '130', '-W', '5', '-O', f'{ip}']
    else:
        cmd = ['ping', '-n', '130', '-w', '5000', f'{ip}']
    process = await asyncio.create_subprocess_exec(*cmd,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)

    timeout = datetime.timedelta(seconds=120)
    start = datetime.datetime.now()
    await state.update_data(kill_process=1)
    while datetime.datetime.now() - start < timeout:
        process_is_needed = await state.get_data()
        if not process_is_needed['kill_process']:
            process._transport.close()
            logger.info(f"Пользователь: {user_id} принудительно прервал процесс пинга")
            return None
        line = await process.stdout.readline()
        if line.decode(encoding='cp866'):
            decoded_result = (line.decode(encoding='cp866'))
            if any(ans in decoded_result for ans in ['ttl', 'TTL']):
                process._transport.close()
                return True
        await asyncio.sleep(1)
    process._transport.close()
    return False
