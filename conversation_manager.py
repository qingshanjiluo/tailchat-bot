"""
对话记录管理器
记录和保存机器人与用户的对话历史
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from loguru import logger

from config import config


@dataclass
class ConversationMessage:
    """对话消息"""

    id: str
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: float
    user_id: str
    user_name: str
    converse_id: str
    is_dm: bool
    mentions: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ConversationMessage":
        return cls(**data)


@dataclass
class Conversation:
    """对话会话"""

    converse_id: str
    user_id: str
    user_name: str
    is_dm: bool
    created_at: float
    updated_at: float
    messages: List[ConversationMessage]
    message_count: int

    def add_message(self, message: ConversationMessage):
        """添加消息到对话"""
        self.messages.append(message)
        self.message_count += 1
        self.updated_at = time.time()

        # 限制消息数量
        if len(self.messages) > config.conversation.max_history_messages:
            self.messages = self.messages[-config.conversation.max_history_messages :]

    def get_recent_messages(self, count: int = 10) -> List[ConversationMessage]:
        """获取最近的消息"""
        return self.messages[-count:] if self.messages else []

    def get_conversation_history(self, for_ai: bool = False) -> List[Dict[str, str]]:
        """获取对话历史，格式化为AI可用的格式"""
        history = []
        for msg in self.messages[-config.conversation.max_history_messages :]:
            if for_ai:
                history.append({"role": msg.role, "content": msg.content})
            else:
                history.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": datetime.fromtimestamp(msg.timestamp).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "user": msg.user_name,
                    }
                )
        return history

    def to_dict(self) -> Dict:
        return {
            "converse_id": self.converse_id,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "is_dm": self.is_dm,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": self.message_count,
            "messages": [msg.to_dict() for msg in self.messages],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Conversation":
        messages = [
            ConversationMessage.from_dict(msg) for msg in data.get("messages", [])
        ]
        return cls(
            converse_id=data["converse_id"],
            user_id=data["user_id"],
            user_name=data["user_name"],
            is_dm=data["is_dm"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages,
            message_count=data["message_count"],
        )


class ConversationManager:
    """对话管理器"""

    def __init__(self):
        self.config = config.conversation
        self.conversations: Dict[str, Conversation] = {}
        self._ensure_directories()
        self._load_conversations()

        logger.info(f"对话管理器初始化完成，历史记录: {self.config.enable_history}")
        logger.info(f"对话保存路径: {self.config.history_path}")

    def _ensure_directories(self):
        """确保目录存在"""
        if self.config.enable_history:
            os.makedirs(self.config.history_path, exist_ok=True)
            logger.info(f"创建对话目录: {self.config.history_path}")

    def _get_conversation_filepath(self, converse_id: str) -> str:
        """获取对话文件路径"""
        safe_id = converse_id.replace("/", "_").replace("\\", "_").replace(":", "_")
        return os.path.join(self.config.history_path, f"{safe_id}.json")

    def _load_conversations(self):
        """加载保存的对话"""
        if not self.config.enable_history:
            return

        try:
            if not os.path.exists(self.config.history_path):
                return

            for filename in os.listdir(self.config.history_path):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.config.history_path, filename)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            conversation = Conversation.from_dict(data)
                            self.conversations[conversation.converse_id] = conversation
                    except Exception as e:
                        logger.warning(f"加载对话文件失败 {filename}: {e}")

            logger.info(f"已加载 {len(self.conversations)} 个对话历史")

        except Exception as e:
            logger.error(f"加载对话历史失败: {e}")

    def _save_conversation(self, conversation: Conversation):
        """保存对话到文件"""
        if not self.config.enable_history:
            return

        try:
            filepath = self._get_conversation_filepath(conversation.converse_id)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(conversation.to_dict(), f, ensure_ascii=False, indent=2)

            logger.debug(f"对话已保存: {conversation.converse_id}")

        except Exception as e:
            logger.error(f"保存对话失败 {conversation.converse_id}: {e}")

    def get_or_create_conversation(
        self, converse_id: str, user_id: str, user_name: str, is_dm: bool
    ) -> Conversation:
        """获取或创建对话"""
        if converse_id in self.conversations:
            return self.conversations[converse_id]

        conversation = Conversation(
            converse_id=converse_id,
            user_id=user_id,
            user_name=user_name,
            is_dm=is_dm,
            created_at=time.time(),
            updated_at=time.time(),
            messages=[],
            message_count=0,
        )

        self.conversations[converse_id] = conversation
        return conversation

    def add_user_message(self, message_data: Dict) -> Conversation:
        """添加用户消息"""
        converse_id = message_data.get("converseId", "unknown")
        user_id = message_data.get("author", "unknown")
        user_name = message_data.get("author", "未知用户")
        is_dm = message_data.get("isDM", False)

        conversation = self.get_or_create_conversation(
            converse_id, user_id, user_name, is_dm
        )

        user_message = ConversationMessage(
            id=message_data.get("_id", str(time.time())),
            role="user",
            content=message_data.get("content", ""),
            timestamp=time.time(),
            user_id=user_id,
            user_name=user_name,
            converse_id=converse_id,
            is_dm=is_dm,
            mentions=message_data.get("mentions", []),
        )

        conversation.add_message(user_message)
        self._save_conversation(conversation)

        logger.info(f"记录用户消息: {user_name} -> {converse_id}")
        return conversation

    def add_assistant_message(
        self, converse_id: str, content: str, user_id: str = None, user_name: str = None
    ) -> Optional[Conversation]:
        """添加助手回复"""
        if converse_id not in self.conversations:
            logger.warning(f"找不到对话 {converse_id}，无法记录助手回复")
            return None

        conversation = self.conversations[converse_id]

        # 如果没有提供用户信息，使用对话中的信息
        if user_id is None:
            user_id = conversation.user_id
        if user_name is None:
            user_name = conversation.user_name

        assistant_message = ConversationMessage(
            id=f"assistant_{int(time.time())}",
            role="assistant",
            content=content,
            timestamp=time.time(),
            user_id=user_id,
            user_name=user_name,
            converse_id=converse_id,
            is_dm=conversation.is_dm,
            mentions=[],
        )

        conversation.add_message(assistant_message)
        self._save_conversation(conversation)

        logger.info(f"记录助手回复: {converse_id}")
        return conversation

    def get_conversation_history_for_ai(
        self, converse_id: str, max_messages: int = None
    ) -> List[Dict[str, str]]:
        """获取AI可用的对话历史"""
        if converse_id not in self.conversations:
            return []

        conversation = self.conversations[converse_id]
        if max_messages is None:
            max_messages = config.conversation.max_history_messages

        return conversation.get_conversation_history(for_ai=True)[-max_messages:]

    def get_conversation_summary(self, converse_id: str) -> Dict[str, Any]:
        """获取对话摘要"""
        if converse_id not in self.conversations:
            return {"error": "对话不存在"}

        conversation = self.conversations[converse_id]

        return {
            "converse_id": conversation.converse_id,
            "user_name": conversation.user_name,
            "is_dm": conversation.is_dm,
            "message_count": conversation.message_count,
            "created_at": datetime.fromtimestamp(conversation.created_at).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "updated_at": datetime.fromtimestamp(conversation.updated_at).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "recent_messages": [
                {
                    "role": msg.role,
                    "content": (
                        msg.content[:100] + "..."
                        if len(msg.content) > 100
                        else msg.content
                    ),
                    "time": datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S"),
                }
                for msg in conversation.get_recent_messages(5)
            ],
        }

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """获取所有对话摘要"""
        conversations = []
        for conv in self.conversations.values():
            summary = self.get_conversation_summary(conv.converse_id)
            if "error" not in summary:
                conversations.append(summary)

        # 按更新时间排序
        conversations.sort(key=lambda x: x["updated_at"], reverse=True)
        return conversations

    def clear_conversation(self, converse_id: str) -> bool:
        """清空对话历史"""
        if converse_id in self.conversations:
            conversation = self.conversations[converse_id]
            conversation.messages = []
            conversation.message_count = 0
            conversation.updated_at = time.time()

            self._save_conversation(conversation)
            logger.info(f"已清空对话历史: {converse_id}")
            return True

        return False

    def delete_conversation(self, converse_id: str) -> bool:
        """删除对话"""
        if converse_id in self.conversations:
            del self.conversations[converse_id]

            # 删除文件
            if self.config.enable_history:
                filepath = self._get_conversation_filepath(converse_id)
                if os.path.exists(filepath):
                    os.remove(filepath)

            logger.info(f"已删除对话: {converse_id}")
            return True

        return False

    def cleanup_old_conversations(self, max_age_days: int = 30):
        """清理旧的对话"""
        if not self.config.enable_history:
            return

        cutoff_time = time.time() - (max_age_days * 24 * 3600)
        deleted_count = 0

        for converse_id, conversation in list(self.conversations.items()):
            if (
                conversation.updated_at < cutoff_time
                and conversation.message_count == 0
            ):
                self.delete_conversation(converse_id)
                deleted_count += 1

        logger.info(f"清理了 {deleted_count} 个旧对话")

    def export_conversation(
        self, converse_id: str, format: str = "json"
    ) -> Optional[str]:
        """导出对话"""
        if converse_id not in self.conversations:
            return None

        conversation = self.conversations[converse_id]

        if format == "json":
            return json.dumps(conversation.to_dict(), ensure_ascii=False, indent=2)
        elif format == "text":
            lines = []
            lines.append(f"对话ID: {conversation.converse_id}")
            lines.append(f"用户: {conversation.user_name}")
            lines.append(f"类型: {'私信' if conversation.is_dm else '群聊'}")
            lines.append(f"消息数量: {conversation.message_count}")
            lines.append(
                f"创建时间: {datetime.fromtimestamp(conversation.created_at).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            lines.append(
                f"更新时间: {datetime.fromtimestamp(conversation.updated_at).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            lines.append("=" * 50)

            for msg in conversation.messages:
                time_str = datetime.fromtimestamp(msg.timestamp).strftime("%H:%M:%S")
                role_str = "用户" if msg.role == "user" else "助手"
                lines.append(f"[{time_str}] {role_str}: {msg.content}")

            return "\n".join(lines)

        return None


# 全局对话管理器实例
conversation_manager = ConversationManager()
