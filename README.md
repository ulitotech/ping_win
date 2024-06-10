# PingWin Telegram Bot
## _Telegram bot for ping electricity metering devices_
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)![Microsoft Excel](https://img.shields.io/badge/Microsoft_Excel-217346?style=for-the-badge&logo=microsoft-excel&logoColor=white)![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)![Docker](https://img.shields.io/badge/Docker-blue?logo=docker&logoColor=white&style=for-the-badge)
***
## Features

- Ping devices via remoted server
- Recognize ICCID via text or photo
- Update DB with excel files (admin privilegion)
- Get SMS template for manual ping device 
- Get help about ping process
- Automaticaly sending SMS

## Docker settings
 
For share USB port with GSM module  to Docker container you should execute code below
```bash
sudo docker build -t <image name>
sudo docker run -d -t -i --device=/dev/ttyUSB0 <image name>
```
