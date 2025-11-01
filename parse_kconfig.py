import json
import os
import sys
import argparse
from kconfiglib import Kconfig

# --- 配置 ---
# 从环境变量读取 OpenWrt 源码路径，提供默认值
OPENWRT_SRC_PATH = os.environ.get("OPENWRT_SRC_PATH", "/mnt/openwrt_source")
# Kconfiglib 需要这个根 Kconfig 文件
ROOT_KCONFIG = os.path.join(OPENWRT_SRC_PATH, "Kconfig")

# 输出的 JSON 文件, 将给前端使用
OUTPUT_JSON = os.environ.get("OUTPUT_JSON_PATH", "menu.json")

def serialize_symbol(sym):
    """
    将一个 Kconfig 'Symbol' (即一个 CONFIG_XXX 选项) 序列化为字典
    """
    # 过滤掉没有用户提示的内部选项, 它们不需要在前端显示
    if not sym.prompt:
        return None

    # kconfiglib 会返回 (prompt, condition) 的元组列表
    # 我们只取第一个 prompt
    prompt, _ = sym.prompt[0]

    return {
        "id": sym.name,          # "CONFIG_TARGET_x86_64"
        "type": sym.type_name,   # "bool", "string", "int"
        "prompt": prompt,        # "Enable this feature"
        "help": sym.help if sym.help else "",
        
        # 依赖关系 (转为字符串, 供前端JS解析或显示)
        # direct_depends 是一个表达式对象, str() 会将其转为 "(A && B) || C" 这样的字符串
        "depends_on": str(sym.direct_depends), 
        
        # 自动选择: 'select ...'
        # sym.selects 是一个 (Symbol, condition) 的元组列表
        "selects": [sel_sym.name for sel_sym, cond in sym.selects],
        
        # 默认值
        "default": [str(d[0]) for d in sym.defaults],
        
        # 菜单路径 (用于前端构建树)
        "menu_path": get_menu_path(sym)
    }

def get_menu_path(sym):
    """
    辅助函数: 获取一个选项在菜单中的路径, 例如 ["Target", "x86", "Generic"]
    """
    path = []
    node = sym.menu_node
    while node:
        # 我们只关心有标题的菜单 (menu "Title" or menuconfig "Title")
        if node.prompt and (node.is_menu or node.is_menuconfig):
            path.append(node.prompt[0]) # (prompt, condition)
        node = node.parent
        
    # 移除根节点 (通常是 "Main Menu")
    if path:
        path.pop() 
        
    return list(reversed(path)) # 反转得到 "根 -> 叶" 的路径

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='Parse OpenWrt Kconfig and generate menu.json'
    )
    parser.add_argument(
        '--src-path',
        default=OPENWRT_SRC_PATH,
        help=f'Path to OpenWrt source directory (default: {OPENWRT_SRC_PATH})'
    )
    parser.add_argument(
        '--output',
        default=OUTPUT_JSON,
        help=f'Output JSON file path (default: {OUTPUT_JSON})'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    src_path = args.src_path
    output_path = args.output
    root_kconfig = os.path.join(src_path, "Kconfig")
    
    # 检查源码目录是否存在
    if not os.path.exists(src_path):
        print(f"Error: OpenWrt source directory not found: {src_path}", file=sys.stderr)
        print("Please set OPENWRT_SRC_PATH environment variable or use --src-path", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(root_kconfig):
        print(f"Error: Kconfig file not found: {root_kconfig}", file=sys.stderr)
        print("Please ensure you have a valid OpenWrt source tree", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading Kconfig from: {root_kconfig}")
    
    # Kconfiglib 需要一些环境变量来正确解析, 就像 'make menuconfig' 一样
    # 我们需要模拟它们。最重要的是 TOPDIR。
    os.environ["TOPDIR"] = src_path
    
    try:
        # warn_to_stderr=False 避免在解析 feeds 时产生过多噪音
        kconf = Kconfig(root_kconfig, warn_to_stderr=args.verbose)
    except Exception as e:
        print(f"Error loading Kconfig: {e}", file=sys.stderr)
        print("Tip: Did you run './scripts/feeds update -a' and './scripts/feeds install -a'?", file=sys.stderr)
        sys.exit(1)

    print("Kconfig loaded. Parsing all symbols...")
    
    all_options = []
    # kconf.syms 是一个包含所有 CONFIG_XXX 的字典
    for sym in kconf.syms.values():
        data = serialize_symbol(sym)
        if data:
            all_options.append(data)

    print(f"Found {len(all_options)} user-visible config options.")

    # 写入 JSON 文件
    try:
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_options, f, indent=2, ensure_ascii=False)
        print(f"Successfully generated {output_path}")
    except Exception as e:
        print(f"Error writing JSON: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
