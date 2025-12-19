FROM python:3.9  # 例

WORKDIR /app

# 【重要】先に requirements.txt をコンテナ内にコピーする必要があります
COPY requirements.txt . 

# その後に pip install を実行します
RUN pip install --no-cache-dir -r requirements.txt

# その他のソースコードをコピー
COPY . .# Pythonが入った軽量なOSを使う
FROM python:3.9-slim

# 作業フォルダを作る
WORKDIR /app

# フォルダの中身を全部コピーする
COPY . .

# requirements.txtを見てインストールする
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Runのお約束（8080番ポート）
EXPOSE 8080

# アプリを起動するコマンド
CMD streamlit run app.py --server.port 8080 --server.address 0.0.0.0