#!/usr/bin/env python3
"""
消息调度系统
支持根据JSON指令执行不同的操作：
1. 发送群组消息
2. 发送私信
3. 进入指定群组
4. @特定用户
5. 定时消息
"""

import asyncio
import json
import time
import random
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from loguru import logger
from enum import Enum


class ActionType(Enum):
    """操作类型枚举"""
    SEND_GROUP_MESSAGE = "send_group_message"
    SEND_DIRECT_MESSAGE = "send_direct_message"
    NAVIGATE_TO_GROUP = "navigate_to_group"
    MENTION_USER = "mention_user"
    SCHEDULED_MESSAGE = "scheduled_message"
    REPLY_TO_MESSAGE = "reply_to_message"


@dataclass
class Action:
    """操作指令"""
    action_type: ActionType
    target: str  # 目标：群组ID、用户ID、URL等
    content: str  # 消息内容
    mentions: List[str] = None  # @提及的用户列表
    delay_seconds: int = 0  # 延迟执行时间（秒）
    repeat_interval: int = 0  # 重复间隔（秒），0表示不重复
    max_repeats: int = 1  # 最大重复次数
    
    @classmethod
    def from_json(cls, json_str: str) -> "Action":
        """从JSON字符串创建Action"""
        data = json.loads(json_str)
        
        # 转换action_type字符串为枚举
        action_type_str = data.get("action_type", "")
        try:
            action_type = ActionType(action_type_str)
        except ValueError:
            raise ValueError(f"无效的操作类型: {action_type_str}")
        
        return cls(
            action_type=action_type,
            target=data.get("target", ""),
            content=data.get("content", ""),
            mentions=data.get("mentions", []),
            delay_seconds=data.get("delay_seconds", 0),
            repeat_interval=data.get("repeat_interval", 0),
            max_repeats=data.get("max_repeats", 1)
        )
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        data = {
            "action_type": self.action_type.value,
            "target": self.target,
            "content": self.content,
            "mentions": self.mentions or [],
            "delay_seconds": self.delay_seconds,
            "repeat_interval": self.repeat_interval,
            "max_repeats": self.max_repeats
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


class MessageScheduler:
    """消息调度器"""
    
    def __init__(self, browser_client):
        """
        初始化消息调度器
        
        Args:
            browser_client: TailChatBrowserClient实例
        """
        self.client = browser_client
        self.scheduled_tasks = []
        self.running = False
        self.task_queue = asyncio.Queue()
        
        # 注册默认的消息处理器
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """注册默认的操作处理器"""
        self.handlers = {
            ActionType.SEND_GROUP_MESSAGE: self._handle_send_group_message,
            ActionType.SEND_DIRECT_MESSAGE: self._handle_send_direct_message,
            ActionType.NAVIGATE_TO_GROUP: self._handle_navigate_to_group,
            ActionType.MENTION_USER: self._handle_mention_user,
            ActionType.SCHEDULED_MESSAGE: self._handle_scheduled_message,
            ActionType.REPLY_TO_MESSAGE: self._handle_reply_to_message,
        }
    
    async def _handle_send_group_message(self, action: Action) -> bool:
        """处理发送群组消息"""
        try:
            logger.info(f"发送群组消息到 {action.target}: {action.content[:50]}...")
            
            # 构建完整的消息内容（包含@提及）
            full_content = action.content
            if action.mentions:
                mentions_str = " ".join([f"@{user}" for user in action.mentions])
                full_content = f"{mentions_str}\n{full_content}"
            
            # 发送消息
            success = await self.client.send_message(action.target, full_content)
            if success:
                logger.info(f"群组消息发送成功: {action.target}")
            else:
                logger.error(f"群组消息发送失败: {action.target}")
            
            return success
            
        except Exception as e:
            logger.error(f"发送群组消息失败: {e}")
            return False
    
    async def _handle_send_direct_message(self, action: Action) -> bool:
        """处理发送私信"""
        try:
            logger.info(f"发送私信给 {action.target}: {action.content[:50]}...")
            
            # 发送私信
            success = await self.client.send_direct_message(action.target, action.content)
            if success:
                logger.info(f"私信发送成功: {action.target}")
            else:
                logger.error(f"私信发送失败: {action.target}")
            
            return success
            
        except Exception as e:
            logger.error(f"发送私信失败: {e}")
            return False
    
    async def _handle_navigate_to_group(self, action: Action) -> bool:
        """处理导航到群组"""
        try:
            logger.info(f"导航到群组: {action.target}")
            
            # 如果target是URL，直接导航
            if action.target.startswith("http"):
                await self.client.page.goto(action.target, wait_until="networkidle")
                await asyncio.sleep(3)  # 等待页面加载
                logger.info(f"已导航到群组URL: {action.target}")
                return True
            else:
                # 假设target是群组ID，构建URL
                base_url = self.client.config.api_url.rstrip("/")
                group_url = f"{base_url}/main/group/{action.target}"
                await self.client.page.goto(group_url, wait_until="networkidle")
                await asyncio.sleep(3)
                logger.info(f"已导航到群组: {group_url}")
                return True
                
        except Exception as e:
            logger.error(f"导航到群组失败: {e}")
            return False
    
    async def _handle_mention_user(self, action: Action) -> bool:
        """处理@用户"""
        try:
            logger.info(f"在群组 {action.target} 中@用户: {action.mentions}")
            
            # 构建@消息
            if not action.mentions:
                logger.warning("没有指定要@的用户")
                return False
            
            mentions_str = " ".join([f"@{user}" for user in action.mentions])
            message_content = f"{mentions_str} {action.content}"
            
            # 发送消息
            success = await self.client.send_message(action.target, message_content)
            if success:
                logger.info(f"@消息发送成功: {action.target}")
            else:
                logger.error(f"@消息发送失败: {action.target}")
            
            return success
            
        except Exception as e:
            logger.error(f"发送@消息失败: {e}")
            return False
    
    async def _handle_scheduled_message(self, action: Action) -> bool:
        """处理定时消息"""
        try:
            logger.info(f"安排定时消息: {action.content[:50]}... (延迟: {action.delay_seconds}秒)")
            
            # 创建定时任务
            async def scheduled_task():
                if action.delay_seconds > 0:
                    await asyncio.sleep(action.delay_seconds)
                
                # 根据target类型决定发送方式
                if "/group/" in action.target or action.target.startswith("http"):
                    # 群组消息
                    return await self._handle_send_group_message(action)
                else:
                    # 假设是用户ID，发送私信
                    return await self._handle_send_direct_message(action)
            
            # 启动定时任务
            task = asyncio.create_task(scheduled_task())
            self.scheduled_tasks.append(task)
            
            return True
            
        except Exception as e:
            logger.error(f"安排定时消息失败: {e}")
            return False
    
    async def _handle_reply_to_message(self, action: Action) -> bool:
        """处理回复消息"""
        try:
            logger.info(f"回复消息: {action.content[:50]}...")
            
            # 这里需要根据具体的消息ID来回复
            # 简化处理：直接发送消息到目标
            if "/group/" in action.target or action.target.startswith("http"):
                return await self._handle_send_group_message(action)
            else:
                return await self._handle_send_direct_message(action)
                
        except Exception as e:
            logger.error(f"回复消息失败: {e}")
            return False
    
    async def execute_action(self, action: Action) -> bool:
        """执行单个操作"""
        try:
            logger.info(f"执行操作: {action.action_type.value}")
            
            # 查找处理器
            handler = self.handlers.get(action.action_type)
            if not handler:
                logger.error(f"未知的操作类型: {action.action_type}")
                return False
            
            # 如果有延迟，先等待
            if action.delay_seconds > 0:
                logger.info(f"等待 {action.delay_seconds} 秒后执行...")
                await asyncio.sleep(action.delay_seconds)
            
            # 执行操作
            result = await handler(action)
            
            # 如果需要重复执行
            if action.repeat_interval > 0 and action.max_repeats > 1:
                await self._schedule_repeated_action(action)
            
            return result
            
        except Exception as e:
            logger.error(f"执行操作失败: {e}")
            return False
    
    async def _schedule_repeated_action(self, action: Action):
        """安排重复执行的操作"""
        async def repeat_task(original_action: Action, remaining_repeats: int):
            await asyncio.sleep(original_action.repeat_interval)
            
            if remaining_repeats > 0:
                logger.info(f"重复执行操作 ({remaining_repeats}次剩余)")
                
                # 创建新的action（减少重复次数）
                new_action = Action(
                    action_type=original_action.action_type,
                    target=original_action.target,
                    content=original_action.content,
                    mentions=original_action.mentions,
                    delay_seconds=0,
                    repeat_interval=original_action.repeat_interval,
                    max_repeats=remaining_repeats - 1
                )
                
                # 执行操作
                await self.execute_action(new_action)
        
        # 启动重复任务
        task = asyncio.create_task(repeat_task(action, action.max_repeats - 1))
        self.scheduled_tasks.append(task)
    
    async def execute_json_instruction(self, json_instruction: str) -> bool:
        """执行JSON指令"""
        try:
            # 解析JSON指令
            data = json.loads(json_instruction)
            
            # 支持单个操作或操作列表
            if isinstance(data, list):
                # 多个操作
                results = []
                for item in data:
                    action = Action.from_json(json.dumps(item))
                    result = await self.execute_action(action)
                    results.append(result)
                
                # 所有操作都成功才算成功
                return all(results)
            else:
                # 单个操作
                action = Action.from_json(json_instruction)
                return await self.execute_action(action)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return False
        except Exception as e:
            logger.error(f"执行JSON指令失败: {e}")
            return False
    
    async def start(self):
        """启动调度器"""
        self.running = True
        logger.info("消息调度器已启动")
        
        # 启动任务处理循环
        asyncio.create_task(self._process_task_queue())
    
    async def stop(self):
        """停止调度器"""
        self.running = False
        logger.info("消息调度器正在停止...")
        
        # 取消所有计划任务
        for task in self.scheduled_tasks:
            task.cancel()
        
        # 清空队列
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        logger.info("消息调度器已停止")
    
    async def _process_task_queue(self):
        """处理任务队列"""
        while self.running:
            try:
                # 从队列获取任务
                action = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # 执行任务
                await self.execute_action(action)
                
                # 标记任务完成
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # 超时，继续循环
                continue
            except asyncio.CancelledError:
                # 任务被取消
                break
            except Exception as e:
                logger.error(f"处理任务队列失败: {e}")
    
    def schedule_action(self, action: Action):
        """安排操作到队列"""
        self.task_queue.put_nowait(action)
    
    def schedule_json_instruction(self, json_instruction: str):
        """安排JSON指令到队列"""
        try:
            action = Action.from_json(json_instruction)
            self.schedule_action(action)
        except Exception as e:
            logger.error(f"安排JSON指令失败: {e}")


# 示例JSON指令
EXAMPLE_INSTRUCTIONS = {
    "发送群组消息": '''
    {
        "action_type": "send_group_message",
        "target": "68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
        "content": "大家好！我是TailChat AI助手，很高兴加入这个群组！",
        "mentions": ["用户1", "用户2"],
        "delay_seconds": 5
    }
    ''',
    
    "发送私信": '''
    {
        "action_type": "send_direct_message",
        "target": "user123",
        "content": "你好！我是TailChat AI助手，有什么可以帮你的吗？",
        "delay_seconds": 10
    }
    ''',
    
    "导航到群组": '''
    {
        "action_type": "navigate_to_group",
        "target": "https://chat.mk49.cyou/main/group/68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
        "content": "",
        "delay_seconds": 0
    }
    ''',
    
    "@用户聊天": '''
    {
        "action_type": "mention_user",
        "target": "68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
        "content": "有什么问题需要我帮忙解决吗？",
        "mentions": ["张三", "李四"],
        "delay_seconds": 15
    }
    ''',
    
    "定时消息": '''
    {
        "action_type": "scheduled_message",
        "target": "68a2be8fad67a2438ad9dbd4/68a2be8fad67a2438ad9dbd3",
        "content": "每日提醒：记得完成今天的任务哦！",
        "delay_seconds": 60,
        "repeat_interval": 86400,
        "max_repeats": 7
    }
    '''
}


async def test_scheduler():
    """测试调度器"""
    from browser_client import TailChatBrowserClient
    
    # 创建客户端
    client = TailChatBrowserClient()
    
    # 创建调度器
    scheduler = MessageScheduler(client)
    
    # 启动调度器
    await scheduler.start()
    
    # 测试各种指令
    print("测试消息调度系统...")
    print("=" * 60)
    
    for name, instruction in EXAMPLE_INSTRUCTIONS.items():
        print(f"\n测试: {name}")
        print(f"指令: {instruction[:100]}...")
        
        success = await scheduler.execute_json_instruction(instruction)
        if success:
            print(f"✅ {name} 测试通过")
        else:
            print(f"❌ {name} 测试失败")
        
        await asyncio.sleep(2)  # 等待一下
    
    # 停止调度器
    await scheduler.stop()
    
    print("\n" + "=" * 60)
    print("消息调度系统测试完成")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_scheduler())