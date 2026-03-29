"""
富媒体消息支持模块
支持表情、图片、网址、文件等
"""
import re
import random
import os
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
from loguru import logger

from config import config


class RichMediaSupport:
    """富媒体消息支持"""
    
    def __init__(self):
        # 表情符号库
        self.emojis = {
            "happy": ["😊", "😄", "😁", "😂", "🤣", "😍", "🥰", "😘"],
            "sad": ["😢", "😭", "😔", "😞", "😟", "🙁", "☹️"],
            "angry": ["😠", "😡", "🤬", "👿", "💢"],
            "surprised": ["😲", "😳", "🤯", "😱", "😨"],
            "love": ["❤️", "💕", "💖", "💗", "💓", "💞", "💘"],
            "weather": ["☀️", "⛅", "☁️", "🌧️", "⛈️", "🌩️", "❄️", "🌪️"],
            "animals": ["🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼"],
            "food": ["🍎", "🍕", "🍔", "🍟", "🍦", "🍩", "🍫", "🍿"],
            "objects": ["📱", "💻", "📷", "🎮", "📚", "✏️", "🎵", "🎬"],
            "symbols": ["✅", "❌", "⚠️", "❗", "❓", "💡", "⭐", "🎯"],
        }
        
        # 图片URL模板
        self.image_templates = {
            "cat": "https://cataas.com/cat",
            "dog": "https://dog.ceo/api/breeds/image/random",
            "placeholder": "https://via.placeholder.com/400x300",
            "unsplash": "https://source.unsplash.com/random/800x600",
            "picsum": "https://picsum.photos/800/600",
        }
        
        # 支持的图片格式
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        
        # 支持的视频格式
        self.supported_video_formats = ['.mp4', '.webm', '.mov', '.avi']
        
        # 支持的文档格式
        self.supported_doc_formats = ['.pdf', '.doc', '.docx', '.txt', '.md', '.csv', '.xlsx']
        
        logger.info("富媒体支持模块初始化完成")
    
    def add_emojis(self, text: str, emotion: str = "happy", count: int = 1) -> str:
        """
        为文本添加表情符号
        
        Args:
            text: 原始文本
            emotion: 情感类型
            count: 添加的表情数量
            
        Returns:
            添加了表情的文本
        """
        if emotion not in self.emojis:
            emotion = "happy"
        
        emoji_list = self.emojis[emotion]
        selected_emojis = random.sample(emoji_list, min(count, len(emoji_list)))
        
        # 随机决定表情添加位置
        if random.random() > 0.5:
            # 添加到开头
            return f"{''.join(selected_emojis)} {text}"
        else:
            # 添加到结尾
            return f"{text} {''.join(selected_emojis)}"
    
    def generate_image_url(self, category: str = "random") -> str:
        """
        生成图片URL
        
        Args:
            category: 图片类别
            
        Returns:
            图片URL
        """
        if category in self.image_templates:
            return self.image_templates[category]
        elif category == "random":
            # 随机选择一个类别
            random_category = random.choice(list(self.image_templates.keys()))
            return self.image_templates[random_category]
        else:
            # 使用unsplash搜索
            return f"https://source.unsplash.com/random/800x600/?{category}"
    
    def format_url_message(self, url: str, title: str = "") -> str:
        """
        格式化URL消息
        
        Args:
            url: 网址
            title: 链接标题
            
        Returns:
            格式化后的消息
        """
        if not title:
            # 从URL提取域名作为标题
            parsed = urlparse(url)
            title = parsed.netloc or url
        
        return f"[{title}]({url})"
    
    def create_rich_message(self, 
                           text: str, 
                           include_emoji: bool = True,
                           include_image: bool = False,
                           image_category: str = "random",
                           include_links: List[str] = None) -> str:
        """
        创建富媒体消息
        
        Args:
            text: 文本内容
            include_emoji: 是否包含表情
            include_image: 是否包含图片
            image_category: 图片类别
            include_links: 包含的链接列表
            
        Returns:
            富媒体消息
        """
        message_parts = []
        
        # 添加图片（如果有）
        if include_image:
            image_url = self.generate_image_url(image_category)
            message_parts.append(f"![图片]({image_url})")
        
        # 添加文本
        if include_emoji:
            # 随机选择情感
            emotions = list(self.emojis.keys())
            emotion = random.choice(emotions)
            formatted_text = self.add_emojis(text, emotion, random.randint(1, 2))
            message_parts.append(formatted_text)
        else:
            message_parts.append(text)
        
        # 添加链接（如果有）
        if include_links:
            links_section = "\n\n相关链接:\n"
            for link in include_links:
                links_section += f"- {self.format_url_message(link)}\n"
            message_parts.append(links_section)
        
        return "\n\n".join(message_parts)
    
    def extract_urls(self, text: str) -> List[str]:
        """
        从文本中提取URL
        
        Args:
            text: 文本
            
        Returns:
            URL列表
        """
        # 简单的URL正则匹配
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text)
        
        # 确保URL以http://或https://开头
        formatted_urls = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            formatted_urls.append(url)
        
        return formatted_urls
    
    def is_image_url(self, url: str) -> bool:
        """
        检查URL是否是图片
        
        Args:
            url: 网址
            
        Returns:
            是否是图片
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for ext in self.supported_image_formats:
            if path.endswith(ext):
                return True
        
        # 检查常见图片域名
        image_domains = ['i.imgur.com', 'imgur.com', 'i.redd.it', 'cdn.discordapp.com',
                        'images.unsplash.com', 'picsum.photos', 'cataas.com']
        if parsed.netloc in image_domains:
            return True
        
        return False
    
    def is_video_url(self, url: str) -> bool:
        """
        检查URL是否是视频
        
        Args:
            url: 网址
            
        Returns:
            是否是视频
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for ext in self.supported_video_formats:
            if path.endswith(ext):
                return True
        
        return False
    
    def is_document_url(self, url: str) -> bool:
        """
        检查URL是否是文档
        
        Args:
            url: 网址
            
        Returns:
            是否是文档
        """
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        for ext in self.supported_doc_formats:
            if path.endswith(ext):
                return True
        
        return False
    
    def analyze_media_content(self, text: str) -> Dict[str, List[str]]:
        """
        分析文本中的媒体内容
        
        Args:
            text: 文本
            
        Returns:
            媒体内容分类
        """
        urls = self.extract_urls(text)
        
        result = {
            "urls": urls,
            "images": [],
            "videos": [],
            "documents": [],
            "other_urls": []
        }
        
        for url in urls:
            if self.is_image_url(url):
                result["images"].append(url)
            elif self.is_video_url(url):
                result["videos"].append(url)
            elif self.is_document_url(url):
                result["documents"].append(url)
            else:
                result["other_urls"].append(url)
        
        return result
    
    def create_media_summary(self, text: str) -> str:
        """
        创建媒体内容摘要
        
        Args:
            text: 文本
            
        Returns:
            媒体摘要
        """
        media = self.analyze_media_content(text)
        
        if not media["urls"]:
            return "未检测到媒体内容"
        
        summary_parts = ["检测到媒体内容:"]
        
        if media["images"]:
            summary_parts.append(f"📷 图片: {len(media['images'])}张")
            # 显示前3张图片
            for i, img in enumerate(media["images"][:3]):
                summary_parts.append(f"  {i+1}. {self.format_url_message(img)}")
        
        if media["videos"]:
            summary_parts.append(f"🎬 视频: {len(media['videos'])}个")
        
        if media["documents"]:
            summary_parts.append(f"📄 文档: {len(media['documents'])}个")
        
        if media["other_urls"]:
            summary_parts.append(f"🔗 其他链接: {len(media['other_urls'])}个")
        
        return "\n".join(summary_parts)
    
    def enhance_message_with_media(self, text: str, original_message: str = "") -> str:
        """
        用媒体内容增强消息
        
        Args:
            text: 要发送的文本
            original_message: 原始消息（用于分析媒体）
            
        Returns:
            增强后的消息
        """
        if not original_message:
            return text
        
        media = self.analyze_media_content(original_message)
        
        # 如果有图片，在回复中提及
        if media["images"]:
            if len(media["images"]) == 1:
                text = f"看到了你分享的图片！\n\n{text}"
            else:
                text = f"看到了你分享的{len(media['images'])}张图片！\n\n{text}"
        
        # 如果有视频，在回复中提及
        if media["videos"]:
            text = f"看到了你分享的视频！\n\n{text}"
        
        # 随机添加表情
        if random.random() > 0.5:
            text = self.add_emojis(text, "happy", 1)
        
        return text
    
    def get_random_emoji(self, category: str = None) -> str:
        """
        获取随机表情
        
        Args:
            category: 表情类别
            
        Returns:
            表情符号
        """
        if category and category in self.emojis:
            return random.choice(self.emojis[category])
        else:
            # 从所有表情中随机选择
            all_emojis = []
            for emoji_list in self.emojis.values():
                all_emojis.extend(emoji_list)
            return random.choice(all_emojis)
    
    def create_welcome_message(self, username: str = "朋友") -> str:
        """
        创建欢迎消息
        
        Args:
            username: 用户名
            
        Returns:
            欢迎消息
        """
        welcome_templates = [
            f"👋 欢迎 {username}！{self.get_random_emoji('happy')}",
            f"🎉 {username}，欢迎加入！{self.get_random_emoji('happy')}",
            f"✨ 你好 {username}！很高兴见到你！{self.get_random_emoji('love')}",
            f"🌟 {username}，欢迎！有什么需要帮助的吗？{self.get_random_emoji('happy')}",
        ]
        
        message = random.choice(welcome_templates)
        
        # 50%概率添加图片
        if random.random() > 0.5:
            image_url = self.generate_image_url("welcome")
            message = f"{message}\n\n![欢迎图片]({image_url})"
        
        return message


# 单例实例
rich_media = RichMediaSupport()