FROM python:3.10-slim AS backend

WORKDIR /app

# 依存関係のインストールに必要なファイルのみをコピー
COPY ./backend/requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# ---- ランタイムで変えたい値（デフォルトを用意）----
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8000
ENV UVICORN_TIMEOUT=3000
# -----------------------------------------------

# shell 形式の CMD で環境変数を展開
CMD sh -c 'uvicorn main:app --host "${UVICORN_HOST}" --port "${UVICORN_PORT}" --timeout-keep-alive "${UVICORN_TIMEOUT}"'

# container 内で待ち受ける port no
EXPOSE 8000
