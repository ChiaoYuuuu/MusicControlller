FROM python:3.9-slim

# 安裝依賴
RUN apt-get update && apt-get install -y libaio1 wget unzip && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /code

# 複製 Oracle client
COPY ./oracle/instantclient_23_8 /code/oracle/instantclient_23_8
ENV LD_LIBRARY_PATH=/code/oracle/instantclient_23_8

# 安裝 Python 套件
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案原始碼
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

