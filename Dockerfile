FROM python:3.10-slim

# 設定 Poetry 版本
ENV POETRY_VERSION=1.8.2

# 安裝必要的系統依賴和 Poetry，並刪除 APT 緩存來減少映像大小
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 將 Poetry 添加到 PATH
ENV PATH="/root/.local/bin:$PATH"

# 設定工作目錄
WORKDIR /app

# 複製專案文件到容器內
COPY . /app

# 使用 Poetry 安裝必要依賴
RUN poetry install --no-root

# 安裝 Jupyter Lab，並使用 --no-cache-dir 來避免緩存
RUN poetry run pip install --no-cache-dir jupyterlab

# 開放 Jupyter Lab 端口
EXPOSE 8888

# 容器啟動時運行 Jupyter Lab
CMD ["poetry", "run", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]

