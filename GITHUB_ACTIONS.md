# GitHub Actions 自动化访问 TailChat

本文档介绍如何使用GitHub Actions自动访问TailChat网站（https://chat.mk49.cyou/）。

## 功能特性

### 自动化访问
- ✅ **定时访问**: 每天北京时间6:00-22:00之间每小时自动访问
- ✅ **手动触发**: 支持通过GitHub界面手动触发
- ✅ **健康检查**: 检查网站HTTP状态、加载时间、页面元素
- ✅ **截图功能**: 自动截取网站页面截图
- ✅ **结果报告**: 生成详细的访问报告

### 基于用户交互记录
根据提供的 `inspector-export-1774750241417.json` 文件，工作流可以：
- 模拟用户点击行为
- 导航到好友页面 (`/main/personal/friends`)
- 检查好友列表
- 执行测试操作（点击设置、开关等）

## 工作流配置

### 1. 简单访问工作流 (`simple-visit.yml`)
**功能**: 基本的网站健康检查和截图
- 检查HTTP状态码
- 测量页面加载时间
- 截取页面截图
- 检查TailChat特定元素

**触发条件**:
- 定时触发: 每天UTC时间22-14点（北京时间6-22点）每小时运行
- 手动触发: 通过GitHub Actions界面手动运行

### 2. 完整自动化工作流 (`auto-visit-tailchat.yml`)
**功能**: 完整的用户交互模拟
- 访问首页并检查登录状态
- 导航到好友页面
- 检查好友列表
- 执行测试操作（基于JSON记录）
- 全面的健康检查

## 使用方法

### 快速开始

1. **将工作流文件复制到你的仓库**
   ```bash
   mkdir -p .github/workflows
   cp tailchat-ai-bot/.github/workflows/simple-visit.yml .github/workflows/
   ```

2. **启用GitHub Actions**
   - 推送代码到GitHub仓库
   - 进入仓库的"Actions"标签页
   - 启用工作流

3. **手动运行工作流**
   - 在Actions页面找到"Simple TailChat Visit"工作流
   - 点击"Run workflow"
   - 选择要访问的URL（默认: https://chat.mk49.cyou/）

### 自定义配置

#### 修改定时计划
编辑 `.github/workflows/simple-visit.yml` 中的 `schedule` 部分：
```yaml
schedule:
  # UTC时间，北京时间 = UTC+8
  - cron: '0 */2 * * *'  # 每2小时运行一次
  - cron: '0 0,6,12,18 * * *'  # 每天0,6,12,18点运行
```

#### 添加环境变量
在工作流文件中添加环境变量：
```yaml
env:
  TAILCHAT_URL: ${{ secrets.TAILCHAT_URL || 'https://chat.mk49.cyou/' }}
  CHECK_FRIENDS: true
```

#### 配置GitHub Secrets
对于需要认证的访问，可以配置Secrets：
1. 进入仓库 Settings → Secrets and variables → Actions
2. 添加以下Secrets（如果需要）：
   - `TAILCHAT_USERNAME`: TailChat用户名
   - `TAILCHAT_PASSWORD`: TailChat密码
   - `TAILCHAT_API_KEY`: API密钥

## 工作流详解

### 执行步骤

1. **环境准备**
   - 检出代码
   - 安装Python 3.10
   - 安装依赖 (requests, beautifulsoup4, playwright)

2. **浏览器安装**
   - 安装Chromium浏览器
   - 安装系统依赖

3. **执行访问脚本**
   - 运行Python自动化脚本
   - 访问目标网站
   - 执行检查操作

4. **结果处理**
   - 保存JSON格式的结果文件
   - 上传截图和结果文件作为Artifact
   - 显示执行摘要

### 输出结果

工作流会生成以下输出：

1. **JSON结果文件** (`visit_results.json`)
   ```json
   {
     "main_page": {
       "success": true,
       "status_code": 200,
       "load_time": 3.45,
       "title": "TailChat",
       "tailchat_elements": {
         "has_tailchat_app": true,
         "has_login_form": false,
         "has_chat_interface": true
       }
     },
     "friends_page": {
       "accessible": true,
       "status_code": 200
     }
   }
   ```

2. **页面截图** (`/tmp/tailchat_*.png`)
   - 完整的页面截图
   - 用于视觉验证

