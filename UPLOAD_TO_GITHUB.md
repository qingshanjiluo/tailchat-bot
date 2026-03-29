# 上传到 GitHub 仓库指南

本指南将帮助您将TailChat AI机器人项目上传到GitHub仓库：https://github.com/qingshanjiluo/tailchat-bot

## 方法一：使用Git命令行（推荐）

### 步骤1: 克隆目标仓库
```bash
# 克隆您的GitHub仓库
git clone https://github.com/qingshanjiluo/tailchat-bot.git
cd tailchat-bot
```

### 步骤2: 复制项目文件
```bash
# 假设tailchat-ai-bot在上级目录
# 复制所有文件（排除.git目录）
cp -r ../tailchat-ai-bot/* .
cp -r ../tailchat-ai-bot/.github .

# 复制隐藏文件
cp ../tailchat-ai-bot/.env.example .
cp ../tailchat-ai-bot/.gitignore . 2>/dev/null || true
```

### 步骤3: 清理不需要的文件
```bash
# 删除Python缓存文件
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
```

### 步骤4: 创建.gitignore文件（如果不存在）
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
/tmp/
*.tmp
*.temp

# Test coverage
.coverage
htmlcov/
.pytest_cache/
EOF
```

### 步骤5: 提交并推送代码
```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "添加TailChat AI机器人

功能特性：
- 集成DeepSeek API智能对话
- 支持私信和@消息回复
- 主动消息发送功能
- 在线时间控制（6:00-22:00）
- GitHub Actions自动运行
- 完整的配置和文档"

# 推送到GitHub
git push origin main
```

## 方法二：使用部署脚本

### 运行自动部署脚本
```bash
# 进入项目目录
cd tailchat-ai-bot

# 给脚本执行权限（Linux/Mac）
chmod +x deploy_to_github.sh

# 运行部署脚本
./deploy_to_github.sh
```

### 脚本将执行以下操作：
1. 克隆目标仓库
2. 复制所有项目文件
3. 创建配置文件
4. 测试配置
5. 指导配置GitHub Secrets
6. 提交和推送代码

## 方法三：手动上传文件

### 通过GitHub网页界面上传
1. 访问 https://github.com/qingshanjiluo/tailchat-bot
2. 点击"Add file" → "Upload files"
3. 选择tailchat-ai-bot目录中的所有文件
4. 提交更改

### 需要上传的文件列表：
```
必需文件：
- main.py                    # 主程序
- config.py                  # 配置管理
- tailchat_client.py         # TailChat客户端
- deepseek_client.py         # DeepSeek API客户端
- message_processor.py       # 消息处理器
- active_sender.py           # 主动消息发送器
- requirements.txt           # Python依赖

配置文件：
- .env.example               # 环境变量示例
- .gitignore                # Git忽略文件

文档文件：
- README.md                  # 项目文档
- QUICKSTART.md              # 快速开始指南
- DEPLOY_TO_GITHUB.md        # 部署指南
- GITHUB_ACTIONS.md          # GitHub Actions说明

工具脚本：
- deploy_to_github.sh        # 部署脚本
- start.sh                   # 启动脚本
- test_bot.py                # 测试脚本

GitHub Actions：
- .github/workflows/run-bot.yml          # 运行机器人工作流
- .github/workflows/simple-visit.yml     # 简单访问工作流
- .github/workflows/auto-visit-tailchat.yml # 自动化工作流

可选文件：
- Dockerfile                 # Docker配置
- docker-compose.yml         # Docker Compose配置
- rich_media.py              # 富媒体支持
- git_image_support.py       # Git图片支持
```

## 配置GitHub Secrets

上传代码后，必须在GitHub仓库中配置以下Secrets：

### 步骤1: 访问Secrets设置
1. 进入仓库：https://github.com/qingshanjiluo/tailchat-bot
2. 点击"Settings" → "Secrets and variables" → "Actions"
3. 点击"New repository secret"

### 步骤2: 添加必需Secrets
| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `TAILCHAT_APP_ID` | 您的App ID | 从TailChat管理后台获取 |
| `TAILCHAT_APP_SECRET` | 您的App Secret | 从TailChat管理后台获取 |
| `DEEPSEEK_API_KEY` | 您的API密钥 | 从DeepSeek平台获取 |
| `TAILCHAT_API_URL` | https://chat.mk49.cyou | TailChat服务器地址 |

### 步骤3: 可选Secrets
| Secret名称 | 值 | 说明 |
|-----------|-----|------|
| `ACTIVE_MESSAGE_USERS` | user_id1,user_id2 | 主动消息接收用户ID |
| `BOT_ACTIVE_HOURS_START` | 6 | 在线开始时间（0-23） |
| `BOT_ACTIVE_HOURS_END` | 22 | 在线结束时间（0-23） |

## 验证上传

### 检查上传的文件
```bash
# 在本地仓库目录中
ls -la

