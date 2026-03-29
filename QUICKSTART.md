# TailChat AI Bot 快速开始指南

## 5分钟快速部署

### 步骤1: 环境准备
```bash
# 克隆项目（如果已下载可跳过）
git clone <repository-url>
cd tailchat-ai-bot

# 确保已安装Python 3.8+
python --version
```

### 步骤2: 基础配置
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件
# 使用文本编辑器打开.env文件，填写以下必要配置:
# 1. TAILCHAT_APP_ID 和 TAILCHAT_APP_SECRET (从TailChat管理后台获取)
# 2. DEEPSEEK_API_KEY (从DeepSeek平台获取)
```

### 步骤3: 安装依赖
```bash
# 使用pip安装
pip install -r requirements.txt

# 或者使用启动脚本（会自动检查依赖）
chmod +x start.sh
./start.sh
```

### 步骤4: 测试运行
```bash
# 运行测试脚本检查配置
python test_bot.py

# 如果测试通过，启动机器人
python main.py
```

## TailChat OpenAPI 配置指南

### 1. 获取App ID和App Secret
1. 登录TailChat管理后台
2. 进入"开放平台" -> "应用管理"
3. 点击"创建应用"
4. 填写应用信息：
   - 应用名称: AI助手
   - 回调地址: 留空或填写 `http://localhost:11000`
   - 权限: 勾选"发送消息"、"读取消息"、"管理好友"
5. 创建后获取App ID和App Secret

### 2. 验证配置
在`.env`文件中配置：
```env
TAILCHAT_API_URL=http://你的tailchat服务器地址:11000
TAILCHAT_APP_ID=你的App ID
TAILCHAT_APP_SECRET=你的App Secret
```

## DeepSeek API 配置指南

### 1. 获取API密钥
1. 访问 [DeepSeek平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入API密钥管理页面
4. 创建新的API密钥

### 2. 配置API密钥
在`.env`文件中配置：
```env
DEEPSEEK_API_KEY=你的API密钥
```

## 基本使用

### 启动机器人
```bash
# 方法1: 直接运行
python main.py

# 方法2: 使用启动脚本
./start.sh

# 方法3: Docker运行
docker-compose up -d
```

### 与机器人互动
在TailChat中：
1. **@机器人对话**: 在群聊中@机器人并发送消息
2. **私信聊天**: 添加机器人为好友并发送私信
3. **使用命令**: 
   - `!help` - 显示帮助
   - `!status` - 查看状态
   - `!image 主题` - 生成图片描述
   - `!clear` - 清除对话历史

### 查看日志
```bash
# 查看实时日志
tail -f logs/bot_*.log

# 查看错误日志
grep ERROR logs/bot_*.log
```

## 常见问题

### Q1: 连接TailChat失败
**可能原因**:
- TailChat服务器地址错误
- App ID或App Secret错误
- TailChat OpenAPI未启用

**解决方案**:
1. 检查TAILCHAT_API_URL是否正确
2. 确认App ID和App Secret来自正确的应用
3. 联系TailChat管理员确认OpenAPI已启用

### Q2: DeepSeek API调用失败
**可能原因**:
- API密钥错误或过期
- API额度不足
- 网络连接问题

**解决方案**:
1. 在DeepSeek平台验证API密钥
2. 检查API使用额度
3. 测试网络连接: `curl https://api.deepseek.com`

### Q3: 机器人不回复消息
**可能原因**:
- 不在在线时间内（默认6:00-22:00）
- 自动回复被关闭
- WebSocket连接断开

**解决方案**:
1. 检查当前时间是否在配置的在线时间内
2. 确认BOT_AUTO_REPLY设置为true
3. 查看日志中的连接状态

## 高级配置

### 修改在线时间
编辑`.env`文件：
```env
# 设置为24小时在线
BOT_ACTIVE_HOURS_START=0
BOT_ACTIVE_HOURS_END=23

# 或设置为特定时间
BOT_ACTIVE_HOURS_START=9
BOT_ACTIVE_HOURS_END=18
```

### 配置Git图片支持
1. 准备一个Git仓库存放图片
2. 在`.env`中配置：
```env
GIT_REPO_URL=https://github.com/你的用户名/你的仓库.git
GIT_REPO_BRANCH=main
GIT_IMAGE_PATH=images/  # 图片存放目录
```

### 自定义消息模板
编辑`active_sender.py`文件，修改以下变量：
- `greeting_templates`: 问候消息模板
- `tip_templates`: 提示消息模板  
- `fun_fact_templates`: 趣味知识模板

## 生产环境部署

### 使用Docker部署
```bash
# 构建镜像
docker build -t tailchat-ai-bot .

# 运行容器
docker run -d \
  --name tailchat-ai-bot \
  --restart unless-stopped \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  tailchat-ai-bot
```

### 使用Docker Compose
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 系统服务部署（Linux）
```bash
# 创建系统服务
sudo cp tailchat-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tailchat-bot
sudo systemctl start tailchat-bot

# 查看服务状态
sudo systemctl status tailchat-bot
```

## 获取帮助

- **文档**: 查看 [README.md](README.md) 获取完整文档
- **测试**: 运行 `python test_bot.py` 进行功能测试
- **日志**: 查看 `logs/` 目录下的日志文件
- **问题**: 查看日志中的错误信息进行排查

---

**开始使用吧！** 🚀

如果遇到问题，请参考完整文档或查看日志文件中的详细错误信息。