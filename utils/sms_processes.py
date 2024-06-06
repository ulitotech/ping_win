import time
import serial


phone = serial.Serial("COM4",  9600)
time.sleep(1)
while True:
   cmd = input('-> ')
   cmd = cmd+'\r\n'
   phone.write(cmd.encode())
   time.sleep(1)
   print(phone.read_all())
print('start')
cmd = "AT\r\n"
phone.write(cmd.encode())
time.sleep(1)
print(phone.read_all())
cmd = "AT+CMGF=1\r\n"
phone.write(cmd.encode())
time.sleep(1)
print(phone.read_all())
cmd = 'AT+CMGS="number"\r\n'
phone.write(cmd.encode())
time.sleep(0.5)
print(phone.read_all())
sms = 'yo\r\n'
phone.write(sms.encode())
time.sleep(0.5)
print(phone.read_all())
sms = '\r\n'
phone.write(sms.encode())
time.sleep(0.5)
print(phone.read_all())
