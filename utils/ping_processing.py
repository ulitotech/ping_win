import asyncio
from sys import platform


async def connection_test(ip: str) -> bool:
    """Пингует ip несколько раз и возвращает состояние устройства"""
    if 'linux' in platform:
        cmd = f'ping -c 1 {ip}'
    else:
        cmd = f'ping /n 1 {ip}'
    for i in range(3):
        process = await asyncio.create_subprocess_shell(cmd,
                                                        stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        decoded_result = stdout.decode(encoding='cp866')
        if any(ans in decoded_result for ans in ['ttl', 'TTL']):
            return True
    return False
