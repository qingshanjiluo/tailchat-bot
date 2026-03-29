#!/bin/bash

# TailChat AI Bot 部署到GitHub脚本
# 目标仓库: https://github.com/qingshanjiluo/tailchat-bot

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
    echo "    TailChat AI Bot 部署工具"
    echo "========================================"
    echo ""
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "需要安装 $1"
        exit 1
    fi
}

# 克隆目标仓库
clone_target_repo() {
    local target_dir="$1"
    
    if [ -d "$target_dir" ]; then
        log_warn "目录 $target_dir 已存在"
        read -p "是否覆盖？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$target_dir"
        else
            log_error "部署取消"
            exit 1
        fi
    fi
    
    log_step "1. 克隆目标仓库..."
    git clone https://github.com/qingshanjiluo/tailchat-bot.git "$target_dir"
    
    if [ $? -eq 0 ]; then
        log_info "仓库克隆成功"
    else
        log_error "仓库克隆失败"
        exit 1
    fi
}

# 复制项目文件
copy_project_files() {
    local source_dir="$1"
    local target_dir="$2"
    
    log_step "2. 复制项目文件..."
    
    # 复制主要文件
    cp -r "$source_dir"/* "$target_dir"/
    
    # 复制隐藏文件（除了.git）
    cp "$source_dir"/.env.example "$target_dir"/
    cp "$source_dir"/.gitignore "$target_dir"/ 2>/dev/null || true
    
    # 复制GitHub Actions工作流
    mkdir -p "$target_dir/.github/workflows"
    cp -r "$source_dir/.github/workflows"/* "$target_dir/.github/workflows/"
    
    log_info "文件复制完成"
}

# 创建配置文件
create_config_file() {
    local target_dir="$1"
    
    log_step "3. 创建配置文件..."
    
    cd "$target_dir"
    
    if [ -f ".env" ]; then
        log_warn ".env 文件已存在"
        read -p "是否覆盖？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "使用现有配置文件"
            return
        fi
    fi
    
    # 从示例文件创建
    cp .env.example .env
    
    log_info "配置文件已创建，请编辑 .env 文件填写以下信息："
    echo ""
    echo "必需配置："
    echo "1. TAILCHAT_APP_ID     - TailChat OpenAPI应用ID"
    echo "2. TAILCHAT_APP_SECRET - TailChat OpenAPI应用密钥"
    echo "3. DEEPSEEK_API_KEY    - DeepSeek API密钥"
    echo ""
    echo "可选配置："
    echo "4. TAILCHAT_API_URL    - TailChat服务器地址（默认: https://chat.mk49.cyou）"
    echo "5. ACTIVE_MESSAGE_USERS - 主动消息接收用户ID（逗号分隔）"
    echo ""
    
    read -p "是否现在编辑配置文件？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        elif command -vi &> /dev/null; then
            vi .env
        else
            log_warn "未找到文本编辑器，请手动编辑 .env 文件"
        fi
    fi
}

# 测试配置
test_configuration() {
    local target_dir="$1"
    
    log_step "4. 测试配置..."
    
    cd "$target_dir"
    
    # 检查Python环境
    if ! command -v python3 &> /dev/null; then
        log_error "需要安装Python3"
        return 1
    fi
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip install -r requirements.txt > /dev/null 2>&1 || {
        log_error "依赖安装失败"
        return 1
    }
    
    # 测试配置
    log_info "测试配置..."
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from config import config
    print('✅ 配置导入成功')
    print(f'   TailChat API: {config.tailchat.api_url}')
    print(f'   DeepSeek API: {'已配置' if config.deepseek.api_key else '未配置'}')
    print(f'   在线时间: {config.behavior.active_hours_start}:00-{config.behavior.active_hours_end}:00')
    
    if config.validate():
        print('✅ 配置验证通过')
    else:
        print('❌ 配置验证失败')
except Exception as e:
    print(f'❌ 配置测试失败: {e}')
    sys.exit(1)
" || {
        log_error "配置测试失败"
        return 1
    }
    
    log_info "配置测试完成"
    return 0
}

# 设置GitHub Secrets说明
show_github_secrets_instructions() {
    log_step "5. GitHub Secrets 配置说明"
    
    echo ""
    echo "在推送代码前，需要在GitHub仓库中配置以下Secrets："
    echo ""
    echo "1. 访问 https://github.com/qingshanjiluo/tailchat-bot/settings/secrets/actions"
    echo "2. 点击 'New repository secret'"
    echo "3. 添加以下Secrets："
    echo ""
    echo "   | Secret名称         | 值                          |"
    echo "   |-------------------|-----------------------------|"
    echo "   | TAILCHAT_APP_ID   | 您的TailChat App ID         |"
    echo "   | TAILCHAT_APP_SECRET | 您的TailChat App Secret   |"
    echo "   | DEEPSEEK_API_KEY  | 您的DeepSeek API密钥        |"
    echo "   | TAILCHAT_API_URL  | https://chat.mk49.cyou      |"
    echo ""
    
    read -p "是否已记下这些信息？(按Enter继续)" -n 1 -r
    echo
}

# 提交和推送代码
commit_and_push() {
    local target_dir="$1"
    
    log_step "6. 提交代码到GitHub..."
    
    cd "$target_dir"
    
    # 检查git状态
    if [ -z "$(git status --porcelain)" ]; then
        log_info "没有更改需要提交"
        return 0
    fi
    
    # 添加文件
    git add .
    
    # 提交
    git commit -m "添加TailChat AI机器人
- 添加AI机器人核心功能
- 配置GitHub Actions工作流
- 更新文档和配置文件"
    
    # 推送
    log_info "推送代码到GitHub..."
    git push origin main
    
    if [ $? -eq 0 ]; then
        log_info "代码推送成功"
    else
        log_error "代码推送失败"
        return 1
    fi
}

# 显示部署完成信息
show_completion_info() {
    log_step "7. 部署完成！"
    
    echo ""
    echo "🎉 TailChat AI机器人部署完成！"
    echo ""
    echo "下一步操作："
    echo ""
    echo "1. 验证GitHub Secrets配置"
    echo "   访问: https://github.com/qingshanjiluo/tailchat-bot/settings/secrets/actions"
    echo ""
    echo "2. 手动触发工作流测试"
    echo "   访问: https://github.com/qingshanjiluo/tailchat-bot/actions"
    echo "   点击 'Run TailChat AI Bot' 工作流"
    echo "   点击 'Run workflow' 按钮"
    echo ""
    echo "3. 监控运行状态"
    echo "   在工作流运行页面查看日志"
    echo "   检查机器人是否正常连接"
    echo ""
    echo "4. 测试机器人功能"
    echo "   在TailChat中："
    echo "   - 发送私信给机器人"
    echo "   - 在群聊中@机器人"
    echo "   - 使用!help查看命令"
    echo ""
    echo "5. 配置主动消息（可选）"
    echo "   在.env文件中设置ACTIVE_MESSAGE_USERS"
    echo "   添加要接收主动消息的用户ID"
    echo ""
    echo "机器人行为说明："
    echo "✅ 只回复私信消息"
    echo "✅ @消息必须回复"
    echo "✅ 可以主动发送消息"
    echo "✅ 在线时间: 6:00-22:00"
    echo "❌ 不回复群聊非@消息"
    echo ""
    echo "如需帮助，请查看文档："
    echo "- README.md - 完整文档"
    echo "- DEPLOY_TO_GITHUB.md - 部署指南"
    echo "- QUICKSTART.md - 快速开始"
    echo ""
}

# 主函数
main() {
    show_title
    
    # 检查必要命令
    check_command git
    check_command python3
    check_command pip
    
    # 设置目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    TARGET_DIR="$(pwd)/tailchat-bot-deploy"
    
    # 执行部署步骤
    clone_target_repo "$TARGET_DIR"
    copy_project_files "$SCRIPT_DIR" "$TARGET_DIR"
    create_config_file "$TARGET_DIR"
    
    if test_configuration "$TARGET_DIR"; then
        show_github_secrets_instructions
        
        read -p "是否提交代码到GitHub？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            commit_and_push "$TARGET_DIR"
        else
            log_warn "代码未提交，请手动提交"
        fi
        
        show_completion_info
    else
        log_error "配置测试失败，请检查配置文件"
        exit 1
    fi
}

# 运行主函数
main "$@"