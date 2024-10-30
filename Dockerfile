FROM python:3.10-slim

RUN apt update && apt install -y nmap \
    iproute2 && rm -rf /var/lib/apt/lists/

WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3","./KiTools.py" ]