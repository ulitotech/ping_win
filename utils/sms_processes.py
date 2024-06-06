import time
import serial
from serial.tools import list_ports
import time
from loguru import logger

# def send_sms_via_gsm(text:str, number:str)->bool:
#     try:
#         phone = serial.Serial("COM3",  9600)
#         time.sleep(1)
#         cmd = "AT\r\n"
#     except Exception as e:
#         logger.info(f"Произошла ошибка в работе gsm модуля: {e}")
#


#
# cmd = "AT\r\n"
# phone.write(cmd.encode())
# time.sleep(0.5)
# print(phone.read_all())
# cmd = "AT+CMGF=1\r\n"
# phone.write(cmd.encode())
# time.sleep(0.5)
# print(phone.read_all())
# cmd = 'AT+CMGS="+7990"\r\n'
# phone.write(cmd.encode())
# time.sleep(0.5)
# print(phone.read_all())
# sms = 'test\r\n'
# phone.write(sms.encode())
# time.sleep(0.5)
# print(phone.read_all())
# sms = '\r\n'
# phone.write(sms.encode())
# time.sleep(0.5)
# print(phone.read_all())

port = ''
for p in list(serial.tools.list_ports.comports()):
    if 'CH340' in p.description:
        port = p.device
        break

phone = serial.Serial(port,  9600)
time.sleep(1)

# while True:
#     cmd = input('|--->')
#     phone.write(f'{cmd}\r\n'.encode())
#     time.sleep(0.5)
#     while phone.in_waiting:
#         print(phone.readline())
#         time.sleep(0.1)


def wait_response() -> str:
    resp = ''
    timeout = time.time()+10
    while not phone.in_waiting and time.time() < timeout:
        pass
    if phone.in_waiting:
        resp = phone.readline()
    else:
        print('Timeout...')
    return resp.decode()


def send_at_command(command: str, waiting: bool) -> str:
    resp = ''
    phone.write(command)
    if waiting:
        resp += wait_response()
    print(resp)
    return resp
