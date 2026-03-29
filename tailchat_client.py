"""
TailChat 客户端模块
"""

import json
import time
import random
import asyncio
import websocket
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import requests
from loguru import logger

from config import config


@dataclass
class Message:
    """消息对象"""

    id: str
    content: str
    author: str
    author_id: str
    converse_id: str
    group_id: Optional[str]
    is_dm: bool
    mentions: List[str]
    created_at: str

    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        return cls(
            id=data.get("_id", ""),
            content=data.get("content", ""),
            author=data.get("author", ""),
            author_id=data.get("author", ""),  # TailChat中author就是用户ID
            converse_id=data.get("converseId", ""),
            group_id=data.get("groupId"),
            is_dm=data.get("isDM", False),
            mentions=data.get("mentions", []),
            created_at=data.get("createdAt", ""),
        )

    def mentions_bot(self, bot_user_id: str) -> bool:
        """检查是否@了机器人"""
        return bot_user_id in self.mentions

    def is_direct_message(self) -> bool:
        """检查是否是私信"""
        return self.is_dm


class TailChatClient:
    """TailChat 客户端"""

    def __init__(self):
        self.config = config.tailchat
        self.ws = None
        self.connected = False
        self.user_id = None
        self.token = None
        self.message_handlers = []
        self.heartbeat_thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def login(self) -> bool:
        """登录TailChat获取token"""
        try:
            logger.info(f"正在登录TailChat: {self.config.api_url}")

            # 使用OpenAPI登录
            login_url = f"{self.config.api_url}/api/openapi/bot/login"
            payload = {"appId": self.config.app_id, "appSecret": self.config.app_secret}

            response = requests.post(login_url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            self.token = data.get("data", {}).get("token")
            self.user_id = data.get("data", {}).get("userId")

            if not self.token or not self.user_id:
                logger.error("登录失败: 未获取到token或userId")
                return False

            logger.info(f"登录成功, userId: {self.user_id}")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"登录请求失败: {e}")
            return False
        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            return False

    def connect_websocket(self) -> bool:
        """连接WebSocket"""
        try:
            ws_url = f"ws://{self.config.api_url.replace('http://', '').replace('https://', '')}/socket.io/?token={self.token}&EIO=4&transport=websocket"
            logger.info(f"正在连接WebSocket: {ws_url}")

            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )

            # 启动WebSocket线程
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()

            # 等待连接建立
            for _ in range(10):
                if self.connected:
                    break
                time.sleep(0.5)

            if self.connected:
                logger.info("WebSocket连接成功")
                self._start_heartbeat()
                return True
            else:
                logger.error("WebSocket连接超时")
                return False

        except Exception as e:
            logger.error(f"连接WebSocket失败: {e}")
            return False

    def _on_open(self, ws):
        """WebSocket连接打开"""
        logger.info("WebSocket连接已打开")
        self.connected = True
        self.reconnect_attempts = 0

        # 发送连接确认
        ws.send("40")

    def _on_message(self, ws, message):
        """处理WebSocket消息"""
        try:
            if message.startswith("40"):
                # 连接确认
                logger.debug("收到连接确认")
                self._send_auth()
            elif message.startswith("42"):
                # 事件消息
                self._handle_event(message)
            elif message.startswith("2"):
                # 心跳响应
                self._handle_pong()
            elif message.startswith("3"):
                # 心跳请求
                ws.send("2")
            else:
                logger.debug(f"收到未知消息: {message[:50]}")

        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")

    def _send_auth(self):
        """发送认证消息"""
        auth_data = ["auth", {"token": self.token}]
        self._send_event("auth", auth_data)

    def _handle_event(self, message: str):
        """处理事件消息"""
        try:
            # 解析消息格式: 42["event", data]
            if message.startswith("42["):
                content = message[2:]  # 去掉"42"
                data = json.loads(content)

                if len(data) >= 2:
                    event_name = data[0]
                    event_data = data[1]

                    if event_name == "message":
                        self._handle_message_event(event_data)
                    elif event_name == "message.update":
                        self._handle_message_update(event_data)
                    elif event_name == "message.delete":
                        self._handle_message_delete(event_data)
                    elif event_name == "friend.request":
                        self._handle_friend_request(event_data)
                    elif event_name == "connection":
                        logger.info(f"连接状态: {event_data}")
                    else:
                        logger.debug(f"收到事件: {event_name}")

        except json.JSONDecodeError as e:
            logger.error(f"解析事件消息失败: {e}, 消息: {message[:100]}")
        except Exception as e:
            logger.error(f"处理事件失败: {e}")

    def _handle_message_event(self, data: Dict):
        """处理新消息事件"""
        try:
            message_data = data.get("message", {})
            message = Message.from_dict(message_data)

            # 忽略自己发送的消息
            if message.author_id == self.user_id:
                return

            logger.info(f"收到新消息: {message.author} -> {message.content[:50]}...")

            # 触发消息处理器
            for handler in self.message_handlers:
                try:
                    handler(message)
                except Exception as e:
                    logger.error(f"消息处理器执行失败: {e}")

        except Exception as e:
            logger.error(f"处理消息事件失败: {e}, 数据: {data}")

    def _handle_message_update(self, data: Dict):
        """处理消息更新事件"""
        logger.debug(f"消息更新: {data}")

    def _handle_message_delete(self, data: Dict):
        """处理消息删除事件"""
        logger.debug(f"消息删除: {data}")

    def _handle_friend_request(self, data: Dict):
        """处理好友请求事件"""
        logger.info(f"收到好友请求: {data}")

    def _handle_pong(self):
        """处理心跳响应"""
        pass

    def _on_error(self, ws, error):
        """WebSocket错误处理"""
        logger.error(f"WebSocket错误: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket连接关闭"""
        logger.info(f"WebSocket连接关闭: {close_status_code} - {close_msg}")
        self.connected = False

        # 尝试重连
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            wait_time = min(30, 2**self.reconnect_attempts)  # 指数退避
            logger.info(
                f"{wait_time}秒后尝试重连... (尝试 {self.reconnect_attempts}/{self.max_reconnect_attempts})"
            )
            time.sleep(wait_time)
            self.connect_websocket()

    def _send_event(self, event: str, data: Any):
        """发送事件"""
        if self.ws and self.connected:
            message = json.dumps([event, data])
            self.ws.send(f"42{message}")

    def _start_heartbeat(self):
        """启动心跳线程"""

        def heartbeat():
            while self.connected:
                try:
                    if self.ws and self.connected:
                        self.ws.send("2")  # 发送ping
                    time.sleep(25)  # 每25秒发送一次心跳
                except Exception as e:
                    logger.error(f"心跳发送失败: {e}")
                    break

        self.heartbeat_thread = threading.Thread(target=heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def send_message(
        self, converse_id: str, content: str, mentions: List[str] = None
    ) -> bool:
        """发送消息"""
        try:
            if not self.connected:
                logger.error("未连接到WebSocket")
                return False

            message_data = {
                "converseId": converse_id,
                "content": content,
                "plain": content,
            }

            if mentions:
                message_data["mentions"] = mentions

            self._send_event("chat.message.sendMessage", message_data)
            logger.info(f"已发送消息到 {converse_id}: {content[:50]}...")
            return True

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    def send_direct_message(self, user_id: str, content: str) -> bool:
        """发送私信"""
        try:
            # 首先获取或创建私信会话
            url = f"{self.config.api_url}/api/user/dm/create"
            headers = {"x-token": self.token}
            payload = {"memberIds": [user_id]}

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            converse_id = data.get("data", {}).get("converseId")

            if converse_id:
                return self.send_message(converse_id, content, mentions=[user_id])
            else:
                logger.error("获取私信会话失败")
                return False

        except Exception as e:
            logger.error(f"发送私信失败: {e}")
            return False

    def add_message_handler(self, handler: Callable[[Message], None]):
        """添加消息处理器"""
        self.message_handlers.append(handler)

    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connected and self.connected

    def disconnect(self):
        """断开连接"""
        if self.ws:
            self.ws.close()
        self.connected = False
        logger.info("已断开TailChat连接")


# 单例客户端
client = TailChatClient()
