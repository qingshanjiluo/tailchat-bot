"""
主动消息发送器模块
"""
import time
import random
import schedule
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from loguru import logger

from config import config
from tailchat_client import client as tailchat_client
from deepseek_client import deepseek_client
from message_processor import processor as message_processor


class ActiveMessageSender:
    """主动消息发送器"""
    
    def __init__(self):
        self.config = config.behavior
        self.tailchat = tailchat_client
        self.deepseek = deepseek_client
        self.processor = message_processor
        
        # 定时任务
        self.scheduler = schedule.Scheduler()
        self.scheduler_thread = None
        self.running = False
        
        # 消息模板
        self.greeting_templates = [
            "大家早上好！🌞 新的一天开始了，有什么需要帮助的吗？",
            "午安！😊 下午的工作/学习还顺利吗？",
            "晚上好！🌙 今天过得怎么样？",
            "周末愉快！🎉 有什么计划吗？",
        ]
        
        self.tip_templates = [
            "💡 小提示: 你可以@我提问，或者使用!help查看所有命令",
            "🤖 提醒: 我支持文本摘要、情感分析、图片描述生成等功能",
            "📚 你知道吗: 我可以记住我们的对话历史，让交流更连贯",
        ]
        
        self.fun_fact_templates = [
            "🎲 趣味知识: 你知道吗？蜜蜂可以识别人类的面孔",
            "🌍 冷知识: 地球上的蚂蚁总重量超过人类总重量",
            "💻 科技趣闻: 第一个计算机病毒是在1983年创建的",
        ]
        
        # 已发送消息记录（避免重复）
        self.sent_messages = {}
        
        logger.info("主动消息发送器初始化完成")
    
    def start(self):
        """启动定时任务"""
        if self.running:
            logger.warning("主动消息发送器已经在运行")
            return
        
        # 注册定时任务
        self._register_scheduled_tasks()
        
        # 启动调度器线程
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("主动消息发送器已启动")
    
    def stop(self):
        """停止定时任务"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("主动消息发送器已停止")
    
    def _run_scheduler(self):
        """运行调度器"""
        while self.running:
            try:
                self.scheduler.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"调度器运行错误: {e}")
                time.sleep(5)
    
    def _register_scheduled_tasks(self):
        """注册定时任务"""
        
        # 每天早上8点发送问候
        self.scheduler.every().day.at("08:00").do(
            self._send_morning_greeting
        )
        
        # 每天中午12点发送午间问候
        self.scheduler.every().day.at("12:00").do(
            self._send_noon_greeting
        )
        
        # 每天晚上20点发送晚间问候
        self.scheduler.every().day.at("20:00").do(
            self._send_evening_greeting
        )
        
        # 每小时发送小提示（随机时间）
        self.scheduler.every().hour.do(
            self._send_random_tip
        )
        
        # 每2小时发送趣味知识（随机时间）
        self.scheduler.every(2).hours.do(
            self._send_fun_fact
        )
        
        # 每天检查活跃用户并发送个性化消息
        self.scheduler.every().day.at("10:00").do(
            self._check_active_users
        )
        
        # 每周一发送周报提醒
        self.scheduler.every().monday.at("09:00").do(
            self._send_weekly_reminder
        )
        
        logger.info(f"已注册 {len(self.scheduler.jobs)} 个定时任务")
    
    def _send_morning_greeting(self):
        """发送早晨问候"""
        if not self._is_active_hours():
            return
        
        message = random.choice([
            "大家早上好！🌞 新的一天开始了，祝大家工作顺利！",
            "早安！☕️ 记得吃早餐哦～",
            "早上好！✨ 今天也是充满希望的一天！",
        ])
        
        self._broadcast_to_active_groups(message)
        logger.info("已发送早晨问候")
    
    def _send_noon_greeting(self):
        """发送午间问候"""
        if not self._is_active_hours():
            return
        
        message = random.choice([
            "午安！🍱 午餐时间到，记得休息一下～",
            "中午好！😊 工作/学习辛苦了！",
            "午休时间到！💤 适当休息有助于提高效率",
        ])
        
        self._broadcast_to_active_groups(message)
        logger.info("已发送午间问候")
    
    def _send_evening_greeting(self):
        """发送晚间问候"""
        if not self._is_active_hours():
            return
        
        message = random.choice([
            "晚上好！🌙 今天过得怎么样？",
            "晚安前的问候！✨ 记得放松一下～",
            "晚上好！📚 今天有什么收获吗？",
        ])
        
        self._broadcast_to_active_groups(message)
        logger.info("已发送晚间问候")
    
    def _send_random_tip(self):
        """发送随机小提示"""
        if not self._is_active_hours():
            return
        
        # 随机决定是否发送（避免太频繁）
        if random.random() < 0.3:  # 30%概率发送
            message = random.choice(self.tip_templates)
            self._broadcast_to_random_group(message)
            logger.info("已发送随机小提示")
    
    def _send_fun_fact(self):
        """发送趣味知识"""
        if not self._is_active_hours():
            return
        
        # 随机决定是否发送
        if random.random() < 0.2:  # 20%概率发送
            message = random.choice(self.fun_fact_templates)
            self._broadcast_to_random_group(message)
            logger.info("已发送趣味知识")
    
    def _check_active_users(self):
        """检查活跃用户并发送个性化消息"""
        if not self._is_active_hours():
            return
        
        # 这里可以实现检查最近活跃用户的逻辑
        # 目前先发送通用消息
        message = "👋 嗨！最近怎么样？有什么我可以帮忙的吗？"
        self._broadcast_to_active_groups(message)
        logger.info("已发送活跃用户检查消息")
    
    def _send_weekly_reminder(self):
        """发送周报提醒"""
        if not self._is_active_hours():
            return
        
        message = "📅 周一提醒：新的一周开始了！祝大家本周工作顺利，收获满满！"
        self._broadcast_to_active_groups(message)
        logger.info("已发送周报提醒")
    
    def _broadcast_to_active_groups(self, message: str):
        """向活跃群组广播消息"""
        # 这里应该实现获取活跃群组的逻辑
        # 目前先记录日志，实际使用时需要实现
        logger.info(f"准备广播消息: {message}")
        
        # 模拟发送到几个群组
        # 在实际应用中，这里应该获取真实的群组ID
        # self.tailchat.send_message(group_id, message)
    
    def _broadcast_to_random_group(self, message: str):
        """向随机群组发送消息"""
        # 这里应该实现获取群组列表并随机选择的逻辑
        # 目前先记录日志
        logger.info(f"准备发送到随机群组: {message}")
    
    def send_custom_broadcast(self, message: str, target_type: str = "all"):
        """
        发送自定义广播消息
        
        Args:
            message: 消息内容
            target_type: 目标类型，可选 "all", "active", "random"
        """
        if not self._is_active_hours():
            logger.warning("非在线时间，不发送广播")
            return False
        
        try:
            if target_type == "all":
                self._broadcast_to_active_groups(message)
            elif target_type == "active":
                self._broadcast_to_active_groups(message)
            elif target_type == "random":
                self._broadcast_to_random_group(message)
            else:
                logger.error(f"未知的目标类型: {target_type}")
                return False
            
            logger.info(f"已发送自定义广播: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"发送自定义广播失败: {e}")
            return False
    
    def send_to_converse(self, converse_id: str, message: str, mentions: List[str] = None):
        """发送消息到指定会话"""
        if not self._is_active_hours():
            logger.warning("非在线时间，不发送消息")
            return False
        
        try:
            success = self.tailchat.send_message(converse_id, message, mentions)
            if success:
                logger.info(f"已发送消息到会话 {converse_id}: {message[:50]}...")
            return success
            
        except Exception as e:
            logger.error(f"发送消息到会话失败: {e}")
            return False
    
    def send_ai_generated_message(self, topic: str, target_converse_id: Optional[str] = None):
        """发送AI生成的消息"""
        if not self._is_active_hours():
            logger.warning("非在线时间，不发送AI生成消息")
            return False
        
        try:
            # 使用DeepSeek生成关于主题的消息
            prompt = f"请生成一段关于{topic}的友好、有趣的聊天消息，用于群组聊天中。保持简短自然。"
            
            response = self.deepseek.chat(
                message=prompt,
                system_prompt="你是一个友好的聊天机器人。请生成自然、友好的聊天消息，适合在群组中发送。"
            )
            
            if not response["success"]:
                logger.error("生成AI消息失败")
                return False
            
            message = response["reply"]
            
            if target_converse_id:
                # 发送到指定会话
                return self.send_to_converse(target_converse_id, message)
            else:
                # 广播到活跃群组
                return self.send_custom_broadcast(message, "active")
                
        except Exception as e:
            logger.error(f"发送AI生成消息失败: {e}")
            return False
    
    def _is_active_hours(self) -> bool:
        """检查是否在在线时间内"""
        now = datetime.now()
        current_hour = now.hour
        
        if self.config.active_hours_start <= self.config.active_hours_end:
            # 正常时间范围，如 6:00-22:00
            return self.config.active_hours_start <= current_hour < self.config.active_hours_end
        else:
            # 跨天时间范围，如 22:00-6:00
            return current_hour >= self.config.active_hours_start or current_hour < self.config.active_hours_end
    
    def get_schedule_info(self) -> Dict:
        """获取调度器信息"""
        jobs = []
        for job in self.scheduler.jobs:
            jobs.append({
                "function": job.job_func.__name__,
                "next_run": str(job.next_run) if job.next_run else None,
                "interval": str(job.interval) if hasattr(job, 'interval') else None
            })
        
        return {
            "running": self.running,
            "job_count": len(jobs),
            "jobs": jobs
        }


# 单例发送器
active_sender = ActiveMessageSender()