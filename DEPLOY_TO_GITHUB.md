# 部署到 GitHub 仓库指南

本指南将帮助您将TailChat AI机器人部署到GitHub仓库：https://github.com/qingshanjiluo/tailchat-bot

## 部署前准备

### 1. 克隆目标仓库
```bash
git clone https://github.com/qingshanjiluo/tailchat-bot.git
cd tailchat-bot
```

### 2. 复制项目文件
将本项目的所有文件复制到目标仓库：
```bash
# 假设tailchat-ai-bot在上级目录
cp -r ../tailchat-ai-bot/* .
cp -r ../tailchat-ai-bot/.github .  # 复制GitHub Actions工作流
cp ../tailchat-ai-bot/.env.example .env.example
```

### 3. 清理不需要的文件
```bash
# 删除可能不需要的文件
rm -rf __pycache__ *.pyc
```

## 环境配置

### 必需的环境变量
创建 `.env` 文件并配置以下变量：

```env
# ========== TailChat 配置 ==========
# TailChat服务器地址（您的TailChat实例）
TAILCHAT_API_URL=https://chat.mk49.cyou

# OpenAPI应用ID和密钥（从TailChat管理后台获取）
TAILCHAT_APP_ID=your_app_id_here
TAILCHAT_APP_SECRET=your_app_secret_here

# 机器人显示名称
TAILCHAT_BOT_USERNAME=AI助手

# ========== DeepSeek 配置 ==========
# DeepSeek API密钥（从DeepSeek平台获取）
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# API地址和模型
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
DEEPSEEK_MODEL=deepseek-chat

# ========== 机器人行为配置 ==========
# 在线时间（北京时间6:00-22:00）
BOT_ACTIVE_HOURS_START=6
BOT_ACTIVE_HOURS_END=22

# 消息行为配置
BOT_AUTO_REPLY=true
BOT_AUTO_REPLY_PROBABILITY=1.0  # 私信100%回复
BOT_MAX_MESSAGE_LENGTH=1000

# 消息模板
WELCOME_MESSAGE=你好！我是AI助手，有什么可以帮你的吗？
BUSY_MESSAGE=我现在不在线，请在6:00-22:00之间联系我。

# ========== 主动消息配置 ==========
# 主动发送消息给以下用户ID（逗号分隔）
ACTIVE_MESSAGE_USERS=user_id_1,user_id_2

# 主动消息发送间隔（分钟）
ACTIVE_MESSAGE_INTERVAL=60
```

## TailChat OpenAPI 配置步骤

### 1. 获取App ID和App Secret
1. 登录您的TailChat管理后台（如 https://chat.mk49.cyou）
2. 进入"开放平台" → "应用管理"
3. 点击"创建应用"
4. 填写应用信息：
   - 应用名称: AI助手
   - 回调地址: 留空或填写 `https://chat.mk49.cyou`
   - 权限: 必须勾选以下权限：
     - 发送消息
     - 读取消息
     - 管理好友
     - 获取用户信息
5. 创建后复制App ID和App Secret

### 2. 测试OpenAPI连接
```bash
# 测试登录
curl -X POST "https://chat.mk49.cyou/api/openapi/bot/login" \
  -H "Content-Type: application/json" \
  -d '{"appId": "YOUR_APP_ID", "appSecret": "YOUR_APP_SECRET"}'
```

## GitHub Actions 部署配置

### 1. 设置GitHub Secrets
在GitHub仓库设置中配置以下Secrets：
1. 进入仓库 Settings → Secrets and variables → Actions
2. 点击"New repository secret"
3. 添加以下Secrets：

| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `TAILCHAT_APP_ID` | 您的App ID | TailChat OpenAPI应用ID |
| `TAILCHAT_APP_SECRET` | 您的App Secret | TailChat OpenAPI应用密钥 |
| `DEEPSEEK_API_KEY` | 您的API密钥 | DeepSeek API密钥 |
| `TAILCHAT_API_URL` | https://chat.mk49.cyou | TailChat服务器地址 |

### 2. 配置工作流文件
修改 `.github/workflows/run-bot.yml`：

```yaml
name: Run TailChat AI Bot

on:
  workflow_dispatch:  # 手动触发
  schedule:
    # 每天UTC时间22点运行（北京时间6点）
    - cron: '0 22 * * *'

jobs:
  run-bot:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Create environment file
      run: |
        cat > .env << EOF
        TAILCHAT_API_URL=${{ secrets.TAILCHAT_API_URL || 'https://chat.mk49.cyou' }}
        TAILCHAT_APP_ID=${{ secrets.TAILCHAT_APP_ID }}
        TAILCHAT_APP_SECRET=${{ secrets.TAILCHAT_APP_SECRET }}
        TAILCHAT_BOT_USERNAME=AI助手
        DEEPSEEK_API_KEY=${{ secrets.DEEPSEEK_API_KEY }}
        DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
        DEEPSEEK_MODEL=deepseek-chat
        BOT_ACTIVE_HOURS_START=6
        BOT_ACTIVE_HOURS_END=22
        BOT_AUTO_REPLY=true
        BOT_AUTO_REPLY_PROBABILITY=1.0
        BOT_MAX_MESSAGE_LENGTH=1000
        WELCOME_MESSAGE=你好！我是AI助手，有什么可以帮你的吗？
        BUSY_MESSAGE=我现在不在线，请在6:00-22:00之间联系我。
        EOF
        
    - name: Run the bot
      run: |
        python main.py
```

