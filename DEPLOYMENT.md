# 部署检查清单

## 📋 部署前准备

### 1. OpenWrt 源码准备
- [ ] 已下载 OpenWrt 源码
- [ ] 已执行 `./scripts/feeds update -a`
- [ ] 已执行 `./scripts/feeds install -a`
- [ ] 记录源码路径：________________

### 2. 系统要求检查
- [ ] Docker 已安装（运行 `docker --version`）
- [ ] Docker Compose 已安装（运行 `docker-compose --version`）
- [ ] 端口 5000 可用（或准备修改）

### 3. 配置文件修改
- [ ] 已编辑 `docker-compose.yml`
- [ ] 已将 `/path/to/your/openwrt` 修改为实际路径
- [ ] 已检查端口映射（默认 5000:5000）
- [ ] （可选）已配置 `.env` 文件

## 🚀 部署步骤

### 快速部署（推荐）

```bash
# 1. 使用快速启动脚本
./start.sh

# 脚本会自动完成以下操作：
# - 检查 Docker 环境
# - 构建镜像
# - 启动容器
# - 健康检查
# - 生成 menu.json（如果需要）
```

### 手动部署

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动容器
docker-compose up -d

# 3. 查看日志确认启动成功
docker-compose logs -f

# 4. 生成 menu.json
docker-compose exec openwrt-config-generator python parse_kconfig.py

# 5. 访问应用
# 浏览器打开 http://localhost:5000
```

## ✅ 部署后验证

### 1. 健康检查
```bash
curl http://localhost:5000/health
```

期望响应：
```json
{
  "status": "healthy",
  "openwrt_src_exists": true,
  "menu_json_exists": true
}
```

### 2. 访问测试
- [ ] 打开 http://localhost:5000
- [ ] 能看到配置生成器界面
- [ ] 能看到配置选项树
- [ ] 能勾选/取消勾选选项
- [ ] 依赖项正确禁用/启用
- [ ] 自动选择功能正常工作

### 3. 功能测试
- [ ] 选择几个配置项
- [ ] 点击"生成 .config 文件"
- [ ] 成功下载 .config 文件
- [ ] 下载的文件内容正确

## 🔧 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs --tail=100

# 检查容器状态
docker-compose ps

# 重新构建镜像
docker-compose build --no-cache
docker-compose up -d
```

### menu.json 生成失败

```bash
# 进入容器检查
docker-compose exec openwrt-config-generator bash

# 手动运行解析器
cd /app
python parse_kconfig.py --verbose

# 检查 OpenWrt 源码挂载
ls -la /mnt/openwrt_source/
```

### 配置生成失败

```bash
# 检查 make 是否可用
docker-compose exec openwrt-config-generator which make

# 测试 make defconfig
docker-compose exec openwrt-config-generator bash -c "cd /mnt/openwrt_source && make defconfig"
```

### 权限问题

```bash
# 检查挂载目录权限
ls -la /path/to/your/openwrt

# 如果需要，修改权限
chmod -R 755 /path/to/your/openwrt
```

## 🔐 生产环境部署建议

### 1. 安全配置

```yaml
# docker-compose.yml 修改建议
environment:
  - DEBUG=False
  - CORS_ORIGINS=https://yourdomain.com
```

### 2. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name config.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 180s;
    }
}
```

### 3. 添加 HTTPS

```bash
# 使用 Let's Encrypt
certbot --nginx -d config.yourdomain.com
```

### 4. 资源限制

```yaml
# docker-compose.yml 添加资源限制
services:
  openwrt-config-generator:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 5. 日志管理

```yaml
# docker-compose.yml 添加日志配置
services:
  openwrt-config-generator:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 6. 备份策略

```bash
# 定期备份 menu.json
cp menu.json menu.json.backup.$(date +%Y%m%d)

# 备份整个项目
tar -czf openwrt-config-backup-$(date +%Y%m%d).tar.gz .
```

## 📊 监控建议

### 1. 健康检查监控

```bash
# 使用 cron 定期检查
*/5 * * * * curl -sf http://localhost:5000/health || echo "Service down" | mail -s "Alert" admin@example.com
```

### 2. 日志监控

```bash
# 查看实时日志
docker-compose logs -f --tail=100

# 查看错误日志
docker-compose logs | grep ERROR
```

### 3. 资源使用监控

```bash
# 查看容器资源使用
docker stats openwrt-config-generator
```

## 🔄 更新和维护

### 更新代码

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose down
docker-compose up -d

# 4. 重新生成 menu.json（如果 Kconfig 有变化）
docker-compose exec openwrt-config-generator python parse_kconfig.py
```

### 更新 OpenWrt 源码

```bash
# 1. 更新源码
cd /path/to/your/openwrt
git pull
./scripts/feeds update -a
./scripts/feeds install -a

# 2. 重新生成 menu.json
docker-compose exec openwrt-config-generator python parse_kconfig.py
```

### 清理和重置

```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi openwrt-config-generator

# 完全重建
docker-compose build --no-cache
docker-compose up -d
```

## 📞 获取帮助

如果遇到问题：

1. 查看 [README.md](README.md) 中的故障排除部分
2. 检查 Docker 日志：`docker-compose logs`
3. 提交 Issue，包含以下信息：
   - 错误信息
   - Docker 版本
   - 操作系统版本
   - 完整的日志输出

## ✅ 部署完成确认

完成以下检查后，您的部署就绪：

- [ ] 容器正常运行（`docker-compose ps` 显示 Up）
- [ ] 健康检查通过
- [ ] 前端页面可访问
- [ ] menu.json 加载成功
- [ ] 配置生成功能正常
- [ ] 依赖逻辑工作正常
- [ ] 自动选择功能正常

恭喜！您已成功部署 OpenWrt Config Generator！🎉
