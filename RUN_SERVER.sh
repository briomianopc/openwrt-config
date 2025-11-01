#!/bin/bash
# 启动本地测试服务器

cd /workspace

echo "======================================"
echo "OpenWrt Config Generator - 本地测试"
echo "======================================"
echo ""
echo "启动 Flask 服务器..."
echo ""
echo "访问地址: http://localhost:5000"
echo ""
echo "测试指南:"
echo "  1. 打开浏览器访问上述地址"
echo "  2. 查看 FRONTEND_TEST.md 获取详细测试步骤"
echo "  3. 按 Ctrl+C 停止服务器"
echo ""
echo "======================================"
echo ""

python3 api.py
