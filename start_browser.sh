#!/bin/bash

# TailChat AI 机器人 - 浏览器自动化版本启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 显示标题
show_title() {
    echo ""
    echo "========================================"
    echo "    TailChat AI 浏览器自动化机器人"
    echo "========================================"
    echo ""
}

# 检查Python环境
check_python() {
    log_step "1. 检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "需要安装Python3"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    log_info "Python版本: $python_version"
    
    # 检查Python版本
    if [[ $(echo "$python_version 3.8" | awk '{print ($1 < $2)}') -eq 1 ]]; then
        log_error "需要Python 3.8或更高版本"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    log_step "2. 安装Python依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "找不到 requirements.txt 文件"
        exit 1
    fi
    
    log_info "安装依赖包..."
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        log_info "依赖安装完成"
    else
        log_error "依赖安装失败"
        exit 1
    fi
}

# 安装Playwright浏览器
install_playwright_browsers() {
    log_step "3. 安装Playwright浏览器..."
    
    log_info "安装Chromium浏览器..."
    python3 -m playwright install chromium
    
    if [ $? -eq 0 ]; then
        log_info "浏览器安装完成"
    else
        log_warn "浏览器安装失败，尝试继续运行"
    fi
}

# 检查环境变量
check_env() {
    log_step "4. 检查环境变量..."
    
    if [ ! -f ".env" ]; then
        log_warn "未找到 .env 文件"
        log_info "从示例文件创建 .env 文件..."
        
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "已创建 .env 文件，请编辑该文件填写配置"
            log_info "必需配置:"
            echo ""
            echo "  TAILCHAT_USERNAME     - 您的TailChat用户名"
            echo "  TAILCHAT_PASSWORD     - 您的TailChat密码"
            echo "  DEEPSEEK_API_KEY      - DeepSeek API密钥"
            echo ""
            echo "可选配置:"
            echo "  TAILCHAT_API_URL      - TailChat服务器地址 (默认: https://chat.mk49.cyou)"
            echo "  TAILCHAT_HEADLESS     - 是否使用无头模式 (默认: true)"
            echo ""
            
            read -p "是否现在编辑配置文件？(y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                if command -v nano &> /dev/null; then
                    nano .env
                elif command -v vim &> /dev/null; then
                    vim .env
                elif command -v vi &> /dev/null; then
                    vi .env
                else
                    log_warn "未找到文本编辑器，请手动编辑 .env 文件"
                fi
            fi
        else
            log_error "找不到 .env.example 文件"
            exit 1
        fi
    else
        log_info "找到 .env 文件"
    fi
}

# 测试配置
test_config() {
    log_step "5. 测试配置..."
    
    log_info "测试Python导入..."
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from config import config
    print('✅ 配置导入成功')
    print(f'   TailChat URL: {config.tailchat.api_url}')
    print(f'   用户名: {config.tailchat.username}')
    print(f'   使用浏览器: {config.tailchat.use_browser}')
    print(f'   无头模式: {config.tailchat.headless}')
    print(f'   DeepSeek API: {'已配置' if config.deepseek.api_key else '未配置'}')
    print(f'   在线时间: {config.behavior.active_hours_start}:00-{config.behavior.active_hours_end}:00')
    
    if config.validate():
        print('✅ 配置验证通过')
    else:
        print('❌ 配置验证失败')
        sys.exit(1)
except Exception as e:
    print(f'❌ 配置测试失败: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_info "配置测试完成"
    else
        log_error "配置测试失败"
        exit 1
    fi
}

# 创建日志目录
create_logs_dir() {
    log_step "6. 创建日志目录..."
    
    if [ ! -d "logs" ]; then
        mkdir -p logs
        log_info "已创建 logs 目录"
    else
        log_info "logs 目录已存在"
    fi
}

# 运行机器人
run_bot() {
    log_step "7. 启动机器人..."
    
    log_info "启动TailChat AI浏览器自动化机器人..."
    echo ""
    echo "机器人行为说明:"
    echo "  ✅ 只回复私信消息"
    echo "  ✅ @消息必须回复"
    echo "  ✅ 可以主动发送消息"
    echo "  ❌ 不回复群聊非@消息"
    echo "  ⏰ 在线时间: ${config.behavior.active_hours_start}:00-${config.behavior.active_hours_end}:00"
    echo ""
    echo "按 Ctrl+C 停止机器人"
    echo ""
    
    # 运行机器人
    python3 main_browser.py
}

# 显示完成信息
show_completion() {
    log_step "机器人已停止"
    
    echo ""
    echo "感谢使用TailChat AI浏览器自动化机器人！"
    echo ""
    echo "日志文件:"
    echo "  - logs/bot_$(date +%Y-%m-%d).log"
    echo ""
    echo "如需重新启动，请运行:"
    echo "  ./start_browser.sh"
    echo ""
}

# 主函数
main() {
    show_title
    
    # 检查当前目录
    if [ ! -f "main_browser.py" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行步骤
    check_python
    install_dependencies
    install_playwright_browsers
    check_env
    test_config
    create_logs_dir
    run_bot
    
    show_completion
}

# 运行主函数
main "$@"