# 应该看到以下主要文件：
# - main.py
# - config.py
# - requirements.txt
# - .github/workflows/run-bot.yml
# - README.md
```

### 检查Git状态
```bash
git status
# 应该显示"nothing to commit, working tree clean"
```

### 查看GitHub仓库
1. 访问 https://github.com/qingshanjiluo/tailchat-bot
2. 确认所有文件已上传
3. 检查文件内容是否正确

## 首次运行测试

### 手动触发GitHub Actions
1. 进入仓库的"Actions"标签页
2. 找到"Run TailChat AI Bot"工作流
3. 点击"Run workflow"
4. 选择运行时长（默认60分钟）
5. 点击"Run workflow"按钮

### 监控运行状态
1. 点击运行中的工作流
2. 查看各个步骤的日志
3. 检查是否有错误
4. 下载Artifacts查看详细日志

### 预期结果
- ✅ 所有步骤显示绿色对勾
- ✅ "Run the bot"步骤运行成功
- ✅ 生成日志文件Artifact
- ✅ 机器人成功连接到TailChat

## 故障排除

### 常见问题

#### 1. 上传文件失败
**错误**: `Permission denied` 或 `Authentication failed`
**解决**:
```bash
# 检查Git配置
git config --list

# 设置Git用户信息
git config --global user.name "您的用户名"
git config --global user.email "您的邮箱"

# 使用HTTPS代替SSH
git remote set-url origin https://github.com/qingshanjiluo/tailchat-bot.git
```

#### 2. GitHub Actions运行失败
**错误**: `Secrets not found` 或 `Invalid configuration`
**解决**:
1. 确认已配置所有必需Secrets
2. 检查Secret名称是否正确
3. 确认Secret值没有多余空格

#### 3. 机器人连接失败
**错误**: `Login failed` 或 `WebSocket connection failed`
**解决**:
1. 检查TAILCHAT_API_URL是否正确
2. 确认App ID和App Secret有效
3. 验证TailChat服务器可访问

#### 4. Python依赖安装失败
**错误**: `pip install failed`
**解决**:
```bash
# 在本地测试依赖安装
pip install -r requirements.txt

# 如果特定包失败，尝试单独安装
pip install playwright requests openai python-dotenv
```

## 后续步骤

### 1. 配置TailChat OpenAPI
1. 登录TailChat管理后台
2. 创建OpenAPI应用
3. 获取App ID和App Secret
4. 配置到GitHub Secrets

### 2. 获取DeepSeek API密钥
1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 创建API密钥
4. 配置到GitHub Secrets

### 3. 测试机器人功能
1. 在TailChat中发送私信给机器人
2. 在群聊中@机器人
3. 使用!help命令
4. 验证回复是否正常

### 4. 监控和维护
1. 定期检查GitHub Actions运行状态
2. 查看机器人日志
3. 更新依赖和配置
4. 备份重要数据

## 获取帮助

### 文档资源
- `README.md` - 完整项目文档
- `QUICKSTART.md` - 5分钟快速开始
- `DEPLOY_TO_GITHUB.md` - 部署指南（本文档）
- `GITHUB_ACTIONS.md` - GitHub Actions详细说明

### 测试工具
```bash
# 本地测试配置
python test_bot.py

# 本地运行机器人
python main.py
```

### 问题反馈
如果在部署过程中遇到问题：
1. 查看相关文档
2. 运行测试脚本诊断
3. 检查错误日志
4. 验证配置信息

---

**上传完成！** 🎉

现在您的TailChat AI机器人已经成功部署到GitHub仓库。接下来：
1. 配置GitHub Secrets
2. 手动触发工作流测试
3. 在TailChat中测试机器人功能
4. 享受智能聊天的乐趣！

祝您部署顺利！ 🤖🚀