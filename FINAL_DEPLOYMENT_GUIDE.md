# TailChat AI机器人 - 最终部署指南

## 项目概述

已成功创建完整的TailChat AI机器人项目，包含以下功能：

✅ **核心功能**
- 自动回复私信消息
- @消息必须回复
- 支持主动发送消息
- 集成DeepSeek API
- 富媒体消息支持（表情、图片、网址）
- Git仓库图片支持
- 在线时间控制（6:00-22:00）

✅ **技术架构**
- Python 3.8+ 环境
- TailChat OpenAPI + WebSocket
- DeepSeek API（兼容OpenAI格式）
- Playwright浏览器自动化
- GitHub Actions CI/CD

## 文件准备完成

项目已打包为压缩文件：`tailchat-ai-bot.zip` (63.5KB)

包含以下文件：
```
tailchat-ai-bot/
├── .env.example                    # 环境变量示例
├── .github/workflows/              # GitHub Actions工作流
│   ├── auto-visit-tailchat.yml     # 自动访问TailChat
│   ├── run-bot.yml                 # 运行机器人主工作流
│   └── simple-visit.yml            # 简单访问测试
├── config.py                       # 配置管理
├── tailchat_client.py              # TailChat客户端
├── deepseek_client.py              # DeepSeek API客户端
├── message_processor.py            # 消息处理器（只回复私信，@必须回复）
├── active_sender.py                # 主动消息发送器
├── rich_media.py                   # 富媒体支持
├── git_image_support.py            # Git仓库图片支持
├── main.py                         # 主程序入口
├── requirements.txt                # Python依赖
├── README.md                       # 完整文档
├── QUICKSTART.md                   # 快速开始指南
├── DEPLOY_TO_GITHUB.md             # GitHub部署指南
├── GITHUB_ACTIONS.md               # GitHub Actions配置指南
├── UPLOAD_TO_GITHUB.md             # 上传到GitHub指南
├── Dockerfile                      # Docker容器配置
├── docker-compose.yml              # Docker Compose配置
├── start.sh                        # 启动脚本
└── test_bot.py                     # 测试脚本
```

## 手动上传到GitHub步骤

由于网络连接问题，请按以下步骤手动上传：

### 方法一：通过GitHub网页界面上传（推荐）

1. **访问目标仓库**
   - 打开 https://github.com/qingshanjiluo/tailchat-bot
   - 点击 "Add file" → "Upload files"

2. **上传压缩包内容**
   - 解压 `tailchat-ai-bot.zip`
   - 将所有文件拖拽到GitHub上传界面
   - 确保包含 `.github/workflows/` 目录

3. **提交更改**
   - 提交信息：`添加TailChat AI机器人`
   - 描述：`添加完整的AI机器人，支持私信自动回复、DeepSeek API集成、主动消息发送等功能`

### 方法二：使用Git命令行

如果您有Git访问权限：

```bash
# 1. 克隆仓库
git clone https://github.com/qingshanjiluo/tailchat-bot.git
cd tailchat-bot

# 2. 复制项目文件
# 解压 tailchat-ai-bot.zip 到当前目录
# 或从 temp-deploy 目录复制

# 3. 提交并推送
git add .
git commit -m "添加TailChat AI机器人"
git push origin main
```

## GitHub Secrets配置

上传代码后，**必须**在GitHub仓库中配置以下Secrets：

### 必需配置
1. **TAILCHAT_APP_ID** - TailChat OpenAPI应用ID
2. **TAILCHAT_APP_SECRET** - TailChat OpenAPI应用密钥
3. **DEEPSEEK_API_KEY** - DeepSeek API密钥

### 配置步骤
1. 访问：https://github.com/qingshanjiluo/tailchat-bot/settings/secrets/actions
2. 点击 "New repository secret"
3. 添加上述三个Secrets

### 可选配置
- **TAILCHAT_API_URL** - TailChat服务器地址（默认：https://chat.mk49.cyou）
- **ACTIVE_MESSAGE_USERS** - 主动消息接收用户ID（逗号分隔）

## 测试和验证

### 1. 手动触发工作流
1. 访问：https://github.com/qingshanjiluo/tailchat-bot/actions
2. 点击 "Run TailChat AI Bot" 工作流
3. 点击 "Run workflow" 按钮

