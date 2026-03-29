# TailChat AI 机器人 - 一键启动部署指南

## 概述

本指南详细介绍了如何使用GitHub Actions一键启动TailChat AI浏览器自动化机器人。该机器人能够：
- 模拟人类操作登录您的TailChat账号
- 自动回复私信和@消息
- 使用DeepSeek API生成智能回复
- 记录对话历史，提供连贯的对话体验
- 支持多种运行模式（正常模式、24小时模式、测试模式）

## 快速开始

### 1. 准备工作

在开始之前，请确保您拥有：
- GitHub账号
- TailChat账号（用于机器人登录）
- DeepSeek API密钥（用于AI回复）

### 2. 配置GitHub Secrets

在您的GitHub仓库中，需要配置以下Secrets：

1. 进入仓库页面 → Settings → Secrets and variables → Actions
2. 点击"New repository secret"添加以下Secrets：

| Secret名称 | 说明 | 示例值 |
|------------|------|--------|
| `TAILCHAT_USERNAME` | TailChat用户名 | `your_username` |
| `TAILCHAT_PASSWORD` | TailChat密码 | `your_password` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TAILCHAT_API_URL` | TailChat网站URL（可选） | `https://chat.mk49.cyou` |

### 3. 一键启动机器人

#### 方法一：通过GitHub Actions界面启动

1. 进入仓库的"Actions"标签页
2. 在左侧选择"One-Click Browser Bot"工作流
3. 点击"Run workflow"按钮
4. 选择运行模式：
   - **normal**: 正常模式（6:00-22:00在线）
   - **24h**: 24小时模式（全天在线）
   - **test**: 测试模式（运行30分钟测试）
5. 选择是否启用详细日志
6. 点击"Run workflow"启动机器人

#### 方法二：通过脚本启动（本地测试）

```bash
# 克隆仓库
git clone https://github.com/qingshanjiluo/tailchat-bot.git
cd tailchat-bot

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
python -m playwright install chromium

# 创建.env文件（参考.env.example）
cp .env.example .env
# 编辑.env文件，填入您的配置

# 启动机器人
python main_browser.py
```

## 运行模式详解

### 正常模式 (normal)
- **在线时间**: 每天6:00-22:00
- **超时时间**: 16小时
- **适用场景**: 日常使用，节省资源

### 24小时模式 (24h)
- **在线时间**: 全天24小时
- **超时时间**: 24小时
- **适用场景**: 需要全天候服务的场景

### 测试模式 (test)
- **在线时间**: 立即开始
- **超时时间**: 30分钟
- **适用场景**: 测试配置和功能

## 机器人功能特性

### 1. 消息处理规则
- **私信**: 自动回复所有私信
- **@消息**: 自动回复所有@机器人的消息
- **群聊非@消息**: 不回复（根据用户要求）
- **命令**: 支持多种命令（!help, !status等）

### 2. AI回复能力
- 使用DeepSeek API生成智能回复
- 支持对话历史记录，提供连贯对话
- 可生成图片描述、情感分析、文本摘要等

### 3. 主动消息功能
- 定时发送问候消息
- 发送随机小贴士和趣味知识
- 可配置主动消息间隔

### 4. 对话记录
- 自动保存所有对话历史
- 支持JSON格式导出
- 可在后续对话中引用历史

## 配置说明

### 环境变量配置

在`.env`文件或GitHub Secrets中配置：

```bash
# TailChat 配置
TAILCHAT_API_URL=https://chat.mk49.cyou
TAILCHAT_USERNAME=your_username
TAILCHAT_PASSWORD=your_password
TAILCHAT_USE_BROWSER=true
TAILCHAT_HEADLESS=true  # 无头模式，适合服务器运行

# DeepSeek API 配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat

# 机器人行为配置
BOT_ACTIVE_HOURS_START=6    # 开始时间（小时）
BOT_ACTIVE_HOURS_END=22     # 结束时间（小时）
BOT_AUTO_REPLY=true         # 启用自动回复
BOT_MAX_MESSAGE_LENGTH=1000 # 最大消息长度

# 对话记录配置
ENABLE_CONVERSATION_HISTORY=true
CONVERSATION_HISTORY_PATH=./conversations
MAX_HISTORY_MESSAGES=50

# 日志配置
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/bot.log
```

### 命令列表

机器人支持以下命令：

| 命令 | 功能 | 示例 |
|------|------|------|
| `!help` | 显示帮助信息 | `!help` |
| `!status` | 查看机器人状态 | `!status` |
| `!clear` | 清除当前对话历史 | `!clear` |
| `!image [主题]` | 生成图片描述 | `!image 日落` |
| `!summary [文本]` | 文本摘要 | `!summary 这是一段很长的文本...` |
| `!sentiment [文本]` | 情感分析 | `!sentiment 我今天很开心` |

## 故障排除

### 常见问题

#### 1. 机器人无法启动
- **检查**: GitHub Secrets是否正确配置
- **检查**: TailChat用户名密码是否正确
- **检查**: DeepSeek API密钥是否有效

#### 2. 机器人无法回复消息
- **检查**: 是否在在线时间内（正常模式6:00-22:00）
- **检查**: 消息是否为私信或@消息
- **检查**: 日志中是否有错误信息

#### 3. Playwright浏览器启动失败
- **解决方案**: 确保已安装系统依赖
  ```bash
  sudo apt-get update
  sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 libatspi2.0-0 libwayland-client0
  ```

#### 4. DeepSeek API调用失败
- **检查**: API密钥是否正确
- **检查**: 网络连接是否正常
- **检查**: API调用额度是否充足

### 查看日志

机器人运行日志保存在：
- **GitHub Actions**: 工作流运行页面 → 下载Artifact
- **本地运行**: `logs/bot.log` 文件

## 高级配置

### 自定义主动消息

编辑`active_sender.py`文件，可以自定义：
- 问候消息内容和时间
- 主动消息间隔
- 消息发送目标

### 扩展功能

项目采用模块化设计，易于扩展：

1. **添加新命令**: 在`message_processor.py`中添加命令处理函数
2. **修改AI行为**: 在`deepseek_client.py`中调整系统提示词
3. **添加新消息类型**: 在`rich_media.py`中实现新的消息格式

### 性能优化

- **减少内存使用**: 设置`TAILCHAT_HEADLESS=true`
- **提高响应速度**: 调整`BOT_AUTO_REPLY_PROBABILITY`
- **节省API调用**: 设置合理的`MAX_HISTORY_MESSAGES`

## 安全注意事项

1. **保护敏感信息**: 不要将`.env`文件提交到Git仓库
2. **API密钥安全**: 定期轮换DeepSeek API密钥
3. **账号安全**: 使用专用账号运行机器人
4. **访问控制**: 限制机器人的消息发送频率

## 技术支持

如果遇到问题：

1. **查看文档**: 阅读本指南和相关文档
2. **检查日志**: 查看详细的运行日志
3. **GitHub Issues**: 在仓库中提交Issue
4. **社区支持**: 访问TailChat社区获取帮助

## 更新日志

### v1.0.0 (初始版本)
- 支持浏览器自动化登录TailChat
- 集成DeepSeek API智能回复
- 实现对话历史记录
- 创建一键启动GitHub Actions工作流
- 支持多种运行模式

---

**祝您使用愉快！🤖**

如有任何问题或建议，欢迎在GitHub仓库中提交Issue。