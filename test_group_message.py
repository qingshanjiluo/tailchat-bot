#!/usr/bin/env python3
"""
测试群聊消息获取和@回复功能
"""

import asyncio
import sys
import time
from loguru import logger

# 添加项目路径
sys.path.insert(0, '.')

from browser_client import TailChatBrowserClient
from message_processor import processor as message_processor
from tailchat_client import Message

class GroupMessageTester:
    """群聊消息测试器"""
    
    def __init__(self):
        self.client = TailChatBrowserClient()
        self.test_messages_received = 0
        self.test_mentions_received = 0
        
    async def test_message_handler(self, message):
        """测试消息处理器"""
        try:
            logger.info(f"测试收到消息: {message.author}: {message.content[:50]}...")
            logger.info(f"  是否是私信: {message.is_direct_message()}")
            logger.info(f"  是否@机器人: {message.mentions}")
            logger.info(f"  消息ID: {message.id}")
            
            self.test_messages_received += 1
            
            # 检查是否@了机器人
            if message.mentions:
                self.test_mentions_received += 1
                logger.info(f"  检测到@提及: {message.mentions}")
                
            # 调用实际的消息处理器
            message_processor.process_message(message)
            
        except Exception as e:
            logger.error(f"测试消息处理失败: {e}")
    
    async def run_test(self, duration_seconds=60):
        """运行测试"""
        logger.info("=== 开始群聊消息获取和@回复测试 ===")
        
        # 注册测试消息处理器
        self.client.add_message_handler(self.test_message_handler)
        
        try:
            # 启动浏览器客户端
            logger.info("启动浏览器客户端...")
            success = await self.client.run()
            if not success:
                logger.error("浏览器客户端启动失败")
                return False
            
            logger.info(f"开始监听消息，持续时间: {duration_seconds}秒")
            
            # 等待指定时间
            start_time = time.time()
            while time.time() - start_time < duration_seconds:
                await asyncio.sleep(1)
                
                # 每10秒输出一次状态
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0:
                    logger.info(f"测试进行中: {elapsed}/{duration_seconds}秒, 收到消息: {self.test_messages_received}, @消息: {self.test_mentions_received}")
            
            # 测试结果
            logger.info("=== 测试结果 ===")
            logger.info(f"总运行时间: {duration_seconds}秒")
            logger.info(f"收到的消息总数: {self.test_messages_received}")
            logger.info(f"收到的@消息数: {self.test_mentions_received}")
            
            if self.test_messages_received > 0:
                logger.success("✓ 消息获取功能正常")
            else:
                logger.warning("⚠ 未收到任何消息，可能需要检查:")
                logger.warning("  1. 是否在正确的群聊页面")
                logger.warning("  2. 是否有新消息")
                logger.warning("  3. DOM选择器是否正确")
            
            if self.test_mentions_received > 0:
                logger.success("✓ @消息检测功能正常")
            else:
                logger.warning("⚠ 未检测到@消息，可以尝试:")
                logger.warning("  1. 在群聊中@机器人")
                logger.warning("  2. 检查@检测逻辑")
            
            return True
            
        except Exception as e:
            logger.error(f"测试运行失败: {e}")
            return False
        finally:
            # 关闭客户端
            await self.client.close()
            logger.info("测试完成，客户端已关闭")

async def main():
    """主函数"""
    tester = GroupMessageTester()
    
    # 运行测试
    await tester.run_test(duration_seconds=120)  # 2分钟测试
    
    # 测试建议
    logger.info("=== 测试建议 ===")
    logger.info("1. 确保TailChat页面在正确的群聊中")
    logger.info("2. 尝试发送普通消息和@机器人的消息")
    logger.info("3. 观察日志输出，确认消息被正确检测")
    logger.info("4. 检查机器人是否回复了@消息")

if __name__ == "__main__":
    # 设置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    
    # 运行测试
    asyncio.run(main())