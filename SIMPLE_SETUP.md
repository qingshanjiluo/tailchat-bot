# TailChat AI 机器人 - 最简单设置指南

## 3步快速启动

### 第1步：配置GitHub Secrets

在GitHub仓库中设置以下Secrets：
1. 进入仓库 → Settings → Secrets and variables → Actions
2. 点击"New repository secret"添加：

| Secret名称 | 必须 | 说明 |
|------------|------|------|
| `TAILCHAT_USERNAME` | ✅ | 你的TailChat用户名 |
| `TAILCHAT_PASSWORD` | ✅ | 你的TailChat密码 |
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API密钥（从官网获取） |
| `TAILCHAT_API_URL` | ❌ | TailChat网站URL（默认：https://chat.mk49.cyou） |

### 第2步：一键启动机器人

1. 进入仓库的"Actions"标签页
2. 找到"One-Click Browser Bot"工作流
3. 点击"Run workflow"
4. 选择：
   - **运行模式**：normal（6:00-22:00在线）
   - **日志级别**：true（启用详细日志）
5. 点击"Run workflow"启动

### 第3步：使用机器人

机器人启动后：
- 在TailChat中给机器人发送私信，会自动回复
- @机器人也会自动回复
- 支持命令：`!help`、`!status`、`!clear`等

## 环境变量说明

### 必须配置的Secrets：
```bash
TAILCHAT_USERNAME=你的用户名
TAILCHAT_PASSWORD=你的密码
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 可选配置：
```bash
TAILCHAT_API_URL=https://chat.mk49.cyou  # 默认值
```

## 运行模式说明

- **normal模式**：每天6:00-22:00在线（推荐）
- **24h模式**：全天24小时在线
- **test模式**：运行30分钟测试

## 故障排除

### 如果启动失败：
1. 检查Secrets是否正确配置
2. 检查TailChat用户名密码是否正确
3. 检查DeepSeek API密钥是否有效

### 查看日志：
1. 在工作流运行页面下载"bot-logs" Artifact
2. 查看logs/bot_github_actions.log文件

## 手动启动命令（本地测试）

```bash
# 克隆仓库
git clone https://github.com/qingshanjiluo/tailchat-bot.git
cd tailchat-bot

# 安装依赖
pip install -r requirements.txt
python -m playwright install chromium

# 创建.env文件
cp .env.example .env
# 编辑.env文件填入你的配置

# 启动
python main_browser.py
```

## 注意事项

1. 机器人只回复私信和@消息
2. 群聊非@消息不会回复
3. 对话历史会自动保存
4. 机器人会模拟人类操作，避免被检测

---

**一键启动，即刻使用！** 🚀