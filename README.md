# OpenWrt 在线配置生成器

这是一个基于 Web 的 OpenWrt `.config` 文件生成器，支持完整的 Kconfig 依赖解析和自动选择逻辑。

## ✨ 特性

- 🎯 **完整的 Kconfig 依赖解析**：支持复杂的依赖表达式（`&&`, `||`, `!`, 括号等）
- 🔄 **自动选择逻辑**：当选择某个选项时，自动启用其依赖的选项
- 🌳 **递归菜单树**：自动构建层级菜单结构
- 🐳 **Docker 部署**：一键部署，无需复杂配置
- 🚀 **生产就绪**：使用 Gunicorn 作为 WSGI 服务器
- 📡 **健康检查**：内置健康检查端点

## 📋 系统要求

- Python 3.11+
- Docker & Docker Compose（可选，推荐）
- OpenWrt 源码（已执行 `./scripts/feeds update -a` 和 `./scripts/feeds install -a`）

## 🚀 快速开始

### 方法 1: Docker Compose（推荐）

1. **克隆项目并修改配置**

```bash
# 编辑 docker-compose.yml
# 将 /path/to/your/openwrt 修改为您的 OpenWrt 源码路径
vim docker-compose.yml
```

2. **构建并启动容器**

```bash
docker-compose up -d
```

3. **生成 menu.json**

```bash
# 方法 A: 在容器内生成
docker-compose exec openwrt-config-generator python parse_kconfig.py

# 方法 B: 在宿主机生成（如果已安装 Python 环境）
python parse_kconfig.py --src-path /path/to/your/openwrt --output ./menu.json
```

4. **访问应用**

打开浏览器访问: http://localhost:5000

### 方法 2: 本地运行

1. **安装依赖**

```bash
pip install -r requirements.txt
```

2. **设置环境变量**

```bash
export OPENWRT_SRC_PATH=/path/to/your/openwrt
export STATIC_DIR=$(pwd)
export OUTPUT_JSON_PATH=./menu.json
```

3. **生成配置菜单**

```bash
python parse_kconfig.py --src-path $OPENWRT_SRC_PATH --output menu.json
```

4. **启动服务器**

```bash
# 开发模式
python api.py

# 生产模式
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 180 api:app
```

5. **访问应用**

打开浏览器访问: http://localhost:5000

## 📁 项目结构

```
.
├── api.py                  # Flask 后端服务
├── parse_kconfig.py        # Kconfig 解析器
├── index.html              # Vue.js 前端
├── requirements.txt        # Python 依赖
├── Dockerfile              # Docker 镜像定义
├── docker-compose.yml      # Docker Compose 配置
├── .dockerignore           # Docker 构建忽略文件
├── menu.json              # 生成的配置菜单（需要运行 parse_kconfig.py）
└── README.md              # 本文档
```

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

## 🐛 故障排除

### 问题：menu.json 加载失败

**原因**: 未生成 menu.json 文件

**解决**:
```bash
# Docker 环境
docker-compose exec openwrt-config-generator python parse_kconfig.py

# 本地环境
python parse_kconfig.py --src-path /path/to/openwrt
```

### 问题：make defconfig 失败

**原因**: OpenWrt 源码未正确准备

**解决**:
```bash
cd /path/to/openwrt
./scripts/feeds update -a
./scripts/feeds install -a
```

### 问题：容器启动后无法访问

**检查**:
```bash
# 查看容器日志
docker-compose logs -f

# 检查健康状态
curl http://localhost:5000/health
```

## 🔐 安全建议

1. **生产环境**: 设置 `CORS_ORIGINS` 为具体的域名列表
2. **限制访问**: 使用反向代理（如 Nginx）限制访问
3. **源码保护**: OpenWrt 源码目录建议以只读方式挂载
4. **定期更新**: 及时更新依赖包以修复安全漏洞

## 📊 性能优化

1. **Worker 数量**: 根据 CPU 核心数调整 `--workers` 参数
2. **超时设置**: 根据 OpenWrt 项目大小调整 `--timeout` 参数
3. **缓存机制**: 可以将 menu.json 缓存到 CDN

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [kconfiglib](https://github.com/ulfalizer/Kconfiglib) - Kconfig 解析库
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Vue.js](https://vuejs.org/) - 前端框架
- [OpenWrt](https://openwrt.org/) - 开源路由器固件

## 📞 联系方式

如有问题，请提交 Issue 或联系维护者。

---

**注意**: 本项目仅用于生成 OpenWrt 配置文件，不包含 OpenWrt 编译功能。
