import asyncio


async def connection_test(ip: str) -> bool:
    """Пингует ip 5 раз и возвращает состояние устройства"""
    cmd = f'ping /n 5 {ip}'
    process = await asyncio.create_subprocess_shell(cmd,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if stdout.decode(encoding='cp866').count('TTL') > 0:
        return True
    else:
        return False
