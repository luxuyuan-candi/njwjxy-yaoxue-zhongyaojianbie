FROM python:3.10-slim
WORKDIR /app

RUN apt update && \
apt install -y git && \
git clone https://github.com/luxuyuan-candi/njwjxy-yaoxue-zhongyaojianbie.git

WORKDIR /app/njwjxy-yaoxue-zhongyaojianbie

RUN python3 -m pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu && \
python3 -m pip install --no-cache-dir -r app/backend/requirements.txt

CMD ["python3", "app/backend/server.py"]
