import asyncio
from sys import platform
import datetime


async def connection_test(ip: str) -> bool:
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
    while datetime.datetime.now() - start < timeout:
        line = await process.stdout.readline()
        if line.decode(encoding='cp866'):
            decoded_result = (line.decode(encoding='cp866'))
            if any(ans in decoded_result for ans in ['ttl', 'TTL']):
                process._transport.close()
                return True
        await asyncio.sleep(1)
    process._transport.close()
    return False
