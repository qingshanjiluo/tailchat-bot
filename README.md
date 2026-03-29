# TailChat AI 机器人 🤖

一个基于Python的TailChat AI机器人，集成DeepSeek API，支持自动回复、主动消息发送、富媒体消息和Git仓库图片支持。

## 功能特性 ✨

### 核心功能
- 🤖 **AI对话**: 集成DeepSeek API，智能回复用户消息
- ⏰ **在线时间控制**: 可配置在线时间（默认6:00-22:00）
- 🔄 **自动回复**: 支持@回复、私信回复和随机自动回复
- 🎯 **主动消息**: 定时发送问候、提示、趣味知识等
- 📱 **富媒体支持**: 表情、图片、网址、文件等

### 高级功能
- 🖼️ **Git图片支持**: 从Git仓库获取和发送图片
- 🎨 **图片生成**: 通过AI生成图片描述
- 📝 **文本摘要**: 自动摘要长文本
- 😊 **情感分析**: 分析文本情感倾向
- 💬 **对话历史**: 维护对话上下文

### 管理功能
- ⚙️ **命令系统**: 支持!help、!status、!clear等命令
- 📊 **状态监控**: 实时监控机器人状态
- 🔧 **配置管理**: 通过环境变量灵活配置
- 📋 **日志记录**: 详细的运行日志

## 快速开始 🚀

### 环境要求
- Python 3.8+
- TailChat服务器（已启用OpenAPI）
- DeepSeek API密钥

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd tailchat-ai-bot
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，填写你的配置
```

4. **运行机器人**
```bash
python main.py
```

## 配置说明 ⚙️

### 环境变量配置

复制`.env.example`为`.env`并修改以下配置：

#### TailChat 配置
```env
# TailChat服务器地址
TAILCHAT_API_URL=http://localhost:11000

# OpenAPI应用ID和密钥（在TailChat管理后台创建）
TAILCHAT_APP_ID=your_app_id
TAILCHAT_APP_SECRET=your_app_secret

# 机器人显示名称和头像
TAILCHAT_BOT_USERNAME=AI助手
TAILCHAT_BOT_AVATAR=https://example.com/avatar.png
```

#### DeepSeek 配置
```env
# DeepSeek API密钥（从DeepSeek平台获取）
DEEPSEEK_API_KEY=your_deepseek_api_key

# API地址和模型
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat
```

#### 机器人行为配置
```env
# 在线时间（24小时制）
BOT_ACTIVE_HOURS_START=6
BOT_ACTIVE_HOURS_END=22

# 自动回复设置
BOT_AUTO_REPLY=true
BOT_AUTO_REPLY_PROBABILITY=0.8
BOT_MAX_MESSAGE_LENGTH=1000

