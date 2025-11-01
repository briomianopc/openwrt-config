#!/bin/bash
# OpenWrt Config Generator 快速启动脚本

set -e

echo "======================================"
echo "OpenWrt Config Generator"
echo "======================================"
echo ""

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装 Docker"
    echo "请访问 https://docs.docker.com/get-docker/ 安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "错误: 未安装 Docker Compose"
    echo "请访问 https://docs.docker.com/compose/install/ 安装 Docker Compose"
    exit 1
fi

# 检查是否配置了 OpenWrt 源码路径
echo "检查 docker-compose.yml 配置..."
if grep -q "/path/to/your/openwrt" docker-compose.yml; then
    echo ""
    echo "⚠️  警告: 您需要先配置 OpenWrt 源码路径！"
    echo ""
    echo "请编辑 docker-compose.yml 文件："
    echo "  将 '/path/to/your/openwrt' 修改为您的 OpenWrt 源码实际路径"
    echo ""
    read -p "是否现在编辑配置文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} docker-compose.yml
    else
        echo "请手动编辑 docker-compose.yml 后再运行此脚本"
        exit 1
    fi
fi

echo ""
echo "正在构建 Docker 镜像..."
docker-compose build

echo ""
echo "正在启动容器..."
docker-compose up -d

echo ""
echo "等待服务启动..."
sleep 5

# 检查容器健康状态
echo "检查服务健康状态..."
for i in {1..10}; do
    if curl -sf http://localhost:5000/health > /dev/null 2>&1; then
        echo "✓ 服务已就绪！"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "✗ 服务启动超时，请检查日志："
        echo "  docker-compose logs -f"
        exit 1
    fi
    echo "  等待中... ($i/10)"
    sleep 3
done

# 检查是否存在 menu.json
if docker-compose exec -T openwrt-config-generator test -f /app/menu.json; then
    echo "✓ menu.json 已存在"
else
    echo ""
    echo "⚠️  menu.json 不存在，正在生成..."
    echo "这可能需要几分钟时间，请耐心等待..."
    docker-compose exec openwrt-config-generator python parse_kconfig.py
    echo "✓ menu.json 生成完成"
fi

echo ""
echo "======================================"
echo "✓ 启动成功！"
echo "======================================"
echo ""
echo "访问地址: http://localhost:5000"
echo ""
echo "常用命令:"
echo "  查看日志:   docker-compose logs -f"
echo "  停止服务:   docker-compose stop"
echo "  重启服务:   docker-compose restart"
echo "  完全清理:   docker-compose down"
echo ""
echo "如需重新生成 menu.json:"
echo "  docker-compose exec openwrt-config-generator python parse_kconfig.py"
echo ""