3. **控制台输出**
   - 详细的执行日志
   - 成功/失败状态

## 高级功能

### 基于用户记录的自动化

如果你有用户交互记录（如提供的JSON文件），可以：

1. **解析用户操作**
   ```python
   # 从JSON提取点击操作
   with open('inspector-export-1774750241417.json') as f:
       data = json.load(f)
   
   for record in data['records']:
       if record['type'] == 'click':
           selector = record['selector']
           # 使用Playwright模拟点击
           page.click(selector)
   ```

2. **创建自定义工作流**
   - 复制 `auto-visit-tailchat.yml`
   - 修改操作序列
   - 添加特定的用户交互

### 集成通知

可以扩展工作流以发送通知：

```yaml
- name: Send Discord notification
  if: always()
  uses: sarisia/actions-status-discord@v1
  with:
    webhook: ${{ secrets.DISCORD_WEBHOOK }}
    status: ${{ job.status }}
    title: "TailChat访问结果"
```

## 故障排除

### 常见问题

1. **Playwright安装失败**
   ```
   解决方案: 确保使用正确的系统依赖
   ```
   ```yaml
   steps:
     - name: Install Playwright dependencies
       run: |
         sudo apt-get update
         sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
   ```

2. **网站访问超时**
   ```
   解决方案: 增加超时时间
   ```
   ```python
   page.goto(url, wait_until='networkidle', timeout=120000)  # 120秒
   ```

3. **截图失败**
   ```
   解决方案: 检查存储权限
   ```
   ```yaml
   - name: Fix permissions
     run: |
       sudo chmod -R 777 /tmp
   ```

### 调试技巧

1. **启用详细日志**
   ```yaml
   env:
     DEBUG: pw:api  # Playwright调试日志
     PYTHONUNBUFFERED: 1
   ```

2. **保存HTML内容**
   ```python
   # 在脚本中添加
   html_content = page.content()
   with open('page.html', 'w') as f:
       f.write(html_content)
   ```

3. **使用非无头模式调试**
   ```python
   # 临时禁用headless模式
   browser = p.chromium.launch(headless=False)
   ```

## 安全考虑

### 最佳实践

1. **不要硬编码凭证**
   - 使用GitHub Secrets存储敏感信息
   - 不在日志中输出密码或令牌

2. **限制访问频率**
   - 避免过于频繁的访问
   - 尊重网站的robots.txt

3. **数据清理**
   - 工作流结束后清理临时文件
   - 不保存不必要的用户数据

### 隐私保护

- 工作流运行在GitHub的隔离环境中
- 截图和结果文件默认保留7天
- 可以配置更短的保留时间

## 扩展功能

### 添加更多检查

```python
def check_chat_functionality(page):
    """检查聊天功能"""
    # 检查消息输入框
    has_input = page.locator('textarea, input[type="text"]').count() > 0
    
    # 检查发送按钮
    has_send_button = page.locator('button:has-text("发送"), button:has-text("Send")').count() > 0
    
    return {
        "has_message_input": has_input,
        "has_send_button": has_send_button
    }
```

### 性能监控

```python
def measure_performance(page):
    """测量性能指标"""
    # 使用Performance API
    performance = page.evaluate('''() => {
        const perf = window.performance;
        return {
            load_time: perf.timing.loadEventEnd - perf.timing.navigationStart,
            dom_ready: perf.timing.domContentLoadedEventEnd - perf.timing.navigationStart,
            entries: perf.getEntriesByType('navigation')[0]
        };
    }''')
    return performance
```

## 支持与反馈

### 获取帮助

1. **查看工作流日志**
   - 在GitHub Actions页面查看详细日志
   - 检查错误信息和堆栈跟踪

2. **调试脚本**
   - 在本地运行Python脚本测试
   - 使用 `--headless=false` 参数查看浏览器行为

3. **社区支持**
   - GitHub Issues: 报告问题或请求功能
   - GitHub Discussions: 讨论使用技巧

### 贡献指南

欢迎贡献改进：

1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

---

**开始自动化你的TailChat访问吧！** 🚀

通过GitHub Actions，你可以确保TailChat网站的可访问性，监控其健康状况，并基于实际用户交互进行自动化测试。