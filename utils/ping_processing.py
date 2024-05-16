import asyncio


async def connection_test(ip: str) -> bool:
    """Пингует ip 5 раз и возвращает состояние устройства"""
    cmd = f'ping /n 1 {ip}'
    for i in range(5):
        process = await asyncio.create_subprocess_shell(cmd,
                                                        stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        if 'TTL' in stdout.decode(encoding='cp866'):
            return True
    return False
