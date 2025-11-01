# OpenWrt 在线配置生成器

一个功能完整的 Web 应用，用于可视化生成 OpenWrt 固件的 `.config` 配置文件。支持完整的 Kconfig 依赖解析、自动选择逻辑和交互式配置界面。

## ✨ 核心特性

### 前端功能
- 🎯 **智能依赖解析**
  - 支持复杂的 Kconfig 表达式：`&&`, `||`, `!`, `==`, `!=`, `<`, `>`, 括号分组等
  - 实时依赖检查，不满足条件的选项自动禁用
  - 使用调度场算法（Shunting Yard）和栈式求值实现

- 🔄 **自动选择机制**
  - 选择某个选项时，自动勾选其依赖项（selects）
  - 自动选择的项会被锁定，显示为蓝色并标记 "[自动选择]"
  - 基于 Vue 3 watch 监听器的响应式更新

- 🌳 **递归菜单树**
  - 根据 menu_path 自动构建层级菜单
  - 支持任意深度的嵌套结构
  - 清晰的视觉层级展示

### 后端功能
- 🐳 **生产就绪**
  - 使用 Gunicorn WSGI 服务器
  - 支持并发请求处理
  - 完整的日志系统

- 🔒 **安全可靠**
  - 环境变量配置，避免硬编码
  - 输入验证和错误处理
  - 线程锁保护并发操作
  - 配置文件自动备份和恢复

- 📡 **API 端点**
  - 健康检查端点
  - 静态文件服务
  - 配置生成接口

## 📋 系统要求

### 必需
- **Python**: 3.11 或更高版本
- **OpenWrt 源码**: 已准备好的 OpenWrt 源码树

### 可选（推荐）
- **Docker**: 20.10+
- **Docker Compose**: 1.29+

## 🚀 部署教程

### 📦 准备工作

#### 1. 准备 OpenWrt 源码

```bash
# 克隆 OpenWrt 源码
git clone https://git.openwrt.org/openwrt/openwrt.git
cd openwrt

# 更新 feeds
./scripts/feeds update -a

# 安装 feeds
./scripts/feeds install -a

# 记录源码路径（后续需要用到）
pwd
# 例如: /home/user/openwrt
```

#### 2. 克隆本项目

```bash
git clone <your-repo-url>
cd openwrt-config-generator
```

---

### 🐳 方法一：Docker 部署（推荐）

这是最简单、最可靠的部署方式。

#### 步骤 1：配置 OpenWrt 源码路径

编辑 `docker-compose.yml`：

```bash
vim docker-compose.yml
```

找到并修改以下行：

```yaml
volumes:
  # 将左边的路径改为你的 OpenWrt 源码路径
  - /home/user/openwrt:/mnt/openwrt_source:ro
```

例如：
```yaml
volumes:
  - /home/user/openwrt:/mnt/openwrt_source:ro
```

#### 步骤 2：一键启动

```bash
./start.sh
```

脚本会自动完成：
- ✅ 检查 Docker 环境
- ✅ 构建 Docker 镜像
- ✅ 启动容器
- ✅ 进行健康检查
- ✅ 生成 menu.json（如果不存在）

#### 步骤 3：访问应用

打开浏览器访问：**http://localhost:5000**

#### 常用 Docker 命令

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 完全清理
docker-compose down

# 重新生成 menu.json
docker-compose exec openwrt-config-generator \
  python parse_kconfig.py
```

---

### 💻 方法二：本地部署

如果你不想使用 Docker，可以直接在本地运行。

#### 步骤 1：安装 Python 依赖

```bash
# 推荐使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 步骤 2：配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
vim .env
```

编辑内容：

```bash
# OpenWrt 源码路径（必须修改）
OPENWRT_SRC_PATH=/home/user/openwrt

# 静态文件目录（通常不需要修改）
STATIC_DIR=/path/to/openwrt-config-generator

# 输出的 menu.json 路径
OUTPUT_JSON_PATH=/path/to/openwrt-config-generator/menu.json

# 服务器端口
PORT=5000

# 调试模式（生产环境设为 False）
DEBUG=False