# 消息模板
WELCOME_MESSAGE=你好！我是AI助手，有什么可以帮你的吗？
BUSY_MESSAGE=我现在不在线，请在6:00-22:00之间联系我。
```

#### Git仓库配置（可选）
```env
# Git仓库配置（用于发送图片）
GIT_REPO_URL=https://github.com/username/repo.git
GIT_REPO_BRANCH=main
GIT_IMAGE_PATH=images/
```

### TailChat OpenAPI配置

1. 登录TailChat管理后台
2. 进入"开放平台" -> "应用管理"
3. 创建新应用，获取App ID和App Secret
4. 确保应用有发送消息的权限

## 使用指南 📖

### 基本使用

1. **启动机器人**
```bash
python main.py
```

2. **在TailChat中与机器人互动**
   - @机器人进行对话
   - 发送私信给机器人
   - 使用命令控制机器人

### 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `!help` | 显示帮助信息 | `!help` |
| `!status` | 查看机器人状态 | `!status` |
| `!clear` | 清除对话历史 | `!clear` |
| `!image <主题>` | 生成图片描述 | `!image 日落` |
| `!summary <文本>` | 文本摘要 | `!summary 这是一段很长的文本...` |
| `!sentiment <文本>` | 情感分析 | `!sentiment 我今天很开心` |

### 主动消息功能

机器人会自动发送以下类型的消息：
- **定时问候**: 早上8点、中午12点、晚上8点
- **小提示**: 每小时随机发送使用提示
- **趣味知识**: 每2小时发送有趣的知识
- **周报提醒**: 每周一早上9点

## 项目结构 📁

```
tailchat-ai-bot/
├── main.py              # 主程序入口
├── config.py            # 配置管理
├── requirements.txt     # 依赖列表
├── .env.example         # 环境变量示例
├── README.md           # 本文档
│
├── tailchat_client.py   # TailChat客户端
├── deepseek_client.py   # DeepSeek API客户端
├── message_processor.py # 消息处理器
├── active_sender.py     # 主动消息发送器
├── rich_media.py        # 富媒体支持
└── git_image_support.py # Git图片支持
```

## 模块说明 🔧

### 1. TailChat客户端 (`tailchat_client.py`)
- WebSocket连接管理
- 消息收发处理
- 用户认证和会话管理

### 2. DeepSeek客户端 (`deepseek_client.py`)
- DeepSeek API集成
- 对话历史管理
- 文本处理功能（摘要、情感分析等）

### 3. 消息处理器 (`message_processor.py`)
- 消息分类处理
- 命令解析和执行
- AI决策和回复生成

### 4. 主动消息发送器 (`active_sender.py`)
- 定时任务调度
- 主动消息生成和发送
- 消息模板管理

### 5. 富媒体支持 (`rich_media.py`)
- 表情符号处理
- 图片URL生成
- 媒体内容分析

### 6. Git图片支持 (`git_image_support.py`)
- Git仓库连接
- 图片URL生成
- 图片搜索和发送

## 部署方式 🚢

### 本地运行
```bash
# 直接运行
python main.py

# 使用nohup后台运行
nohup python main.py > bot.log 2>&1 &
```

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### 系统服务（Systemd）
创建服务文件 `/etc/systemd/system/tailchat-bot.service`:
```ini
[Unit]
Description=TailChat AI Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/tailchat-ai-bot
EnvironmentFile=/opt/tailchat-ai-bot/.env
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tailchat-bot
sudo systemctl start tailchat-bot
```

## 故障排除 🔧

### 常见问题

1. **连接失败**
   - 检查TailChat服务器地址
   - 验证App ID和App Secret
   - 确保TailChat OpenAPI已启用

2. **DeepSeek API错误**
   - 检查API密钥是否正确
   - 确认API密钥有足够的额度
   - 检查网络连接

3. **消息发送失败**
   - 检查WebSocket连接状态
   - 验证机器人权限
   - 查看日志文件

### 日志查看
```bash
# 查看实时日志
tail -f logs/bot_*.log

# 查看错误日志
grep ERROR logs/bot_*.log
```

## 高级配置 🛠️

### 自定义消息模板
修改`active_sender.py`中的消息模板：
```python
self.greeting_templates = [
    "自定义问候消息 {username}!",
    # 添加更多模板...
]
```

### 扩展命令系统
在`message_processor.py`中添加新的命令处理器：
```python
self.command_handlers = {
    # 现有命令...
    "newcommand": self._handle_new_command,
}
```

### 集成其他AI服务
修改`deepseek_client.py`以支持其他AI服务：
```python
# 替换为其他AI服务的API调用
response = other_ai_client.chat(messages=messages)
```

## 安全注意事项 ⚠️

1. **API密钥保护**
   - 不要将`.env`文件提交到版本控制
   - 使用环境变量或密钥管理服务
   - 定期轮换API密钥

2. **权限控制**
   - 为机器人分配最小必要权限
   - 限制可访问的群组和用户
   - 监控机器人的消息发送频率

3. **数据隐私**
   - 对话历史仅保存在内存中
   - 可配置对话历史保留时间
   - 支持清除对话历史命令

## 贡献指南 🤝

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证 📄

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。

## 联系方式 📞

- 问题反馈: [GitHub Issues](https://github.com/yourusername/tailchat-ai-bot/issues)
- 功能建议: [GitHub Discussions](https://github.com/yourusername/tailchat-ai-bot/discussions)

---

**快乐聊天！** 🎉