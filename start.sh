#!/bin/bash

# TailChat AI Bot 启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查Python
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python，请安装Python 3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    log_info "找到Python: $PYTHON_CMD (版本: $PYTHON_VERSION)"
    
    # 检查Python版本
    if [[ "$PYTHON_VERSION" < "3.8" ]]; then
        log_error "需要Python 3.8+，当前版本: $PYTHON_VERSION"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        log_error "未找到requirements.txt文件"
        exit 1
    fi
    
    # 检查是否已安装依赖
    if $PYTHON_CMD -c "import dotenv, requests, websocket, openai, schedule, loguru" &> /dev/null; then
        log_info "依赖已安装"
    else
        log_warn "依赖未安装，正在安装..."
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            log_info "依赖安装成功"
        else
            log_error "依赖安装失败"
            exit 1
        fi
    fi
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warn "未找到.env文件，从.env.example创建..."
            cp .env.example .env
            log_info "已创建.env文件，请编辑配置文件后重新启动"
            exit 0
        else
            log_error "未找到.env或.env.example文件"
            exit 1
        fi
    fi
    
    # 检查必要配置
    source .env 2>/dev/null || true
    
    if [ -z "$TAILCHAT_APP_ID" ] || [ -z "$TAILCHAT_APP_SECRET" ]; then
        log_error "请配置TAILCHAT_APP_ID和TAILCHAT_APP_SECRET"
        exit 1
    fi
    
    if [ -z "$DEEPSEEK_API_KEY" ]; then
        log_error "请配置DEEPSEEK_API_KEY"
        exit 1
    fi
    
    log_info "配置文件检查通过"
}

# 创建日志目录
setup_logs() {
    if [ ! -d "logs" ]; then
        log_info "创建日志目录..."
        mkdir -p logs
    fi
}

# 启动机器人
start_bot() {
    log_info "启动TailChat AI机器人..."
    
    # 设置Python路径
    export PYTHONPATH=$(pwd):$PYTHONPATH
    
    # 运行机器人
    $PYTHON_CMD main.py
}

# 主函数
main() {
    log_info "========================================"
    log_info "    TailChat AI Bot 启动脚本"
    log_info "========================================"
    
    # 检查Python
    check_python
    
    # 检查依赖
    check_dependencies
    
    # 检查配置文件
    check_config
    
    # 设置日志目录
    setup_logs
    
    # 启动机器人
    start_bot
}

# 运行主函数
main "$@"