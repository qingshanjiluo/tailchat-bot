"""
TailChat AI 机器人主程序 - 浏览器自动化版本
使用Playwright模拟人类操作登录和发送消息
"""
import asyncio
import time
import signal
import sys
from datetime import datetime
from loguru import logger

from config import config
from browser_client import TailChatBrowserClient
from deepseek_client import deepseek_client
from message_processor import processor as message_processor
from active_sender import active_sender
from rich_media import rich_media
from git_image_support import git_image_support


class TailChatAIBotBrowser:
    """TailChat AI 浏览器自动化机器人主类"""
    
    def __init__(self):
        self.running = False
        self.shutdown_requested = False
        self.client = TailChatBrowserClient()
        
        # 设置日志
        self._setup_logging()
        
        logger.info("TailChat AI 浏览器自动化机器人初始化中...")
    
    def _setup_logging(self):
        """设置日志"""
        logger.remove()  # 移除默认处理器
        
        # 添加控制台输出
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # 添加文件输出
        logger.add(
            "logs/bot_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # 每天轮换
            retention="7 days",  # 保留7天
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG"
        )
    
    async def initialize(self) -> bool:
        """初始化机器人"""
        try:
            # 验证配置
            if not config.validate():
                logger.error("配置验证失败")
                return False
            
            logger.info("配置验证通过")
            logger.info(f"TailChat URL: {config.tailchat.api_url}")
            logger.info(f"用户名: {config.tailchat.username}")
            logger.info(f"使用浏览器: {config.tailchat.use_browser}")
            logger.info(f"无头模式: {config.tailchat.headless}")
            logger.info(f"在线时间: {config.behavior.active_hours_start}:00-{config.behavior.active_hours_end}:00")
            
            # 初始化DeepSeek客户端
            if not deepseek_client.is_available():
                logger.error("DeepSeek客户端初始化失败")
                return False
            
            logger.info("DeepSeek客户端初始化成功")
            
            # 运行浏览器客户端
            logger.info("正在启动浏览器客户端...")
            
            # 注册消息处理器
            self.client.add_message_handler(self._handle_message_async)
            
            # 启动浏览器客户端
            success = await self.client.run()
            if not success:
                logger.error("浏览器客户端启动失败")
                return False
            
            logger.info("浏览器客户端启动成功")
            
            # 启动主动消息发送器
            active_sender.start()
            logger.info("主动消息发送器已启动")
            
            # 测试连接
            logger.info("正在测试连接...")
            if await self.client.test_connection():
                logger.info("连接测试成功")
            else:
                logger.warning("连接测试部分失败，但继续运行")
            
            logger.info("机器人初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False
    
    async def _handle_message_async(self, message):
        """异步处理消息"""
        try:
            # 调用消息处理器
            message_processor.process_message(message)
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，正在关闭...")
        self.shutdown_requested = True
    
    async def run(self):
        """运行机器人主循环"""
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # 初始化
        if not await self.initialize():
            logger.error("初始化失败，无法启动机器人")
            return
        
        self.running = True
        logger.info("🤖 TailChat AI 浏览器自动化机器人已启动！")
        
        # 显示状态信息
        self._show_status()
        
        try:
            # 主循环
            while self.running and not self.shutdown_requested:
                await asyncio.sleep(1)
                
                # 定期检查状态
                if int(time.time()) % 60 == 0:  # 每分钟检查一次
                    self._check_status()
                
                # 检查是否在活动时间
                if not self._is_active_hours():
                    if int(time.time()) % 300 == 0:  # 每5分钟记录一次
                        logger.info("非活动时间，机器人处于待机状态")
                    continue
                
                # 在这里可以添加其他定期任务
                
        except KeyboardInterrupt:
            logger.info("收到键盘中断")
        except Exception as e:
            logger.error(f"主循环错误: {e}")
        finally:
            await self.shutdown()
    
    def _show_status(self):
        """显示状态信息"""
        logger.info("=" * 50)
        logger.info("TailChat AI 浏览器自动化机器人")
        logger.info("=" * 50)
        logger.info(f"用户: {config.tailchat.username}")
        logger.info(f"服务器: {config.tailchat.api_url}")
        logger.info(f"在线时间: {config.behavior.active_hours_start}:00-{config.behavior.active_hours_end}:00")
        logger.info(f"当前时间: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("=" * 50)
        logger.info("机器人行为:")
        logger.info("  ✅ 只回复私信消息")
        logger.info("  ✅ @消息必须回复")
        logger.info("  ✅ 可以主动发送消息")
        logger.info("  ❌ 不回复群聊非@消息")
        logger.info("=" * 50)
    
    def _check_status(self):
        """检查状态"""
        current_time = datetime.now().strftime("%H:%M:%S")
        is_active = self._is_active_hours()
        
        status_msg = "🟢 运行中" if is_active else "🟡 待机中"
        logger.info(f"状态检查: {status_msg} | 时间: {current_time} | 用户: {config.tailchat.username}")
    
    def _is_active_hours(self) -> bool:
        """检查是否在活动时间内"""
        current_hour = datetime.now().hour
        return config.behavior.active_hours_start <= current_hour < config.behavior.active_hours_end
    
    async def shutdown(self):
        """关闭机器人"""
        if not self.running:
            return
        
        logger.info("正在关闭机器人...")
        self.running = False
        
        # 停止主动消息发送器
        active_sender.stop()
        logger.info("主动消息发送器已停止")
        
        # 断开浏览器连接
        await self.client.disconnect()
        logger.info("浏览器客户端已断开")
        
        # 清理资源
        git_image_support.cleanup_temp_files()
        logger.info("临时文件已清理")
        
        logger.info("🤖 机器人已安全关闭")


async def main():
    """主函数"""
    bot = TailChatAIBotBrowser()
    await bot.run()


if __name__ == "__main__":
    # 创建logs目录
    import os
    os.makedirs("logs", exist_ok=True)
    
    # 运行机器人
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        sys.exit(1)