# TailChat AI 浏览器自动化机器人

一个使用Playwright模拟人类操作的TailChat AI机器人，通过浏览器自动化登录您的账号并自动回复消息。

## ✨ 特性

### 🤖 智能回复
- **私信自动回复**：所有私信消息都会智能回复
- **@消息必须回复**：群聊中@机器人的消息必须回复
- **AI驱动**：集成DeepSeek API，提供智能对话
- **上下文理解**：保持对话上下文，提供连贯回复

### 🎨 富媒体支持
- **表情符号**：支持发送各种表情
- **图片消息**：可以发送本地或网络图片
- **Git仓库图片**：支持从Git仓库获取并发送图片
- **网址链接**：自动识别和格式化网址

### ⏰ 智能调度
- **在线时间控制**：每天6:00-22:00在线
- **主动消息发送**：可以定时发送问候、提示等消息
- **休息时间处理**：非活动时间收到消息会礼貌回复

### 🔧 技术特点
- **浏览器自动化**：使用Playwright模拟人类操作
- **反检测机制**：模拟人类行为，避免被检测为机器人
- **稳定可靠**：完整的错误处理和重连机制
- **易于部署**：支持本地运行和GitHub Actions部署

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/qingshanjiluo/tailchat-bot.git
cd tailchat-bot

# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
python -m playwright install chromium
```

### 2. 配置设置

复制环境变量文件并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置以下必需配置：

```env
# TailChat 登录信息
TAILCHAT_USERNAME=您的用户名
TAILCHAT_PASSWORD=您的密码
TAILCHAT_API_URL=https://chat.mk49.cyou

# DeepSeek API
DEEPSEEK_API_KEY=您的DeepSeek API密钥

# 机器人行为
BOT_ACTIVE_HOURS_START=6
BOT_ACTIVE_HOURS_END=22
```

### 3. 启动机器人

使用启动脚本：

```bash
# 给予执行权限
chmod +x start_browser.sh

# 启动机器人
./start_browser.sh
```

或直接运行：

```bash
python main_browser.py
```

## ⚙️ 配置说明

### 必需配置
| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `TAILCHAT_USERNAME` | TailChat用户名 | `your_username` |
| `TAILCHAT_PASSWORD` | TailChat密码 | `your_password` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxxxxxxx` |

### 可选配置
| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `TAILCHAT_API_URL` | TailChat服务器地址 | `https://chat.mk49.cyou` |
| `TAILCHAT_HEADLESS` | 是否使用无头模式 | `true` |
| `BOT_ACTIVE_HOURS_START` | 活动开始时间(小时) | `6` |
| `BOT_ACTIVE_HOURS_END` | 活动结束时间(小时) | `22` |
| `ACTIVE_MESSAGE_USERS` | 主动消息接收用户ID | 空 |

## 🤖 机器人行为规则

### 消息处理优先级
1. **私信消息**：所有私信都会回复
2. **@消息**：群聊中@机器人的消息必须回复
3. **群聊非@消息**：忽略不回复

### 命令支持
- `!help` - 显示帮助信息
- `!status` - 查看机器人状态
- `!image [关键词]` - 搜索并发送图片
- `!summary [文本]` - 文本摘要
- `!sentiment [文本]` - 情感分析
- `!clear` - 清除对话历史

### 在线时间
- **活动时间**：6:00 - 22:00 (UTC+8)
- **非活动时间**：收到消息回复"休息中"提示
- **时间可配置**：通过环境变量调整

## 🛠️ 技术架构

### 核心模块
```
tailchat-ai-bot/
├── browser_client.py      # 浏览器自动化客户端
├── main_browser.py        # 主程序（浏览器版本）
├── config.py              # 配置管理
├── deepseek_client.py     # DeepSeek API客户端
├── message_processor.py   # 消息处理器
├── active_sender.py       # 主动消息发送器
├── rich_media.py          # 富媒体支持
└── git_image_support.py   # Git仓库图片支持
```

### 浏览器自动化流程
1. **初始化浏览器**：启动Chromium，设置反检测
2. **模拟登录**：输入用户名密码，模拟人类操作
3. **消息监听**：定期检查新消息
4. **智能回复**：调用DeepSeek API生成回复
5. **消息发送**：模拟人类输入和发送

## 🚢 部署方式

### 本地运行
```bash
./start_browser.sh
```

### GitHub Actions（推荐）
1. 上传项目到GitHub仓库
2. 在仓库设置中配置Secrets：
   - `TAILCHAT_USERNAME`
   - `TAILCHAT_PASSWORD`
   - `DEEPSEEK_API_KEY`
3. 工作流会自动运行机器人

### Docker部署
```bash
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

**Q: 登录失败**
- 检查用户名密码是否正确
- 确认TailChat服务器可访问
- 检查网络连接

**Q: 浏览器无法启动**
- 安装Playwright浏览器：`python -m playwright install chromium`
- 检查系统是否有GUI（无头模式不需要）

**Q: 消息不回复**
- 检查是否在活动时间
- 查看日志文件中的错误信息
- 确认DeepSeek API密钥有效

**Q: 被检测为机器人**
- 确保使用最新版本的Playwright
- 调整`browser_client.py`中的反检测设置
- 增加操作延迟，更模拟人类行为

### 日志查看
```bash
# 查看实时日志
tail -f logs/bot_$(date +%Y-%m-%d).log

# 查看错误日志
grep -i error logs/bot_*.log
```

## 📁 项目结构

```
tailchat-ai-bot/
├── .env.example           # 环境变量示例
├── requirements.txt       # Python依赖
├── main_browser.py       # 主程序入口（浏览器版本）
├── browser_client.py     # 浏览器自动化客户端
├── config.py             # 配置管理
├── deepseek_client.py    # DeepSeek API客户端
├── message_processor.py  # 消息处理器
├── active_sender.py      # 主动消息发送器
├── rich_media.py         # 富媒体支持
├── git_image_support.py  # Git仓库图片支持
├── start_browser.sh      # 启动脚本
├── logs/                 # 日志目录
└── .github/workflows/    # GitHub Actions工作流
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如有问题，请：
1. 查看日志文件
2. 检查环境变量配置
3. 提交GitHub Issue

---

**注意**：请合理使用机器人，遵守TailChat平台规则，不要用于垃圾消息或骚扰行为。