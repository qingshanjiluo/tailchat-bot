"""
TailChat AI 机器人主程序
"""

import time
import signal
import sys
from datetime import datetime
from loguru import logger

from config import config
from tailchat_client import client as tailchat_client
from deepseek_client import deepseek_client
from message_processor import processor as message_processor
from active_sender import active_sender
from rich_media import rich_media
from git_image_support import git_image_support


class TailChatAIBot:
    """TailChat AI 机器人主类"""

    def __init__(self):
        self.running = False
        self.shutdown_requested = False

        # 设置日志
        self._setup_logging()

        logger.info("TailChat AI 机器人初始化中...")

    def _setup_logging(self):
        """设置日志"""
        logger.remove()  # 移除默认处理器

        # 添加控制台输出
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO",
        )

        # 添加文件输出
        logger.add(
            "logs/bot_{time:YYYY-MM-DD}.log",
            rotation="00:00",  # 每天轮换
            retention="7 days",  # 保留7天
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
        )

    def initialize(self) -> bool:
        """初始化机器人"""
        try:
            # 验证配置
            if not config.validate():
                logger.error("配置验证失败")
                return False

            # 初始化DeepSeek客户端
            if not deepseek_client.is_available():
                logger.error("DeepSeek客户端初始化失败")
                return False

            # 登录TailChat
            if not tailchat_client.login():
                logger.error("TailChat登录失败")
                return False

            # 连接WebSocket
            if not tailchat_client.connect_websocket():
                logger.error("WebSocket连接失败")
                return False

            # 注册消息处理器
            tailchat_client.add_message_handler(message_processor.process_message)

            # 启动主动消息发送器
            active_sender.start()

            logger.info("机器人初始化完成")
            return True

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False

    def run(self):
        """运行机器人主循环"""
        if not self.initialize():
            logger.error("初始化失败，无法启动机器人")
            return

        self.running = True
        logger.info("🤖 TailChat AI 机器人已启动！")

        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # 显示状态信息
        self._print_status()

        # 主循环
        try:
            while self.running and not self.shutdown_requested:
                # 检查连接状态
                if not tailchat_client.is_connected():
                    logger.warning("WebSocket连接断开，尝试重连...")
                    if not tailchat_client.connect_websocket():
                        logger.error("重连失败，等待10秒后重试")
                        time.sleep(10)
                        continue

                # 检查是否在在线时间内
                if self._is_active_hours():
                    # 在线时间，正常运行
                    time.sleep(1)
                else:
                    # 非在线时间，休眠更长时间
                    logger.info("非在线时间，进入节能模式...")
                    time.sleep(60)  # 每分钟检查一次

                # 定期状态报告（每小时一次）
                current_time = datetime.now()
                if current_time.minute == 0 and current_time.second < 5:
                    self._print_status()

        except KeyboardInterrupt:
            logger.info("收到键盘中断信号")
        except Exception as e:
            logger.error(f"主循环异常: {e}")
        finally:
            self.shutdown()

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，准备关闭...")
        self.shutdown_requested = True

    def shutdown(self):
        """关闭机器人"""
        if not self.running:
            return

        logger.info("正在关闭机器人...")

        # 停止主动消息发送器
        active_sender.stop()

        # 断开TailChat连接
        tailchat_client.disconnect()

        # 清理Git图片临时文件
        git_image_support.cleanup_temp_files()

        self.running = False
        logger.info("机器人已关闭")

    def _is_active_hours(self) -> bool:
        """检查是否在在线时间内"""
        now = datetime.now()
        current_hour = now.hour

        if config.behavior.active_hours_start <= config.behavior.active_hours_end:
            # 正常时间范围，如 6:00-22:00
            return (
                config.behavior.active_hours_start
                <= current_hour
                < config.behavior.active_hours_end
            )
        else:
            # 跨天时间范围，如 22:00-6:00
            return (
                current_hour >= config.behavior.active_hours_start
                or current_hour < config.behavior.active_hours_end
            )

    def _print_status(self):
        """打印状态信息"""
        now = datetime.now()
        is_active = self._is_active_hours()

        status_info = f"""
        ========================================
        TailChat AI 机器人状态
        时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
        运行状态: {'🟢 运行中' if self.running else '🔴 已停止'}
        在线时间: {config.behavior.active_hours_start}:00 - {config.behavior.active_hours_end}:00
        当前状态: {'🟢 在线' if is_active else '🔴 离线'}
        TailChat连接: {'🟢 已连接' if tailchat_client.is_connected() else '🔴 断开'}
        DeepSeek API: {'🟢 可用' if deepseek_client.is_available() else '🔴 不可用'}
        自动回复: {'🟢 开启' if config.behavior.auto_reply else '🔴 关闭'}
        Git图片支持: {'🟢 已配置' if config.git.repo_url else '🔴 未配置'}
        ========================================
        """

        logger.info(status_info)

    def get_status(self) -> dict:
        """获取详细状态信息"""
        now = datetime.now()

        return {
            "timestamp": now.isoformat(),
            "running": self.running,
            "active_hours": {
                "start": config.behavior.active_hours_start,
                "end": config.behavior.active_hours_end,
                "is_active": self._is_active_hours(),
            },
            "connections": {
                "tailchat": tailchat_client.is_connected(),
                "deepseek": deepseek_client.is_available(),
            },
            "features": {
                "auto_reply": config.behavior.auto_reply,
                "git_support": bool(config.git.repo_url),
                "rich_media": True,
                "active_messaging": active_sender.running,
            },
            "statistics": {
                "conversation_history_count": len(deepseek_client.conversation_history),
                "scheduled_jobs": (
                    len(active_sender.scheduler.jobs)
                    if hasattr(active_sender, "scheduler")
                    else 0
                ),
            },
        }


def main():
    """主函数"""
    bot = TailChatAIBot()

    try:
        bot.run()
    except Exception as e:
        logger.error(f"机器人运行异常: {e}")
        bot.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
