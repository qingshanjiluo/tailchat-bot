"""
配置管理模块
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class TailChatConfig:
    """TailChat 配置"""

    api_url: str
    username: str
    password: str
    use_browser: bool
    headless: bool
    bot_username: str
    bot_avatar: Optional[str]

    @classmethod
    def from_env(cls) -> "TailChatConfig":
        return cls(
            api_url=os.getenv("TAILCHAT_API_URL", "https://chat.mk49.cyou"),
            username=os.getenv("TAILCHAT_USERNAME", ""),
            password=os.getenv("TAILCHAT_PASSWORD", ""),
            use_browser=os.getenv("TAILCHAT_USE_BROWSER", "true").lower() == "true",
            headless=os.getenv("TAILCHAT_HEADLESS", "true").lower() == "true",
            bot_username=os.getenv("TAILCHAT_BOT_USERNAME", "AI助手"),
            bot_avatar=os.getenv("TAILCHAT_BOT_AVATAR"),
        )


@dataclass
class DeepSeekConfig:
    """DeepSeek API 配置"""

    api_key: str
    api_url: str
    model: str

    @classmethod
    def from_env(cls) -> "DeepSeekConfig":
        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            api_url=os.getenv(
                "DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions"
            ),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        )


@dataclass
class BotBehaviorConfig:
    """机器人行为配置"""

    active_hours_start: int
    active_hours_end: int
    auto_reply: bool
    auto_reply_probability: float
    max_message_length: int
    welcome_message: str
    busy_message: str

    @classmethod
    def from_env(cls) -> "BotBehaviorConfig":
        return cls(
            active_hours_start=int(os.getenv("BOT_ACTIVE_HOURS_START", "6")),
            active_hours_end=int(os.getenv("BOT_ACTIVE_HOURS_END", "22")),
            auto_reply=os.getenv("BOT_AUTO_REPLY", "true").lower() == "true",
            auto_reply_probability=float(
                os.getenv("BOT_AUTO_REPLY_PROBABILITY", "0.8")
            ),
            max_message_length=int(os.getenv("BOT_MAX_MESSAGE_LENGTH", "1000")),
            welcome_message=os.getenv(
                "WELCOME_MESSAGE", "你好！我是AI助手，有什么可以帮你的吗？"
            ),
            busy_message=os.getenv(
                "BUSY_MESSAGE", "我现在不在线，请在6:00-22:00之间联系我。"
            ),
        )


@dataclass
class ConversationConfig:
    """对话记录配置"""

    enable_history: bool
    history_path: str
    max_history_messages: int
    save_format: str

    @classmethod
    def from_env(cls) -> "ConversationConfig":
        return cls(
            enable_history=os.getenv("ENABLE_CONVERSATION_HISTORY", "true").lower()
            == "true",
            history_path=os.getenv("CONVERSATION_HISTORY_PATH", "./conversations"),
            max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "50")),
            save_format=os.getenv("CONVERSATION_SAVE_FORMAT", "json"),
        )


@dataclass
class GitConfig:
    """Git仓库配置"""

    repo_url: Optional[str]
    repo_branch: str
    image_path: str

    @classmethod
    def from_env(cls) -> "GitConfig":
        return cls(
            repo_url=os.getenv("GIT_REPO_URL"),
            repo_branch=os.getenv("GIT_REPO_BRANCH", "main"),
            image_path=os.getenv("GIT_IMAGE_PATH", "images/"),
        )


@dataclass
class Config:
    """总配置"""

    tailchat: TailChatConfig
    deepseek: DeepSeekConfig
    behavior: BotBehaviorConfig
    conversation: ConversationConfig
    git: GitConfig

    @classmethod
    def load(cls) -> "Config":
        return cls(
            tailchat=TailChatConfig.from_env(),
            deepseek=DeepSeekConfig.from_env(),
            behavior=BotBehaviorConfig.from_env(),
            conversation=ConversationConfig.from_env(),
            git=GitConfig.from_env(),
        )

    def validate(self) -> bool:
        """验证配置是否有效"""
        errors = []

        if not self.tailchat.username:
            errors.append("TAILCHAT_USERNAME 不能为空")
        if not self.tailchat.password:
            errors.append("TAILCHAT_PASSWORD 不能为空")
        if not self.deepseek.api_key:
            errors.append("DEEPSEEK_API_KEY 不能为空")

        if not 0 <= self.behavior.active_hours_start < 24:
            errors.append("BOT_ACTIVE_HOURS_START 必须在 0-23 之间")
        if not 0 <= self.behavior.active_hours_end < 24:
            errors.append("BOT_ACTIVE_HOURS_END 必须在 0-23 之间")
        if not 0 <= self.behavior.auto_reply_probability <= 1:
            errors.append("BOT_AUTO_REPLY_PROBABILITY 必须在 0-1 之间")

        if errors:
            print("配置错误:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True


# 全局配置实例
config = Config.load()
