import html
from asyncio import sleep

from aiogram import Bot
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Device, Sim, Project, Operator, Help
from utils.excel_processes import read_excel


async def add_users(session: AsyncSession, message: Message):
    users = await read_excel(Bot, message)
    double_rows = []
    chunk = 1000
    for i in range(0, len(users), chunk):
        for user in users[i:i + chunk]:
            query = select(User.telegram_id)
            result = await session.execute(query)
            rows = result.all()
            telegram_id_for_comparison = set(i.telegram_id for i in rows)
            if user['telegram_id'] in telegram_id_for_comparison:
                double_rows.append(user['telegram_id'])
                continue
            else:
                telegram_id_for_comparison.add(user['telegram_id'])
                session.add(User(
                    telegram_id=user['telegram_id'],
                    status=user['status'],
                ))
        await session.commit()
    if double_rows:
        return f'Пропущены строки с ID: {", ".join(double_rows)}'
    else:
        return 'Данные корректны'


async def get_devices(session: AsyncSession):
    devices_dict = {}
    query = select(Device, ).where(Device.interface == 'sms')
    devices = await session.execute(query)
    result = devices.scalars().all()
    for r in result:
        devices_dict[r.name] = r.id
    return devices_dict


async def check_user(session: AsyncSession, message: Message, status: str):
    query = select(User).where(User.telegram_id == message.from_user.id and User.status == status)
    users = await session.execute(query)
    result = users.one_or_none()
    return result


async def get_sim(session: AsyncSession, data: int):
    query = select(Sim).where(Sim.iccid == str(data))
    result = await session.execute(query)
    return result.scalar()


async def sms_parameters(session: AsyncSession, device_id: int, iccid: int) -> str:
    query_settings_template = select(Device.settings).where(Device.id == str(device_id))
    settings_template = await session.execute(query_settings_template)
    settings_template = settings_template.one_or_none()
    query_device_parameters = select(Sim.number_tel, Operator.apn, Operator.login, Operator.password,
                                     Project.port).join(Operator).join(Project).where(Sim.iccid == str(iccid))
    device_parameters = await session.execute(query_device_parameters)
    device_parameters = device_parameters.one_or_none()
    device_settings = settings_template[0].replace('{apn}',
                                                   device_parameters.apn).replace('{login}',
                                                                                  device_parameters.login).replace(
        '{password}',
        device_parameters.password).replace('{port}', device_parameters.port)

    return {"number_tel": device_parameters.number_tel, "text": html.escape(device_settings)}


async def add_sims(session: AsyncSession, message: Message):
    sims = await read_excel(Bot, message)
    double_rows = []
    chunk = 10000
    for i in range(0, len(sims), chunk):
        query = select(Sim.iccid, Sim.number_tel)
        result = await session.execute(query)
        rows = result.all()
        iccid_for_comparison = set(i.iccid for i in rows)
        number_tel_for_comparison = set(i.number_tel for i in rows)
        for sim in sims[i:i + chunk]:
            if sim['iccid'] in iccid_for_comparison or sim['number_tel'] in number_tel_for_comparison:
                double_rows.append(sim['iccid'])
                continue
            else:
                iccid_for_comparison.add(sim['iccid'])
                number_tel_for_comparison.add(sim['number_tel'])
                session.add(Sim(iccid=sim['iccid'],
                                number_tel=sim['number_tel'],
                                apn=sim['apn'],
                                ip=sim['ip'],
                                state=sim['state'],
                                operator_id=sim['operator_id'],
                                project_id=sim['project_id'],
                                ))
        await session.commit()
    if double_rows:
        return f'Пропущены строки с ICCID: {", ".join(double_rows)}!!!'
    else:
        return 'Данные корректны'


async def add_devices(session: AsyncSession, message: Message):
    devices = await read_excel(Bot, message)
    double_rows = []
    chunk = 1000
    for i in range(0, len(devices), chunk):
        for device in devices[i:i + chunk]:
            query = select(Device.name)
            result = await session.execute(query)
            rows = result.all()
            name_for_comparison = set(i.name for i in rows)
            if device['name'] in name_for_comparison:
                double_rows.append(device['name'])
                continue
            else:
                name_for_comparison.add(device['name'])
                session.add(Device(
                    name=device['name'],
                    interface=device['interface'],
                    settings=device['settings'],
                ))
        await session.commit()
        await sleep(0.5)
    if double_rows:
        return f'Пропущены строки с Name: {", ".join(double_rows)}'
    else:
        return 'Данные корректны'


async def add_helps(session: AsyncSession, message: Message):
    helps = await read_excel(Bot, message)
    double_rows = []
    chunk = 1000
    for i in range(0, len(helps), chunk):
        for help in helps[i:i + chunk]:
            query = select(Help.name)
            result = await session.execute(query)
            rows = result.all()
            name_for_comparison = set(i.name for i in rows)
            if help['name'] in name_for_comparison:
                double_rows.append(help['name'])
                continue
            else:
                name_for_comparison.add(help['name'])
                session.add(Help(
                    name=help['name'],
                    text=help['text'],
                ))
        await session.commit()
        await sleep(0.5)
    if double_rows:
        return f'Пропущены строки с Name: {", ".join(double_rows)}'
    else:
        return 'Данные корректны'


async def get_help(session: AsyncSession, help_name: str):
    query = select(Help.text).where(Help.name == help_name)
    result = await session.execute(query)
    return result.scalar()


async def add_projects(session: AsyncSession, message: Message):
    projects = await read_excel(Bot, message)
    double_rows = []
    chunk = 1000
    for i in range(0, len(projects), chunk):
        for project in projects[i:i + chunk]:
            query = select(Project.name)
            result = await session.execute(query)
            rows = result.all()
            name_for_comparison = set(i.name for i in rows)
            if project['name'] in name_for_comparison:
                double_rows.append(project['name'])
                continue
            else:
                name_for_comparison.add(project['name'])
                session.add(Project(
                    name=project['name'],
                    port=project['port'],
                ))
        await session.commit()
        await sleep(0.5)
    if double_rows:
        return f'Пропущены строки с Name: {", ".join(double_rows)}'
    else:
        return 'Данные корректны'


async def add_operators(session: AsyncSession, message: Message):
    operators = await read_excel(Bot, message)
    double_rows = []
    chunk = 1000
    for i in range(0, len(operators), chunk):
        for operator in operators[i:i + chunk]:
            query = select(Operator.name)
            result = await session.execute(query)
            rows = result.all()
            name_for_comparison = set(i.name for i in rows)
            if operator['name'] in name_for_comparison:
                double_rows.append(operator['name'])
                continue
            else:
                name_for_comparison.add(operator['name'])
                session.add(Operator(
                    name=operator['name'],
                    apn=operator['apn'],
                    login=operator['login'],
                    password=operator['password'],
                ))
        await session.commit()
        await sleep(0.5)
    if double_rows:
        return f'Пропущены строки с Name: {", ".join(double_rows)}'
    else:
        return 'Данные корректны'
