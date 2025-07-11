FROM python:3.10-slim
WORKDIR /app

RUN apt update && \
apt install -y git && \
git clone https://github.com/luxuyuan-candi/njwjxy-yaoxue-zhongyaojianbie.git

WORKDIR /app/njwjxy-yaoxue-zhongyaojianbie

RUN python3 -m pip install --no-cache-dir -r app/tts/requirements.txt

CMD ["python3", "app/tts/tts_server.py"]
