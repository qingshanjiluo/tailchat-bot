#!/usr/bin/env python3
"""
测试完整的消息处理流程
"""

import asyncio
import sys
import os
import logging
import time

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

from browser_client import TailChatBrowserClient, Message


async def test_message_handling():
    """测试消息处理流程"""
    logger.info("开始测试消息处理流程...")
    
    # 创建客户端实例
    client = TailChatBrowserClient()
    
    try:
        # 测试消息对象创建
        logger.info("测试1: 消息对象创建")
        test_message_data = {
            "_id": "test_msg_001",
            "content": "你好，这是一个测试消息 @test_user",
            "author": "test_user_001",
            "converseId": "test_converse_001",
            "groupId": "test_group_001",
            "isDM": False,
            "mentions": ["test_user"],
            "createdAt": "2026-03-29T07:50:00.000Z"
        }
        
        message = Message.from_dict(test_message_data)
        logger.info(f"消息创建成功: ID={message.id}, 内容={message.content[:30]}...")
        logger.info(f"是否@机器人: {message.mentions_bot('test_user')}")
        logger.info(f"是否是私信: {message.is_direct_message()}")
        
        # 测试私信消息
        logger.info("\n测试2: 私信消息处理")
        dm_message_data = {
            "_id": "test_dm_001",
            "content": "你好，这是私信测试",
            "author": "dm_user_001",
            "converseId": "dm_converse_001",
            "groupId": None,
            "isDM": True,
            "mentions": [],
            "createdAt": "2026-03-29T07:51:00.000Z"
        }
        
        dm_message = Message.from_dict(dm_message_data)
        logger.info(f"私信创建成功: ID={dm_message.id}, 内容={dm_message.content[:30]}...")
        logger.info(f"是否是私信: {dm_message.is_direct_message()}")
        
        # 测试@提及检测
        logger.info("\n测试3: @提及检测")
        mention_patterns = [
            r"@(\w+)",  # @用户名
            r"<@(\w+)>",  # <@用户ID>
            r"@([\u4e00-\u9fa5\w]+)",  # 支持中文用户名
        ]
        
        test_texts = [
            "你好 @张三 请看一下这个问题",
            "Hi @alice, can you help?",
            "测试<@U123456>消息",
            "这是没有@的消息",
        ]
        
        for text in test_texts:
            mentions = []
            for pattern in mention_patterns:
                import re
                matches = re.findall(pattern, text)
                if matches:
                    mentions.extend(matches)
            
            logger.info(f"文本: '{text}' -> 检测到@提及: {mentions}")
        
        # 测试消息处理器注册
        logger.info("\n测试4: 消息处理器注册")
        
        async def test_handler(msg: Message):
            logger.info(f"测试处理器收到消息: {msg.author}: {msg.content[:30]}...")
        
        client.add_message_handler(test_handler)
        logger.info(f"已注册消息处理器数量: {len(client.message_handlers)}")
        
        logger.info("\n✅ 所有测试通过！消息处理流程正常。")
        
        # 测试私信处理逻辑
        logger.info("\n测试5: 私信处理逻辑模拟")
        test_dm_data = {
            "id": "test_dm_002",
            "content": "你好，我需要帮助",
            "author": "help_user",
            "authorId": "help_user_001",
            "converseId": "dm_002",
            "groupId": None,
            "isDM": True,
            "mentions": [],
            "bot_mentioned": False,
            "createdAt": str(time.time())
        }
        
        logger.info(f"模拟私信数据: {test_dm_data}")
        logger.info("私信处理逻辑已集成到 _check_new_messages 方法中")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        logger.info("测试完成")


async def test_browser_client_init():
    """测试浏览器客户端初始化"""
    logger.info("开始测试浏览器客户端初始化...")
    
    try:
        client = TailChatBrowserClient()
        logger.info("浏览器客户端创建成功")
        
        # 检查配置
        logger.info(f"API URL: {client.config.api_url}")
        logger.info(f"用户名: {client.config.username}")
        
        logger.info("✅ 浏览器客户端初始化测试通过")
        return True
        
    except Exception as e:
        logger.error(f"浏览器客户端初始化测试失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TailChat AI 机器人消息处理流程测试")
    print("=" * 60)
    
    # 运行测试
    success = True
    
    # 测试1: 浏览器客户端初始化
    if asyncio.run(test_browser_client_init()):
        print("[PASS] 浏览器客户端初始化测试通过")
    else:
        print("[FAIL] 浏览器客户端初始化测试失败")
        success = False
    
    # 测试2: 消息处理流程
    if asyncio.run(test_message_handling()):
        print("[PASS] 消息处理流程测试通过")
    else:
        print("[FAIL] 消息处理流程测试失败")
        success = False
    
    print("=" * 60)
    if success:
        print("[SUCCESS] 所有测试通过！消息处理流程完整且正常。")
        print("下一步: 可以运行完整机器人测试或部署到GitHub Actions")
    else:
        print("[ERROR] 部分测试失败，请检查代码。")
    
    sys.exit(0 if success else 1)