FROM python:3.11
RUN mkdir -p /usr/src/ping_win
WORKDIR /usr/src/ping_win
COPY . /usr/src/ping_win
RUN apt-get update && apt-get install libzbar0 -y && pip install pyzbar && apt-get install -y iputils-ping &&  \
    pip install --no-cache-dir -r requirements.txt && apt-get install nano
CMD ["python", "main.py"]