### 2. 监控运行状态
- 在工作流运行页面查看实时日志
- 检查机器人是否成功连接TailChat
- 验证DeepSeek API调用是否正常

### 3. 功能测试
在TailChat中测试以下功能：

**私信测试**
1. 发送私信给机器人
2. 机器人应自动回复
3. 测试表情、图片、网址消息

**@消息测试**
1. 在群聊中@机器人
2. 机器人必须回复
3. 测试命令：!help, !status, !image等

**主动消息测试**
1. 机器人应在指定时间发送问候消息
2. 测试主动发送的富媒体消息

## 故障排除

### 常见问题

1. **GitHub Actions失败**
   - 检查Secrets配置是否正确
   - 查看工作流日志中的错误信息
   - 确保Python依赖安装成功

2. **机器人无法连接TailChat**
   - 验证TAILCHAT_APP_ID和TAILCHAT_APP_SECRET
   - 检查网络连接
   - 确认TailChat服务器可访问

3. **DeepSeek API调用失败**
   - 验证DEEPSEEK_API_KEY
   - 检查API配额和限制
   - 查看错误日志中的API响应

4. **消息处理异常**
   - 检查message_processor.py中的逻辑
   - 验证只回复私信和@消息的规则
   - 查看处理日志

### 调试方法
1. 启用详细日志：在.env中设置 `LOG_LEVEL=DEBUG`
2. 查看GitHub Actions完整日志
3. 使用test_bot.py进行本地测试

## 机器人行为说明

### 消息处理规则
- ✅ **回复私信**：所有私信消息都会回复
- ✅ **回复@消息**：群聊中@机器人的消息必须回复
- ❌ **忽略群聊非@消息**：群聊中未@机器人的消息不回复
- ✅ **主动发送消息**：可以定时发送问候、提示等消息

### 在线时间
- **活动时间**：每天 6:00 - 22:00
- **非活动时间**：收到消息会回复"休息中"提示
- **时间控制**：基于服务器时区（UTC+8）

### 命令支持
- `!help` - 显示帮助信息
- `!status` - 查看机器人状态
- `!image [关键词]` - 搜索并发送图片
- `!summary [文本]` - 文本摘要
- `!sentiment [文本]` - 情感分析
- `!clear` - 清除对话历史

## 扩展和定制

### 修改消息处理逻辑
编辑 `message_processor.py` 中的 `process_message` 方法：

```python
def process_message(self, message: Message):
    """处理收到的消息（根据新要求：只回复私信，@必须回复）"""
    # 当前逻辑：
    # 1. 私信 -> 自动回复
    # 2. 群聊@消息 -> 必须回复
    # 3. 群聊非@消息 -> 忽略
```

### 添加新功能
1. 在 `deepseek_client.py` 中添加新的AI功能
2. 在 `rich_media.py` 中添加新的富媒体类型
3. 在 `active_sender.py` 中添加新的定时任务

### 调整在线时间
修改 `config.py` 中的配置：
```python
active_hours_start: int = 6    # 开始时间（小时）
active_hours_end: int = 22     # 结束时间（小时）
```

## 支持与维护

### 监控
- GitHub Actions运行状态
- 机器人连接状态
- API调用成功率

### 更新
1. 定期更新Python依赖
2. 监控DeepSeek API变更
3. 适配TailChat API更新

### 备份
- 定期备份配置
- 保存重要对话记录
- 备份自定义功能代码

## 总结

TailChat AI机器人项目已完整创建并准备好部署。主要特点：

1. **智能回复**：基于DeepSeek AI的智能对话
2. **精准控制**：只回复私信和@消息，避免干扰
3. **富媒体支持**：表情、图片、网址、Git仓库图片
4. **主动交互**：定时发送消息，增强用户互动
5. **可靠部署**：GitHub Actions自动化运行
6. **灵活配置**：环境变量控制所有关键参数

现在您可以将项目上传到GitHub仓库，配置Secrets，并开始使用这个智能机器人！

---

**下一步**：上传项目 → 配置GitHub Secrets → 触发工作流 → 测试功能 → 投入使用