# CORS 设置（生产环境设为具体域名）
CORS_ORIGINS=*
```

#### 步骤 3：生成 menu.json

```bash
python3 parse_kconfig.py \
  --src-path /home/user/openwrt \
  --output ./menu.json
```

**参数说明：**
- `--src-path`: OpenWrt 源码路径
- `--output`: 输出的 JSON 文件路径
- `--verbose`: 显示详细日志（可选）

#### 步骤 4：启动服务器

**开发模式：**
```bash
python3 api.py
```

**生产模式（推荐）：**
```bash
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --timeout 180 \
         --access-logfile - \
         --error-logfile - \
         api:app
```

**参数说明：**
- `--workers 4`: 使用 4 个工作进程（根据 CPU 核心数调整）
- `--timeout 180`: 超时时间 180 秒
- `--access-logfile -`: 访问日志输出到标准输出
- `--error-logfile -`: 错误日志输出到标准输出

#### 步骤 5：访问应用

打开浏览器访问：**http://localhost:5000**

---

## 📖 使用指南

### 界面操作

1. **浏览配置选项**
   - 配置项按菜单路径组织成树形结构
   - 灰色表示被禁用（依赖未满足）
   - 蓝色带 "[自动选择]" 表示自动选中且锁定

2. **选择配置**
   - 勾选需要的功能
   - 系统会自动：
     - 禁用不满足依赖的选项
     - 自动选择必需的依赖项
     - 锁定被自动选择的项

3. **生成配置文件**
   - 点击 "生成 .config 文件" 按钮
   - 系统会调用 `make defconfig` 解析所有依赖
   - 自动下载生成的 `.config` 文件

### 依赖逻辑示例

```javascript
// 简单依赖
CONFIG_TARGET_x86_64 depends on CONFIG_TARGET_x86
// 未勾选 x86 时，x86_64 会被禁用（灰色）

// 复杂依赖（与）
CONFIG_APP_VPN depends on "CONFIG_LUCI && CONFIG_OPENVPN"
// 必须同时勾选 LuCI 和 OpenVPN

// 复杂依赖（或、非）
CONFIG_ADVANCED depends on "(CONFIG_x86 || CONFIG_x86_64) && !CONFIG_DEBUG"
// 需要 x86 或 x86_64，且不启用 DEBUG

// 自动选择
CONFIG_LUCI selects CONFIG_UHTTPD
// 勾选 LuCI 会自动勾选 uHTTPd（蓝色锁定）
```

---

## 📁 项目结构

```
openwrt-config-generator/
├── api.py                  # Flask 后端服务
├── parse_kconfig.py        # Kconfig 解析器  
├── index.html              # Vue.js 前端
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 镜像定义
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore           # Docker 构建忽略
├── .env.example            # 环境变量模板
├── start.sh                # Docker 一键启动脚本
├── README.md               # 项目文档（本文件）
├── DEPLOYMENT.md           # 详细部署指南
├── CHANGELOG.md            # 变更日志
└── PROJECT_SUMMARY.md      # 项目技术总结
```

**注意**：`menu.json` 需要运行 `parse_kconfig.py` 生成，不包含在代码仓库中。

## 🔧 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `OPENWRT_SRC_PATH` | `/mnt/openwrt_source` | OpenWrt 源码目录路径 |
| `STATIC_DIR` | 当前目录 | 静态文件目录 |
| `OUTPUT_JSON_PATH` | `menu.json` | 配置菜单输出路径 |
| `PORT` | `5000` | 服务器监听端口 |
| `DEBUG` | `False` | 调试模式 |
| `CORS_ORIGINS` | `*` | CORS 允许的源（生产环境建议设置具体域名） |

### parse_kconfig.py 命令行参数

```bash
python parse_kconfig.py --help

选项:
  --src-path PATH    OpenWrt 源码目录路径
  --output PATH      输出 JSON 文件路径
  --verbose          启用详细输出
