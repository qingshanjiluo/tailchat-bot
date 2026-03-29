"""
TailChat AI Bot 测试脚本
用于测试各个模块的功能
"""

import sys
import os
from loguru import logger

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from deepseek_client import deepseek_client
from rich_media import rich_media
from git_image_support import git_image_support


def test_config():
    """测试配置模块"""
    print("=== 测试配置模块 ===")

    # 验证配置
    if config.validate():
        print("✅ 配置验证通过")

        # 显示配置信息
        print(f"TailChat API URL: {config.tailchat.api_url}")
        print(f"DeepSeek API Key: {'已设置' if config.deepseek.api_key else '未设置'}")
        print(
            f"在线时间: {config.behavior.active_hours_start}:00 - {config.behavior.active_hours_end}:00"
        )
        print(f"Git仓库: {config.git.repo_url or '未配置'}")
    else:
        print("❌ 配置验证失败")

    print()


def test_deepseek():
    """测试DeepSeek API"""
    print("=== 测试DeepSeek API ===")

    if not deepseek_client.is_available():
        print("❌ DeepSeek客户端不可用")
        return

    # 测试简单对话
    print("测试简单对话...")
    response = deepseek_client.chat(
        message="你好，请用中文回复", system_prompt="你是一个测试助手，请回复'测试成功'"
    )

    if response["success"]:
        print(f"✅ DeepSeek API测试成功")
        print(f"回复: {response['reply'][:50]}...")
        print(f"Token使用: {response['usage']}")
    else:
        print(f"❌ DeepSeek API测试失败: {response.get('error', '未知错误')}")

    # 测试文本摘要
    print("\n测试文本摘要...")
    text = "人工智能是研究、开发用于模拟、延伸和扩展人的智能的理论、方法、技术及应用系统的一门新的技术科学。人工智能是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。"
    summary = deepseek_client.summarize_text(text, max_length=50)
    print(f"摘要: {summary}")

    print()


def test_rich_media():
    """测试富媒体模块"""
    print("=== 测试富媒体模块 ===")

    # 测试表情添加
    text = "你好，今天天气真好"
    enhanced_text = rich_media.add_emojis(text, "happy", 2)
    print(f"原始文本: {text}")
    print(f"增强文本: {enhanced_text}")

    # 测试图片URL生成
    image_url = rich_media.generate_image_url("cat")
    print(f"\n图片URL: {image_url}")

    # 测试URL提取
    test_text = (
        "看看这个网站 https://example.com 和这张图片 https://example.com/image.jpg"
    )
    urls = rich_media.extract_urls(test_text)
    print(f"\n提取的URL: {urls}")

    # 测试媒体分析
    media_analysis = rich_media.analyze_media_content(test_text)
    print(f"媒体分析: {media_analysis}")

    print()


def test_git_image_support():
    """测试Git图片支持"""
    print("=== 测试Git图片支持 ===")

    if not config.git.repo_url:
        print("⚠️  Git仓库未配置，跳过测试")
        return

    # 测试URL解析
    repo_info = git_image_support.parse_git_url(config.git.repo_url)
    if repo_info:
        print(f"✅ Git仓库解析成功")
        print(f"平台: {repo_info['platform']}")
        print(f"所有者: {repo_info['owner']}")
        print(f"仓库: {repo_info['repo']}")
    else:
        print("❌ Git仓库解析失败")

    # 测试图片URL生成
    if repo_info:
        image_url = git_image_support.get_image_url("test.jpg", repo_info)
        print(f"\n图片URL示例: {image_url}")

    # 测试URL验证
    test_url = "https://raw.githubusercontent.com/username/repo/main/images/test.jpg"
    is_valid = git_image_support.validate_image_url(test_url)
    print(f"\nURL验证测试: {test_url} -> {'有效' if is_valid else '无效'}")

    print()


def test_integration():
    """测试集成功能"""
    print("=== 测试集成功能 ===")

    # 测试富媒体消息创建
    rich_message = rich_media.create_rich_message(
        text="这是一个测试消息",
        include_emoji=True,
        include_image=True,
        image_category="cat",
        include_links=["https://example.com"],
    )

    print("富媒体消息示例:")
    print(rich_message)
    print()

    # 测试欢迎消息
    welcome_msg = rich_media.create_welcome_message("测试用户")
    print("欢迎消息示例:")
    print(welcome_msg)

    print()


def main():
    """主测试函数"""
    print("🤖 TailChat AI Bot 测试套件")
    print("=" * 50)

    try:
        # 测试各个模块
        test_config()
        test_deepseek()
        test_rich_media()
        test_git_image_support()
        test_integration()

        print("✅ 所有测试完成！")
        print("\n下一步:")
        print("1. 确保.env文件配置正确")
        print("2. 运行 'python main.py' 启动机器人")
        print("3. 在TailChat中@机器人进行测试")

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
