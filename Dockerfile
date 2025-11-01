# 多阶段构建 Dockerfile for OpenWrt Config Generator

FROM python:3.11-slim as base

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    g++ \
    libncurses5-dev \
    zlib1g-dev \
    gawk \
    git \
    gettext \
    libssl-dev \
    xsltproc \
    wget \
    unzip \
    python3 \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY parse_kconfig.py .
COPY api.py .
COPY index.html .

# 创建必要的目录
RUN mkdir -p /mnt/openwrt_source

# 设置环境变量
ENV OPENWRT_SRC_PATH=/mnt/openwrt_source
ENV STATIC_DIR=/app
ENV OUTPUT_JSON_PATH=/app/menu.json
ENV PORT=5000
ENV DEBUG=False

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# 使用 gunicorn 运行生产服务器
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "180", "--access-logfile", "-", "--error-logfile", "-", "api:app"]