```

## 🌐 API 端点

### GET /
返回主页（index.html）

### GET /menu.json
返回配置菜单 JSON 数据

### GET /health
健康检查端点

响应示例:
```json
{
  "status": "healthy",
  "openwrt_src_exists": true,
  "menu_json_exists": true
}
```

### POST /generate-config
生成 .config 文件

请求体:
```json
{
  "CONFIG_TARGET_x86_64": "y",
  "CONFIG_PACKAGE_luci": "y"
}
```

响应: 下载 `.config` 文件

## 🔍 前端功能说明

### Kconfig 表达式解析

前端实现了完整的 Kconfig 表达式解析器，支持：

- **逻辑运算符**: `&&`, `||`, `!`
- **比较运算符**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **括号分组**: `()`
- **复杂表达式**: `(CONFIG_A && CONFIG_B) || !CONFIG_C`

### 自动选择逻辑

当用户勾选某个选项时，系统会自动：
1. 勾选该选项通过 `selects` 指定的所有依赖项
2. 锁定这些自动选择的选项（显示为蓝色，无法手动取消）
3. 实时更新依赖状态

### 依赖禁用逻辑

当某个选项的依赖条件不满足时，该选项会被禁用（显示为灰色）。

---

## 🐛 故障排除

### 问题 1：menu.json 加载失败

**现象**：浏览器提示 "无法加载 menu.json"

**原因**：未生成 menu.json 文件

**解决方案**：

```bash
# Docker 环境
docker-compose exec openwrt-config-generator \
  python parse_kconfig.py

# 本地环境  
python3 parse_kconfig.py \
  --src-path /path/to/openwrt \
  --output ./menu.json
```

### 问题 2：make defconfig 失败

**现象**：生成配置时报错 "Failed to resolve dependencies"

**原因**：OpenWrt 源码未正确准备

**解决方案**：

```bash
cd /path/to/openwrt

# 更新 feeds
./scripts/feeds update -a

# 安装 feeds
./scripts/feeds install -a

# 验证 Kconfig 存在
ls -la Kconfig
```

### 问题 3：容器启动失败

**现象**：`docker-compose up` 报错

**原因**：配置错误或端口冲突

**解决方案**：

```bash
# 查看详细日志
docker-compose logs --tail=50

# 检查端口是否被占用
netstat -tulpn | grep 5000

# 重新构建镜像
docker-compose build --no-cache

# 清理并重启
docker-compose down
docker-compose up -d
```

### 问题 4：OpenWrt 源码路径错误

**现象**：健康检查显示 `openwrt_src_exists: false`

**原因**：Docker 卷挂载路径不正确

**解决方案**：

1. 检查 `docker-compose.yml` 中的路径：
```yaml
volumes:
  - /correct/path/to/openwrt:/mnt/openwrt_source:ro
```

2. 确保路径存在且可读：
```bash
ls -la /correct/path/to/openwrt/Kconfig
```

3. 重启容器：
```bash
docker-compose restart
```

### 问题 5：Python 依赖安装失败

**现象**：`pip install` 报错

**原因**：网络问题或 Python 版本不兼容

**解决方案**：

```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 升级 pip
python3 -m pip install --upgrade pip

# 检查 Python 版本（需要 3.11+）
python3 --version
```

### 问题 6：前端页面空白

**现象**：打开 http://localhost:5000 页面空白

**排查步骤**：

1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签页是否有错误
3. 查看 Network 标签页，检查 `menu.json` 是否加载成功

**常见原因**：
- menu.json 不存在 → 运行 parse_kconfig.py
- JavaScript 错误 → 检查浏览器控制台
- API 无响应 → 检查后端日志

### 问题 7：配置生成超时

**现象**：点击"生成配置"后长时间无响应

**原因**：OpenWrt 项目过大，make defconfig 耗时长

**解决方案**：

调整超时时间：

**Docker 方式**：
编辑 `Dockerfile`，增加 timeout：
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "api:app"]
```

**本地方式**：
```bash
gunicorn --bind 0.0.0.0:5000 --timeout 300 api:app
```

---

## 🔐 生产环境部署建议

### 1. CORS 配置

**开发环境**：
```bash
CORS_ORIGINS=*
```

**生产环境**：
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. 使用 Nginx 反向代理

创建 Nginx 配置 `/etc/nginx/sites-available/openwrt-config`：

```nginx
server {
    listen 80;
    server_name config.yourdomain.com;

    # SSL 配置（推荐）
    # listen 443 ssl http2;
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 增加超时时间（用于配置生成）
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/openwrt-config /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 配置 HTTPS

使用 Let's Encrypt：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d config.yourdomain.com
```

