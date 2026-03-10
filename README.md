# 蓝奏云分享链接批量获取工具

基于 Scrapling 框架开发的蓝奏云文件分享链接批量获取工具，可绕过蓝奏云的反爬虫机制，获取账号内所有文件（包括子文件夹）的分享链接。

## 功能特点

- ✅ 绕过蓝奏云反爬虫检测
- ✅ 自动加载所有文件（点击"显示更多"）
- ✅ 递归扫描所有子文件夹
- ✅ 支持多层嵌套文件夹
- ✅ 支持 Windows/Linux 服务器运行
- ✅ Headless 模式，无需图形界面
- ✅ 结果保存为 TXT 文件

## 目录结构

```
lanzou_tool/
├── lanzou_get_shares.py      # 主脚本
├── scrapling_framework/       # Scrapling 框架
│   └── scrapling/            # 框架核心代码
├── browser_data/             # 浏览器数据目录（自动创建）
├── README.md                 # 说明文档
└── requirements.txt          # 依赖列表
```

## 安装依赖

### Windows

```bash
pip install playwright camoufox curl_cffi
playwright install chromium
```

### Linux (Ubuntu/Debian)

```bash
# 安装 Python 依赖
pip install playwright camoufox curl_cffi

# 安装浏览器
playwright install chromium

# 安装系统依赖
sudo apt-get update
sudo apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libpango-1.0-0 libcairo2
```

## 获取蓝奏云凭证

1. 登录蓝奏云：https://up.woozooo.com/
2. 按 `F12` 打开开发者工具
3. 切换到 `Application`（应用程序）标签
4. 在左侧找到 `Cookies` -> `https://up.woozooo.com`
5. 复制 `ylogin` 和 `phpdisk_info` 的值

![获取Cookie示意图](https://via.placeholder.com/600x300?text=F12+->+Application+->+Cookies)

## 使用方法

### 1. 配置凭证

编辑 `lanzou_get_shares.py`，修改以下内容：

```python
ylogin = 'YOUR_YLOGIN_HERE'        # 替换为你的 ylogin 值
phpdisk_info = 'YOUR_PHPDISK_INFO_HERE'  # 替换为你的 phpdisk_info 值
```

### 2. 运行脚本

```bash
python lanzou_get_shares.py
```

### 3. 查看结果

运行完成后，结果保存在 `lanzou_shares.txt` 文件中，格式如下：

```
文件夹路径	文件名	分享链接	密码
```

## 输出示例

```
根目录
  斗破苍穹萧炎.txt
  链接: https://www.lanzoui.com/iwiTj3k8lfzi 密码: hji0

[sss]
  1772972469251_斗破苍穹萧炎.txt
  链接: https://www.lanzoui.com/iXdgf3k91aaj 密码: 89y7
```

## Linux 服务器运行

### 后台运行

```bash
# 使用 nohup
nohup python lanzou_get_shares.py > output.log 2>&1 &

# 或使用 screen
screen -S lanzou
python lanzou_get_shares.py
# Ctrl+A+D 退出 screen
```

### 定时任务

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点运行
0 2 * * * cd /path/to/lanzou_tool && python lanzou_get_shares.py >> /var/log/lanzou.log 2>&1
```

## 资源占用

| 资源 | 占用情况 |
|------|----------|
| 内存 | 约 200-400 MB |
| CPU | 低（主要是等待网络） |
| 磁盘 | 约 500 MB（浏览器 + 数据目录） |
| 运行时间 | 约 1-2 分钟（100个文件） |

## 常见问题

### Q: 提示 "folder is not defined" 错误

A: 这是正常的，脚本会自动使用 URL 导航方式进入文件夹。

### Q: 获取到的文件数量不对

A: 确保脚本有足够时间加载所有文件，可以增加 `time.sleep()` 的等待时间。

### Q: Linux 上运行报错

A: 确保已安装所有系统依赖，参考上面的安装说明。

### Q: Cookie 过期

A: 蓝奏云的 Cookie 有效期较长，但如果提示未登录，请重新获取 Cookie。

## 技术原理

1. **绕过反爬虫**：使用 Scrapling 的 `StealthySession`，模拟真实浏览器指纹
2. **持久化会话**：使用 `user_data_dir` 保存浏览器状态
3. **DOM 提取**：直接从页面 DOM 提取文件信息，避免 API 返回假数据
4. **URL 导航**：通过 URL 参数直接访问文件夹，不依赖 JavaScript 函数

## 依赖说明

- **playwright**: 浏览器自动化
- **camoufox**: 浏览器指纹伪装
- **curl_cffi**: HTTP 请求模拟

## 免责声明

本工具仅供学习交流使用，请勿用于非法用途。使用本工具所产生的一切后果由使用者自行承担。

## 更新日志

### v1.0.0 (2026-03-10)
- 首次发布
- 支持获取所有文件分享链接
- 支持递归扫描子文件夹
- 支持自动加载更多文件
