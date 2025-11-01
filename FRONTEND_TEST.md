# 前端功能测试指南

## 🎯 测试目标

验证前端的 Kconfig 依赖逻辑和自动选择功能是否正常工作。

## 🚀 启动测试

### 1. 启动服务器

```bash
cd /workspace
python3 api.py
```

### 2. 打开浏览器

访问: http://localhost:5000

---

## ✅ 测试清单

### 测试 1: 页面加载 ✓

**预期结果:**
- ✅ 页面正常加载，无 JavaScript 错误
- ✅ 显示 "OpenWrt 配置生成器 (Dev)" 标题
- ✅ 菜单树正确渲染
- ✅ 可以看到多个配置项

**实际测试:**
- [ ] 打开浏览器控制台 (F12)
- [ ] 检查是否有红色错误
- [ ] 确认页面内容显示正常

---

### 测试 2: 菜单树结构 ✓

**预期结果:**
- ✅ 配置项按菜单路径分组
- ✅ 可以看到层级结构：
  - Target → Architecture
  - LuCI → Applications
  - Network → VPN
  等等

**实际测试:**
- [ ] 检查是否有菜单分组
- [ ] 确认层级缩进正确

---

### 测试 3: 简单依赖 (depends_on) ✓

**测试步骤:**

1. **测试用例 A**: CONFIG_TARGET_x86_64
   - 初始状态: CONFIG_TARGET_x86_64 应该是**禁用**的（灰色）
   - 原因: 它依赖于 CONFIG_TARGET_x86
   - **操作**: 勾选 `CONFIG_TARGET_x86`
   - **预期**: CONFIG_TARGET_x86_64 变为**可选**（黑色）

2. **测试用例 B**: CONFIG_TARGET_ROOTFS_EXT4
   - 初始状态: 应该是**禁用**的
   - 原因: 它依赖于 CONFIG_TARGET_x86_64
   - **操作**: 依次勾选 CONFIG_TARGET_x86 和 CONFIG_TARGET_x86_64
   - **预期**: CONFIG_TARGET_ROOTFS_EXT4 变为**可选**

**实际测试:**
- [ ] CONFIG_TARGET_x86_64 初始禁用
- [ ] 勾选 CONFIG_TARGET_x86 后，x86_64 可选
- [ ] CONFIG_TARGET_ROOTFS_EXT4 依赖正确

---

### 测试 4: 复杂依赖表达式 (&&) ✓

**测试步骤:**

1. **测试用例**: CONFIG_PACKAGE_luci_app_vpn
   - 依赖表达式: `CONFIG_PACKAGE_luci && CONFIG_PACKAGE_openvpn`
   - 需要**同时**满足两个条件

**操作序列:**
   - [ ] 初始状态: CONFIG_PACKAGE_luci_app_vpn 应该是**禁用**的
   - [ ] 只勾选 CONFIG_PACKAGE_luci → 仍然**禁用**
   - [ ] 再勾选 CONFIG_PACKAGE_openvpn → 变为**可选**
   - [ ] 取消 CONFIG_PACKAGE_luci → 又变回**禁用**

**实际测试:**
- [ ] && 逻辑正确
- [ ] 必须同时满足两个条件

---

### 测试 5: 复杂依赖表达式 (||) ✓

**测试步骤:**

1. **测试用例**: CONFIG_ADVANCED_FEATURES
   - 依赖表达式: `(CONFIG_TARGET_x86 || CONFIG_TARGET_x86_64) && !CONFIG_KERNEL_DEBUG`
   - 需要满足: (x86 或 x86_64) 并且 不启用 KERNEL_DEBUG

**操作序列:**
   - [ ] 初始状态: 应该是**禁用**的
   - [ ] 勾选 CONFIG_TARGET_x86 → 变为**可选** (因为 KERNEL_DEBUG 未启用)
   - [ ] 勾选 CONFIG_KERNEL_DEBUG → 又变回**禁用** (因为 ! 取反)
   - [ ] 取消 CONFIG_KERNEL_DEBUG → 重新**可选**

**实际测试:**
- [ ] || 逻辑正确
- [ ] ! 取反正确
- [ ] 复杂表达式解析正确

---

### 测试 6: 自动选择 (selects) ✓

**测试步骤:**

1. **测试用例 A**: CONFIG_TARGET_x86
   - selects: `CONFIG_ARCH_X86`
   - **操作**: 勾选 CONFIG_TARGET_x86
   - **预期**:
     - ✅ CONFIG_ARCH_X86 **自动被勾选**
     - ✅ CONFIG_ARCH_X86 显示为**蓝色斜体**
     - ✅ CONFIG_ARCH_X86 有 "[自动选择]" 标记
     - ✅ CONFIG_ARCH_X86 的复选框是**禁用**的（无法取消）