### 4. 设置系统服务

创建 systemd 服务文件 `/etc/systemd/system/openwrt-config.service`：

```ini
[Unit]
Description=OpenWrt Config Generator
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/openwrt-config-generator
Environment="OPENWRT_SRC_PATH=/path/to/openwrt"
Environment="DEBUG=False"
Environment="CORS_ORIGINS=https://yourdomain.com"
ExecStart=/usr/local/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 4 \
    --timeout 180 \
    api:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable openwrt-config
sudo systemctl start openwrt-config
sudo systemctl status openwrt-config
```

### 5. 资源限制

在 `docker-compose.yml` 中添加：

```yaml
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

### 6. 日志管理

**Docker 日志配置**：
```yaml
services:
  openwrt-config-generator:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

**本地日志配置**：
```bash
gunicorn --bind 0.0.0.0:5000 \
         --access-logfile /var/log/openwrt-config/access.log \
         --error-logfile /var/log/openwrt-config/error.log \
         api:app
```

### 7. 定期备份

创建备份脚本 `/usr/local/bin/backup-openwrt-config.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/backup/openwrt-config"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/menu_json_$DATE.tar.gz" \
    /path/to/openwrt-config-generator/menu.json

# 保留最近 7 天的备份
find "$BACKUP_DIR" -name "menu_json_*.tar.gz" -mtime +7 -delete
```

添加到 crontab：
```bash
0 2 * * * /usr/local/bin/backup-openwrt-config.sh
```

---

## 📊 性能优化建议

### 1. Worker 进程数

根据 CPU 核心数设置：
```bash
# 公式：(2 × CPU核心数) + 1
# 4核 CPU 使用 9 个 worker
gunicorn --workers 9 api:app
```

### 2. 缓存 menu.json

使用 CDN 或 Redis 缓存：

```python
# 示例：添加到 api.py
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/menu.json')
@cache.cached(timeout=3600)  # 缓存 1 小时
def menu_json():
    return send_from_directory(STATIC_DIR, 'menu.json')
```

### 3. 压缩响应

启用 gzip 压缩：

```python
# 安装: pip install flask-compress
from flask_compress import Compress
Compress(app)
```

### 4. 优化前端加载

- 使用 CDN 加载 Vue.js
- 启用浏览器缓存
- 压缩静态资源

---

## 🧪 测试验证

部署完成后，进行以下测试：

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

### 2. 前端访问
在浏览器中打开 `http://localhost:5000`，验证：
- ✅ 页面正常加载
- ✅ 配置树正确显示
- ✅ 依赖逻辑工作正常
- ✅ 自动选择功能正常

### 3. 配置生成
选择几个配置项，点击"生成 .config 文件"，验证：
- ✅ 成功下载 .config 文件
- ✅ 文件内容包含所选配置
- ✅ 依赖项被正确解析

---

## 📚 相关文档

- **详细部署指南**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **变更日志**: [CHANGELOG.md](CHANGELOG.md)
- **技术总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- Python 代码遵循 PEP 8
- JavaScript 使用 ES6+ 语法
- 提交信息使用中文，格式：`类型: 简短描述`

---

## 📄 许可证

MIT License

---

## 🙏 致谢

感谢以下开源项目：

- [kconfiglib](https://github.com/ulfalizer/Kconfiglib) - Kconfig 解析库
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [OpenWrt](https://openwrt.org/) - 开源嵌入式 Linux 发行版
- [Gunicorn](https://gunicorn.org/) - Python WSGI HTTP 服务器

---

## 📞 支持

如有问题或建议：

- 📧 提交 [Issue](../../issues)
- 💬 参与 [Discussions](../../discussions)
- 📖 查看 [Wiki](../../wiki)

---

## ⚠️ 免责声明

本项目仅用于生成 OpenWrt 配置文件，不包含 OpenWrt 编译功能。使用本工具生成的配置文件，请在充分测试后再用于生产环境。

---

**最后更新**: 2025-11-01  
**版本**: 1.0.0  
**维护状态**: 积极维护中 ✅