## 机器人行为说明

### 消息处理规则
根据您的要求，机器人遵循以下规则：

1. **私信处理** ✅
   - 只回复私信消息
   - 100%回复率（可配置）
   - 使用DeepSeek AI生成智能回复

2. **@消息处理** ✅
   - @机器人的消息必须回复
   - 即使在非在线时间也会回复忙碌消息
   - 支持在群聊中@机器人

3. **群聊消息** ❌
   - 不回复群聊中的非@消息
   - 只记录日志，不进行任何回复

4. **命令系统** ✅
   - 支持!help、!status、!clear等命令
   - 命令在任何情况下都处理

5. **主动消息** ✅
   - 可以主动发送消息给指定用户
   - 支持定时发送问候、提示等
   - 只在私信中发送主动消息

### 在线时间控制
- 默认在线时间：北京时间6:00-22:00
- 非在线时间收到@消息会回复忙碌消息
- 可配置24小时在线

## 测试部署

### 1. 本地测试
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件填写实际配置

# 测试运行
python test_bot.py

# 启动机器人
python main.py
```

### 2. GitHub Actions测试
1. 推送代码到GitHub
2. 进入仓库的"Actions"标签页
3. 手动运行"Run TailChat AI Bot"工作流
4. 查看日志确认运行状态

## 故障排除

### 常见问题

#### 1. 连接TailChat失败
**症状**: `登录失败` 或 `WebSocket连接失败`
**解决方案**:
- 检查TAILCHAT_API_URL是否正确
- 确认App ID和App Secret有效
- 确保TailChat服务器OpenAPI已启用

#### 2. DeepSeek API调用失败
**症状**: `DeepSeek API调用失败`
**解决方案**:
- 检查DEEPSEEK_API_KEY是否正确
- 确认API密钥有足够的额度
- 测试网络连接

#### 3. 机器人不回复消息
**症状**: 收到消息但没有回复
**解决方案**:
- 检查是否在在线时间内
- 查看日志确认消息处理逻辑
- 确认机器人有发送消息的权限

#### 4. GitHub Actions运行失败
**症状**: 工作流运行失败
**解决方案**:
- 检查GitHub Secrets配置
- 查看工作流日志中的错误信息
- 确认Python版本和依赖安装正常

### 日志查看
```bash
# 本地运行查看日志
python main.py 2>&1 | tee bot.log

# GitHub Actions查看日志
# 1. 进入仓库Actions页面
# 2. 点击具体的工作流运行
# 3. 查看"Run the bot"步骤的日志
```

## 高级配置

### 自定义回复行为
修改 `message_processor.py` 中的 `process_message` 方法：

```python
def process_message(self, message: Message):
    """自定义消息处理逻辑"""
    # 您的自定义逻辑
```

### 添加新命令
在 `message_processor.py` 中添加新的命令处理器：

```python
# 1. 在command_handlers中添加
self.command_handlers = {
    # ... 现有命令
    "newcommand": self._handle_new_command,
}

# 2. 实现命令处理器
def _handle_new_command(self, message: Message, args: str):
    """处理新命令"""
    reply = "这是新命令的回复"
    self.tailchat.send_message(message.converse_id, reply)
```

### 配置主动消息接收者
在 `.env` 中配置主动消息接收者：

```env
# 主动消息接收用户ID（逗号分隔）
ACTIVE_MESSAGE_USERS=user_id_1,user_id_2,user_id_3

# 主动消息发送间隔（分钟）
ACTIVE_MESSAGE_INTERVAL=30
```

## 监控和维护

### 1. 状态监控
- 定期检查GitHub Actions运行状态
- 查看机器人日志文件
- 监控DeepSeek API使用情况

### 2. 定期更新
- 更新Python依赖：`pip install -r requirements.txt --upgrade`
- 检查TailChat API变更
- 更新DeepSeek API配置

### 3. 备份配置
- 备份 `.env` 文件
- 备份GitHub Secrets
- 定期导出对话历史（如果需要）

## 支持与帮助

### 获取帮助
1. **查看文档**: 阅读 `README.md` 和 `QUICKSTART.md`
2. **测试功能**: 运行 `python test_bot.py`
3. **查看日志**: 分析日志文件中的错误信息
4. **社区支持**: 在GitHub Issues中提问

### 报告问题
在GitHub仓库中创建Issue，包含以下信息：
1. 问题描述
2. 复现步骤
3. 错误日志
4. 环境信息

---

**部署完成！** 🎉

现在您的TailChat AI机器人已经配置完成，可以：
- 自动回复私信消息
- 必须回复@消息
- 主动发送消息
- 在GitHub Actions中自动运行

开始享受智能聊天的乐趣吧！ 🤖💬