2. **测试用例 B**: CONFIG_PACKAGE_luci
   - selects: `CONFIG_PACKAGE_uhttpd`, `CONFIG_PACKAGE_lua`
   - **操作**: 勾选 CONFIG_PACKAGE_luci
   - **预期**:
     - ✅ CONFIG_PACKAGE_uhttpd 自动被勾选并锁定
     - ✅ CONFIG_PACKAGE_lua 自动被勾选并锁定
     - ✅ 两者都显示为蓝色 + "[自动选择]"

3. **测试用例 C**: 级联自动选择
   - CONFIG_PACKAGE_luci → CONFIG_PACKAGE_uhttpd
   - CONFIG_PACKAGE_openvpn → CONFIG_PACKAGE_openssl
   - **操作**: 勾选 CONFIG_PACKAGE_luci 和 CONFIG_PACKAGE_openvpn
   - **预期**: 4 个选项自动被选中

**实际测试:**
- [ ] 单个 select 正常
- [ ] 多个 select 正常
- [ ] 级联 select 正常
- [ ] 锁定功能正常
- [ ] 视觉反馈正确（蓝色 + 标记）

---

### 测试 7: 取消选择后的依赖更新 ✓

**测试步骤:**

1. **操作序列**:
   - 勾选 CONFIG_TARGET_x86
   - CONFIG_ARCH_X86 自动被选中
   - 勾选 CONFIG_TARGET_x86_64 (现在可选了)
   - CONFIG_TARGET_ROOTFS_EXT4 现在可选
   - **取消勾选** CONFIG_TARGET_x86_64
   - **预期**: CONFIG_TARGET_ROOTFS_EXT4 重新变为**禁用**

**实际测试:**
- [ ] 取消选择后依赖正确更新
- [ ] 自动选择的项也正确解锁

---

### 测试 8: Debug 信息 ✓

**测试步骤:**

1. 勾选一些配置项
2. 查看页面底部的 "当前配置状态 (Debug)" 区域

**预期结果:**
- ✅ 只显示**启用**的配置项 (true 的项)
- ✅ JSON 格式化正确
- ✅ 包含自动选择的项

**实际测试:**
- [ ] Debug 信息显示正确
- [ ] 实时更新

---

### 测试 9: 生成配置文件 ⚠️

**测试步骤:**

1. 勾选一些配置项
2. 点击 "生成 .config 文件" 按钮

**预期结果 (无 OpenWrt 源码):**
- ✅ 显示错误提示: "生成失败: OpenWrt source directory not found"
- ✅ 这是**正常的**，因为没有配置 OpenWrt 源码

**实际测试:**
- [ ] 点击按钮
- [ ] 看到预期的错误提示

**注意**: 如需测试真实配置生成，需要:
1. 准备 OpenWrt 源码
2. 设置 `OPENWRT_SRC_PATH` 环境变量
3. 重启服务器

---

## 📊 测试结果总结

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 页面加载 | ⬜ |  |
| 菜单树结构 | ⬜ |  |
| 简单依赖 | ⬜ |  |
| 复杂依赖 (&&) | ⬜ |  |
| 复杂依赖 (\|\|, !) | ⬜ |  |
| 自动选择 | ⬜ |  |
| 取消选择 | ⬜ |  |
| Debug 信息 | ⬜ |  |
| 生成配置 | ⬜ |  |

---

## 🐛 已知问题

如果发现问题，请记录:

1. **问题描述**:
2. **重现步骤**:
3. **预期行为**:
4. **实际行为**:
5. **浏览器**:
6. **控制台错误** (如果有):

---

## 🎓 Kconfig 表达式语法参考

前端支持以下表达式:

```javascript
// 简单依赖
"CONFIG_A"

// 逻辑与
"CONFIG_A && CONFIG_B"

// 逻辑或
"CONFIG_A || CONFIG_B"

// 逻辑非
"!CONFIG_A"

// 括号分组
"(CONFIG_A || CONFIG_B) && CONFIG_C"

// 复杂嵌套
"(CONFIG_A && CONFIG_B) || (!CONFIG_C && CONFIG_D)"
```

---

## ✅ 测试完成确认

完成以上所有测试后，如果:
- ✅ 所有依赖逻辑正确
- ✅ 自动选择功能正常
- ✅ 视觉反馈清晰

则前端功能验证**通过**！🎉
