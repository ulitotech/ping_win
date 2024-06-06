import time
import serial

phone = serial.Serial("COM3",  9600)
time.sleep(1)

print('start')
cmd = "AT\r\n"
phone.write(cmd.encode())
time.sleep(0.5)
print(phone.read_all())
cmd = "AT+CMGF=1\r\n"
phone.write(cmd.encode())
time.sleep(0.5)
print(phone.read_all())
cmd = 'AT+CMGS="+7990"\r\n'
phone.write(cmd.encode())
time.sleep(0.5)
print(phone.read_all())
sms = 'test\r\n'
phone.write(sms.encode())
time.sleep(0.5)
print(phone.read_all())
sms = '\r\n'
phone.write(sms.encode())
time.sleep(0.5)
print(phone.read_all())
