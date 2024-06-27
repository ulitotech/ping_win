import io
from typing import BinaryIO
from PIL import Image
from aiogram.types import Message
from pyzbar.pyzbar import decode, Decoded
from aiogram import Bot
import string


def iccid_to_correct_form(number: str) -> list:
    """Функция для приведения ICCID к требуемому виду"""
    number = ''.join(i for i in number.translate(string.punctuation) if i.isdigit())
    if number.isdigit() and 17 <= len(number) <= 20:
        if '8970102' in number and len(number) >= 17:
            return number[:17]
        elif '8970101' in number and len(number) >= 20:
            return number[:20]
        elif '8970199' in number or '8970120' in number or '8971350' in number or '8971206' in number and\
                len(number) >= 19:
            return number[:19]
        else:
            return 'SIM не найдена в базе данных, попробовать другую?'
    else:
        return 'Введено некорректное значение. Повторите попытку.'


async def get_numeric_code_from_image(bot: Bot, message: Message):
    """Функция принимает BinaryIO-объект фото.
    Конвертирует штрих-код на фото в числовое значение"""
    image_bio: BinaryIO = await bot.download(file=message.photo[-1])
    image_b: bytes = image_bio.getvalue()
    image: Image = Image.open(io.BytesIO(image_b))
    decoded: list[Decoded] = decode(image)
    if len(decoded) == 0:
        return 'На фото отсутствует/нечитаем штрих-код. Повторите попытку.'
    elif len(decoded) != 1:
        return 'На фото должен быть только один штрих-код!'
    else:
        numeric_code: str = decoded[0].data.decode('utf8')
        return iccid_to_correct_form(numeric_code)
