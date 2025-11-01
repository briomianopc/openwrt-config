import os
import subprocess
import tempfile
import re
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS # 处理跨域请求

# --- 配置 ---
OPENWRT_SRC_PATH = "/mnt/openwrt_source"

# --- Flask App ---
app = Flask(__name__)
# 允许来自任何源的 /generate-config 请求 (在开发中方便)
CORS(app, resources={r"/generate-config": {"origins": "*"}})

@app.route('/generate-config', methods=['POST'])
def generate_config():
    """
    API 端点：接收前端的选项, 生成并返回 .config 文件
    """
    try:
        # 1. 获取前端发送的 JSON 数据
        # 格式: {"CONFIG_TARGET_x86_64": "y", "CONFIG_PACKAGE_luci": "y"}
        user_options = request.json
        if not user_options:
            return jsonify({"error": "No options provided"}), 400

        # 2. 在 OpenWrt 源码目录中创建一个临时的 .config
        # (使用临时文件更安全, 但在源码树中操作更简单)
        config_path = os.path.join(OPENWRT_SRC_PATH, ".config")
            
        print(f"Generating .config in {config_path}")
            
        with open(config_path, 'w', encoding='utf-8') as f:
            # 写入一个基础的 "defconfig" (可选, 但推荐)
            f.write("# Base config\n")
            
            for key, value in user_options.items():
                # 安全检查: 确保是合法的Kconfig键
                if re.match(r'^CONFIG_[\w_]+$', key):
                    # 写入用户选择
                    if value == 'y':
                         f.write(f"{key}=y\n")
                    # (生产环境还需处理 string 和 int)
                    elif isinstance(value, str):
                        f.write(f'{key}="{value}"\n')
                    elif isinstance(value, (int, float)):
                        f.write(f'{key}={value}\n')
                else:
                    print(f"Skipping invalid key: {key}")

        # 3. 【最关键的步骤】
        # 在 OpenWrt 源码目录中, 运行 'make defconfig'
        # 它会读取我们刚写入的 .config, 并自动计算所有必需的依赖项！
        
        print(f"Running 'make defconfig' in {OPENWRT_SRC_PATH}...")
        
        # 环境变量, 告诉 make 我们在 "non-interactive" 模式
        env = os.environ.copy()
        env["TOPDIR"] = OPENWRT_SRC_PATH
        env["DEBIAN_FRONTEND"] = "noninteractive" # 避免卡住
        
        process = subprocess.run(
            ['make', 'defconfig'],
            cwd=OPENWRT_SRC_PATH,
            env=env,
            capture_output=True,
            text=True,
            timeout=60 # 60秒超时
        )

        if process.returncode != 0:
            print("Error running 'make defconfig':", process.stderr)
            return jsonify({"error": "Failed to resolve dependencies", "details": process.stderr}), 500

        print("'make defconfig' successful.")

        # 4. 将最终生成的、包含所有依赖的 .config 文件发送给用户
        # 'make defconfig' 会覆盖我们传入的 .config 文件
        return send_file(
            config_path,
            as_attachment=True,
            download_name=".config",
            mimetype="text/plain"
        )

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
