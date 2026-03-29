"""
DeepSeek API 客户端模块 - 集成对话记录
"""

import json
import time
from typing import Dict, List, Optional, Any
import requests
from openai import OpenAI
from loguru import logger

from config import config
from conversation_manager import conversation_manager


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self):
        self.config = config.deepseek
        self.client = None
        self.conversation_history = {}  # 会话ID -> 消息历史
        self.max_history_length = 20  # 最大历史消息数

        self._init_client()

    def _init_client(self):
        """初始化OpenAI客户端"""
        try:
            # DeepSeek兼容OpenAI API
            self.client = OpenAI(
                api_key=self.config.api_key, base_url=self.config.api_url
            )
            logger.info("DeepSeek客户端初始化成功")
        except Exception as e:
            logger.error(f"DeepSeek客户端初始化失败: {e}")
            self.client = None

    def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        与DeepSeek聊天（集成对话记录）

        Args:
            message: 用户消息
            conversation_id: 会话ID，用于维护对话历史
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数
            user_id: 用户ID（用于对话记录）
            user_name: 用户名（用于对话记录）

        Returns:
            Dict包含回复和状态
        """
        try:
            if not self.client:
                logger.error("DeepSeek客户端未初始化")
                return {"success": False, "error": "客户端未初始化"}

            # 构建消息历史（使用对话管理器）
            messages = self._build_messages_with_history(
                message, conversation_id, system_prompt
            )

            # 调用API
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
            )

            # 提取回复
            reply = response.choices[0].message.content

            # 记录助手回复到对话管理器
            if conversation_id and config.conversation.enable_history:
                conversation_manager.add_assistant_message(
                    converse_id=conversation_id,
                    content=reply,
                    user_id=user_id,
                    user_name=user_name,
                )

            logger.info(f"DeepSeek回复生成成功，长度: {len(reply)}")

            return {
                "success": True,
                "reply": reply,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "conversation_id": conversation_id,
            }

        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            return {"success": False, "error": str(e)}

    def _build_messages_with_history(
        self, message: str, conversation_id: Optional[str], system_prompt: Optional[str]
    ) -> List[Dict[str, str]]:
        """构建消息列表（使用对话管理器）"""
        messages = []

        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            # 默认系统提示
            messages.append(
                {
                    "role": "system",
                    "content": """你是一个友好的AI助手，帮助用户解答问题。请用中文回复，保持友好、有帮助的态度。
                
                你的特点：
                1. 用中文回复，语气友好自然
                2. 回答要具体、有帮助
                3. 可以适当使用表情符号增加亲和力
                4. 如果不知道答案，诚实说明
                5. 保持对话连贯性，参考之前的对话历史""",
                }
            )

        # 添加历史消息（从对话管理器获取）
        if conversation_id and config.conversation.enable_history:
            history = conversation_manager.get_conversation_history_for_ai(
                conversation_id
            )
            if history:
                messages.extend(history)
                logger.debug(f"使用对话历史: {len(history)} 条消息")

        # 添加当前用户消息
        messages.append({"role": "user", "content": message})

        logger.debug(f"构建消息完成，总共 {len(messages)} 条消息")
        return messages

    def _build_messages(
        self, message: str, conversation_id: Optional[str], system_prompt: Optional[str]
    ) -> List[Dict[str, str]]:
        """构建消息列表（兼容旧版本）"""
        return self._build_messages_with_history(
            message, conversation_id, system_prompt
        )

    def _update_conversation_history(
        self, conversation_id: str, user_message: str, assistant_reply: str
    ):
        """更新对话历史"""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []

        history = self.conversation_history[conversation_id]

        # 添加用户消息和助手回复
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_reply})

        # 限制历史长度
        if len(history) > self.max_history_length * 2:
            self.conversation_history[conversation_id] = history[
                -self.max_history_length * 2 :
            ]

    def clear_conversation_history(self, conversation_id: Optional[str] = None):
        """清空对话历史"""
        if conversation_id:
            if conversation_id in self.conversation_history:
                del self.conversation_history[conversation_id]
                logger.info(f"已清空会话 {conversation_id} 的历史")
        else:
            self.conversation_history.clear()
            logger.info("已清空所有会话历史")

    def generate_image_prompt(self, topic: str) -> str:
        """为给定主题生成图片描述"""
        try:
            prompt = f"为以下主题生成一个详细的图片描述，适合用于AI生成图片:\n主题: {topic}\n\n描述应该包含视觉元素、风格、色彩和氛围。用中文描述。"

            response = self.chat(
                message=prompt,
                system_prompt="你是一个专业的图片描述生成器。请根据用户提供的主题，生成详细、生动、富有视觉感的图片描述。描述应该包含具体的视觉元素、艺术风格、色彩搭配和整体氛围。",
            )

            if response["success"]:
                return response["reply"]
            else:
                return f"一张关于{topic}的图片"

        except Exception as e:
            logger.error(f"生成图片描述失败: {e}")
            return f"一张关于{topic}的图片"

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感"""
        try:
            prompt = f"分析以下文本的情感倾向:\n文本: {text}\n\n请分析情感倾向（积极/消极/中性）、情感强度（0-10分）和主要情感关键词。"

            response = self.chat(
                message=prompt,
                system_prompt="你是一个情感分析专家。请分析文本的情感倾向、情感强度和情感关键词。以JSON格式回复，包含sentiment（积极/消极/中性）、intensity（0-10）、keywords（关键词列表）字段。",
            )

            if response["success"]:
                # 尝试解析JSON回复
                try:
                    import re

                    json_str = re.search(r"\{.*\}", response["reply"], re.DOTALL)
                    if json_str:
                        return json.loads(json_str.group())
                except:
                    pass

                # 如果解析失败，返回简单分析
                return {"sentiment": "neutral", "intensity": 5, "keywords": ["未知"]}
            else:
                return {"error": "分析失败"}

        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {"error": str(e)}

    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """文本摘要"""
        try:
            prompt = f"请将以下文本摘要为{max_length}字以内的简洁版本:\n\n{text}"

            response = self.chat(
                message=prompt,
                system_prompt="你是一个专业的文本摘要工具。请将用户提供的文本摘要为简洁、准确的版本，保留核心信息。",
            )

            if response["success"]:
                return response["reply"]
            else:
                return text[:max_length] + "..." if len(text) > max_length else text

        except Exception as e:
            logger.error(f"文本摘要失败: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text

    def is_available(self) -> bool:
        """检查API是否可用"""
        return self.client is not None


# 单例客户端
deepseek_client = DeepSeekClient()
