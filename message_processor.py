"""
消息处理器和AI决策模块
"""

import re
import random
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger

from config import config
from tailchat_client import Message, client as tailchat_client
from deepseek_client import deepseek_client
from conversation_manager import conversation_manager


class MessageProcessor:
    """消息处理器"""

    def __init__(self):
        self.config = config.behavior
        self.tailchat = tailchat_client
        self.deepseek = deepseek_client

        # 命令前缀
        self.command_prefix = ["!", "！", "/"]

        # 命令处理函数映射
        self.command_handlers = {
            "help": self._handle_help,
            "clear": self._handle_clear,
            "status": self._handle_status,
            "image": self._handle_image,
            "summary": self._handle_summary,
            "sentiment": self._handle_sentiment,
        }

        # 关键词触发回复
        self.keyword_triggers = {
            "你好": ["你好！", "嗨！", "你好呀！"],
            "谢谢": ["不客气！", "很高兴能帮到你！", "这是我的荣幸！"],
            "哈哈": ["😄", "😂", "有什么好笑的吗？"],
            "再见": ["再见！", "下次再见！", "拜拜！"],
        }

        # 用户状态跟踪
        self.user_states = {}

        logger.info("消息处理器初始化完成")

    def process_message(self, message: Message):
        """处理收到的消息（根据新要求：只回复私信，@必须回复）"""
        try:
            # 检查是否在线时间内
            if not self._is_active_hours():
                logger.info(f"非在线时间，忽略消息: {message.content[:50]}...")
                # 即使不在线时间，@也必须回复
                if message.mentions_bot(self.tailchat.user_id):
                    self._send_busy_message(message)
                return

            # 检查是否是命令（命令在任何情况下都处理）
            if self._is_command(message.content):
                self._handle_command(message)
                return

            # 检查是否@了机器人 - @必须回复（新要求）
            if message.mentions_bot(self.tailchat.user_id):
                logger.info(f"收到@消息，必须回复: {message.content[:50]}...")
                self._handle_mention(message)
                return

            # 检查是否是私信 - 只回复私信（新要求）
            if message.is_direct_message():
                logger.info(f"收到私信，进行回复: {message.content[:50]}...")
                self._handle_direct_message(message)
                return

            # 新要求：不回复群聊中的非@消息
            # 只记录日志，不进行任何回复
            logger.debug(
                f"忽略群聊非@消息: {message.author} -> {message.content[:50]}..."
            )

        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    def _is_active_hours(self) -> bool:
        """检查是否在在线时间内"""
        now = datetime.now()
        current_hour = now.hour

        if self.config.active_hours_start <= self.config.active_hours_end:
            # 正常时间范围，如 6:00-22:00
            return (
                self.config.active_hours_start
                <= current_hour
                < self.config.active_hours_end
            )
        else:
            # 跨天时间范围，如 22:00-6:00
            return (
                current_hour >= self.config.active_hours_start
                or current_hour < self.config.active_hours_end
            )

    def _send_busy_message(self, message: Message):
        """发送忙碌消息"""
        self.tailchat.send_message(
            message.converse_id, self.config.busy_message, mentions=[message.author_id]
        )

    def _is_command(self, content: str) -> bool:
        """检查是否是命令"""
        if not content:
            return False

        content = content.strip()
        for prefix in self.command_prefix:
            if content.startswith(prefix):
                return True
        return False

    def _handle_command(self, message: Message):
        """处理命令"""
        content = message.content.strip()

        # 提取命令和参数
        for prefix in self.command_prefix:
            if content.startswith(prefix):
                content = content[len(prefix) :]
                break

        parts = content.split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # 查找命令处理器
        if command in self.command_handlers:
            logger.info(f"处理命令: {command}, 参数: {args}")
            self.command_handlers[command](message, args)
        else:
            # 未知命令
            reply = f"未知命令: {command}\n可用命令: {', '.join(self.command_handlers.keys())}"
            self.tailchat.send_message(
                message.converse_id, reply, mentions=[message.author_id]
            )

    def _handle_help(self, message: Message, args: str):
        """处理帮助命令"""
        help_text = """🤖 AI助手命令帮助:
        
        !help - 显示此帮助信息
        !clear - 清除当前会话的对话历史
        !status - 查看机器人状态
        !image <主题> - 生成图片描述
        !summary <文本> - 文本摘要
        !sentiment <文本> - 情感分析
        
        直接@我或私信我可以进行对话！
        """

        self.tailchat.send_message(
            message.converse_id, help_text, mentions=[message.author_id]
        )

    def _handle_clear(self, message: Message, args: str):
        """清除对话历史"""
        conversation_id = message.converse_id
        self.deepseek.clear_conversation_history(conversation_id)

        reply = "✅ 已清除当前会话的对话历史"
        self.tailchat.send_message(
            message.converse_id, reply, mentions=[message.author_id]
        )

    def _handle_status(self, message: Message, args: str):
        """处理状态命令"""
        now = datetime.now()
        is_active = self._is_active_hours()

        status_text = f"""📊 机器人状态:
        
        当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
        在线时间: {self.config.active_hours_start}:00 - {self.config.active_hours_end}:00
        当前状态: {'🟢 在线' if is_active else '🔴 离线'}
        自动回复: {'开启' if self.config.auto_reply else '关闭'}
        回复概率: {self.config.auto_reply_probability * 100}%
        DeepSeek: {'可用' if self.deepseek.is_available() else '不可用'}
        """

        self.tailchat.send_message(
            message.converse_id, status_text, mentions=[message.author_id]
        )

    def _handle_image(self, message: Message, args: str):
        """处理图片生成命令"""
        if not args:
            reply = "请提供图片主题，例如: !image 日落"
            self.tailchat.send_message(
                message.converse_id, reply, mentions=[message.author_id]
            )
            return

        # 生成图片描述
        image_prompt = self.deepseek.generate_image_prompt(args)

        # 构建回复（可以包含图片链接）
        reply = f"🎨 图片描述: {args}\n\n{image_prompt}\n\n(提示: 可以将此描述用于AI绘图工具)"

        self.tailchat.send_message(
            message.converse_id, reply, mentions=[message.author_id]
        )

    def _handle_summary(self, message: Message, args: str):
        """处理文本摘要命令"""
        if not args:
            reply = "请提供要摘要的文本，例如: !summary 这是一段很长的文本..."
            self.tailchat.send_message(
                message.converse_id, reply, mentions=[message.author_id]
            )
            return

        # 生成摘要
        summary = self.deepseek.summarize_text(args)

        reply = f"📝 文本摘要:\n\n{summary}"
        self.tailchat.send_message(
            message.converse_id, reply, mentions=[message.author_id]
        )

    def _handle_sentiment(self, message: Message, args: str):
        """处理情感分析命令"""
        if not args:
            reply = "请提供要分析的文本，例如: !sentiment 我今天很开心"
            self.tailchat.send_message(
                message.converse_id, reply, mentions=[message.author_id]
            )
            return

        # 分析情感
        sentiment = self.deepseek.analyze_sentiment(args)

        if "error" in sentiment:
            reply = f"情感分析失败: {sentiment['error']}"
        else:
            sentiment_emoji = {"积极": "😊", "消极": "😔", "中性": "😐"}
            emoji = sentiment_emoji.get(sentiment.get("sentiment", "中性"), "😐")

            reply = f"{emoji} 情感分析结果:\n"
            reply += f"倾向: {sentiment.get('sentiment', '未知')}\n"
            reply += f"强度: {sentiment.get('intensity', 0)}/10\n"
            reply += f"关键词: {', '.join(sentiment.get('keywords', []))}"

        self.tailchat.send_message(
            message.converse_id, reply, mentions=[message.author_id]
        )

    def _handle_mention(self, message: Message):
        """处理@机器人的消息"""
        # 提取纯文本内容（去掉@部分）
        content = self._extract_clean_content(message.content, message.mentions)

        if not content.strip():
            # 如果只是@没有内容，发送欢迎消息
            reply = self.config.welcome_message
            self.tailchat.send_message(
                message.converse_id, reply, mentions=[message.author_id]
            )
            return

        # 使用DeepSeek生成回复
        conversation_id = message.converse_id

        # 记录用户消息到对话管理器
        if config.conversation.enable_history:
            conversation_manager.add_user_message(
                converse_id=conversation_id,
                content=content,
                user_id=message.author_id,
                user_name=message.author,
                is_dm=message.is_direct_message(),
                mentions=message.mentions,
            )

        # 构建系统提示
        system_prompt = self._build_system_prompt(message)

        # 调用DeepSeek（传递用户信息用于对话记录）
        response = self.deepseek.chat(
            message=content,
            conversation_id=conversation_id,
            system_prompt=system_prompt,
            user_id=message.author_id,
            user_name=message.author,
        )

        if response["success"]:
            reply = response["reply"]

            # 限制回复长度
            if len(reply) > self.config.max_message_length:
                reply = reply[: self.config.max_message_length] + "..."

            # 发送回复
            self.tailchat.send_message(
                message.converse_id, reply, mentions=[message.author_id]
            )
        else:
            # API调用失败，发送错误消息
            error_reply = "抱歉，我暂时无法处理你的请求。请稍后再试。"
            self.tailchat.send_message(
                message.converse_id, error_reply, mentions=[message.author_id]
            )

    def _handle_direct_message(self, message: Message):
        """处理私信"""
        # 私信处理逻辑与@类似，但可以更个性化
        content = message.content

        if not content.strip():
            reply = "你好！我是AI助手，有什么可以帮你的吗？"
            self.tailchat.send_message(message.converse_id, reply)
            return

        # 使用DeepSeek生成回复
        conversation_id = message.converse_id

        # 记录用户消息到对话管理器
        if config.conversation.enable_history:
            conversation_manager.add_user_message(
                converse_id=conversation_id,
                content=content,
                user_id=message.author_id,
                user_name=message.author,
                is_dm=True,  # 私信
                mentions=message.mentions,
            )

        # 私信使用更友好的系统提示
        system_prompt = "你是一个友好的AI助手，正在通过私信与用户交流。请保持友好、有帮助的态度，用中文回复。"

        response = self.deepseek.chat(
            message=content,
            conversation_id=conversation_id,
            system_prompt=system_prompt,
            user_id=message.author_id,
            user_name=message.author,
        )

        if response["success"]:
            reply = response["reply"]

            # 限制回复长度
            if len(reply) > self.config.max_message_length:
                reply = reply[: self.config.max_message_length] + "..."

            # 发送回复
            self.tailchat.send_message(message.converse_id, reply)
        else:
            error_reply = "抱歉，我暂时无法处理你的消息。请稍后再试。"
            self.tailchat.send_message(message.converse_id, error_reply)

    def _handle_auto_reply(self, message: Message):
        """处理自动回复"""
        # 检查关键词触发
        content_lower = message.content.lower()

        for keyword, replies in self.keyword_triggers.items():
            if keyword in content_lower:
                reply = random.choice(replies)
                self.tailchat.send_message(message.converse_id, reply)
                return

        # 随机选择是否进行智能回复（避免过于频繁）
        if random.random() < 0.3:  # 30%概率进行智能回复
            # 使用DeepSeek生成简短回复
            conversation_id = message.converse_id

            # 构建提示，让回复简短
            prompt = f"请对以下消息生成一个简短、友好的回复:\n{message.content}"

            response = self.deepseek.chat(
                message=prompt,
                conversation_id=conversation_id,
                system_prompt="你是一个友好的聊天参与者。请生成简短、自然的回复，保持对话流畅。",
            )

            if response["success"]:
                reply = response["reply"]
                if len(reply) > 100:  # 自动回复不要太长
                    reply = reply[:100] + "..."

                self.tailchat.send_message(message.converse_id, reply)

    def _extract_clean_content(self, content: str, mentions: List[str]) -> str:
        """提取干净的文本内容（去掉@标记）"""
        if not mentions:
            return content

        # 简单的去除@标记
        for mention in mentions:
            content = content.replace(f"@{mention}", "").replace(f"@${mention}", "")

        return content.strip()

    def _build_system_prompt(self, message: Message) -> str:
        """构建系统提示"""
        base_prompt = "你是一个TailChat聊天平台上的AI助手。"

        if message.is_direct_message():
            base_prompt += " 你正在通过私信与用户交流。"
        else:
            base_prompt += " 你正在群组聊天中与用户交流。"

        base_prompt += """
        请用中文回复，保持友好、有帮助的态度。
        如果用户询问你的能力，可以介绍你可以回答问题、生成文本、分析情感等。
        保持回复简洁明了，避免过于冗长。
        """

        return base_prompt

    def send_welcome_message(self, user_id: str):
        """发送欢迎消息给新用户"""
        welcome_msg = self.config.welcome_message
        self.tailchat.send_direct_message(user_id, welcome_msg)

    def send_custom_message(
        self, converse_id: str, content: str, mentions: List[str] = None
    ):
        """发送自定义消息"""
        return self.tailchat.send_message(converse_id, content, mentions)


# 单例处理器
processor = MessageProcessor()
