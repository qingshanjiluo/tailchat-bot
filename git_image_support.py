"""
Git仓库图片支持模块
可以从Git仓库获取和发送图片
"""

import os
import re
import shutil
import tempfile
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from loguru import logger

from config import config


class GitImageSupport:
    """Git仓库图片支持"""

    def __init__(self):
        self.config = config.git
        self.temp_dir = None
        self.repo_cloned = False

        # 支持的Git平台
        self.git_platforms = {
            "github.com": {
                "raw_url": "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}",
                "api_url": "https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            },
            "gitlab.com": {
                "raw_url": "https://gitlab.com/{owner}/{repo}/-/raw/{branch}/{path}",
                "api_url": "https://gitlab.com/api/v4/projects/{owner}%2F{repo}/repository/files/{path}?ref={branch}",
            },
            "gitee.com": {
                "raw_url": "https://gitee.com/{owner}/{repo}/raw/{branch}/{path}",
                "api_url": "https://gitee.com/api/v5/repos/{owner}/{repo}/contents/{path}?ref={branch}",
            },
        }

        # 支持的图片格式
        self.supported_formats = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".bmp",
            ".svg",
        ]

        logger.info("Git图片支持模块初始化完成")

    def parse_git_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        解析Git仓库URL

        Args:
            url: Git仓库URL

        Returns:
            解析后的信息字典，包含owner, repo, platform等
        """
        if not url:
            return None

        try:
            parsed = urlparse(url)
            hostname = parsed.netloc.lower()

            # 提取owner和repo
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo = path_parts[1].replace(".git", "")

                # 确定平台
                platform = None
                for platform_host in self.git_platforms:
                    if platform_host in hostname:
                        platform = platform_host
                        break

                if not platform:
                    # 默认使用github格式
                    platform = "github.com"

                return {
                    "platform": platform,
                    "owner": owner,
                    "repo": repo,
                    "hostname": hostname,
                    "url": url,
                }

        except Exception as e:
            logger.error(f"解析Git URL失败: {e}")

        return None

    def get_image_url(self, image_path: str, repo_info: Dict = None) -> Optional[str]:
        """
        获取图片的原始URL

        Args:
            image_path: 图片路径（相对路径）
            repo_info: 仓库信息，如果为None则使用配置中的仓库

        Returns:
            图片的原始URL
        """
        try:
            if not repo_info:
                if not self.config.repo_url:
                    logger.error("未配置Git仓库URL")
                    return None

                repo_info = self.parse_git_url(self.config.repo_url)
                if not repo_info:
                    return None

            platform = repo_info["platform"]
            owner = repo_info["owner"]
            repo = repo_info["repo"]
            branch = self.config.repo_branch

            # 清理图片路径
            image_path = image_path.strip("/")
            if self.config.image_path:
                base_path = self.config.image_path.strip("/")
                if not image_path.startswith(base_path):
                    image_path = f"{base_path}/{image_path}"

            # 构建原始URL
            if platform in self.git_platforms:
                template = self.git_platforms[platform]["raw_url"]
                return template.format(
                    owner=owner, repo=repo, branch=branch, path=image_path
                )
            else:
                # 通用格式
                return f"https://{platform}/{owner}/{repo}/raw/{branch}/{image_path}"

        except Exception as e:
            logger.error(f"获取图片URL失败: {e}")
            return None

    def list_images_in_repo(self, path: str = "") -> List[Dict[str, str]]:
        """
        列出仓库中的图片

        Args:
            path: 子目录路径

        Returns:
            图片信息列表
        """
        if not self.config.repo_url:
            logger.error("未配置Git仓库URL")
            return []

        repo_info = self.parse_git_url(self.config.repo_url)
        if not repo_info:
            return []

        platform = repo_info["platform"]
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        branch = self.config.repo_branch

        try:
            # 构建API URL
            if platform == "github.com":
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
                response = requests.get(api_url, timeout=10)

                if response.status_code == 200:
                    items = response.json()
                    images = []

                    for item in items:
                        if item.get("type") == "file":
                            file_name = item.get("name", "")
                            file_ext = os.path.splitext(file_name)[1].lower()

                            if file_ext in self.supported_formats:
                                images.append(
                                    {
                                        "name": file_name,
                                        "path": item.get("path", ""),
                                        "url": item.get("download_url", ""),
                                        "size": item.get("size", 0),
                                    }
                                )

                    return images

            # 其他平台暂不支持API列表
            logger.warning(f"平台 {platform} 的API列表功能暂未实现")
            return []

        except Exception as e:
            logger.error(f"列出仓库图片失败: {e}")
            return []

    def search_images(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索仓库中的图片

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的图片列表
        """
        all_images = self.list_images_in_repo(self.config.image_path)

        if not keyword:
            return all_images

        keyword_lower = keyword.lower()
        matched_images = []

        for image in all_images:
            name = image.get("name", "").lower()
            path = image.get("path", "").lower()

            if keyword_lower in name or keyword_lower in path:
                matched_images.append(image)

        return matched_images

    def get_random_image(self) -> Optional[Dict[str, str]]:
        """
        获取随机图片

        Returns:
            随机图片信息
        """
        images = self.list_images_in_repo(self.config.image_path)

        if not images:
            return None

        import random

        return random.choice(images)

    def send_image_message(
        self, image_info: Dict, converse_id: str, caption: str = ""
    ) -> bool:
        """
        发送图片消息

        Args:
            image_info: 图片信息
            converse_id: 会话ID
            caption: 图片说明

        Returns:
            是否发送成功
        """
        try:
            from tailchat_client import client as tailchat_client

            image_url = image_info.get("url")
            if not image_url:
                logger.error("图片URL为空")
                return False

            # 构建消息内容
            message = f"![{image_info.get('name', '图片')}]({image_url})"

            if caption:
                message = f"{caption}\n\n{message}"

            # 发送消息
            return tailchat_client.send_message(converse_id, message)

        except Exception as e:
            logger.error(f"发送图片消息失败: {e}")
            return False

    def create_image_catalog_message(
        self, images: List[Dict], title: str = "图片库"
    ) -> str:
        """
        创建图片目录消息

        Args:
            images: 图片列表
            title: 标题

        Returns:
            目录消息
        """
        if not images:
            return "未找到图片"

        message = f"## {title}\n\n"

        for i, image in enumerate(images[:10]):  # 最多显示10张
            name = image.get("name", "未命名")
            url = image.get("url", "")

            if url:
                message += f"{i+1}. [{name}]({url})\n"
            else:
                message += f"{i+1}. {name}\n"

        if len(images) > 10:
            message += f"\n... 还有 {len(images) - 10} 张图片未显示"

        return message

    def download_image(self, image_url: str, save_path: str = None) -> Optional[str]:
        """
        下载图片到本地

        Args:
            image_url: 图片URL
            save_path: 保存路径，如果为None则使用临时目录

        Returns:
            保存的文件路径
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            if save_path is None:
                # 创建临时目录
                if self.temp_dir is None:
                    self.temp_dir = tempfile.mkdtemp(prefix="tailchat_bot_images_")

                # 从URL提取文件名
                parsed = urlparse(image_url)
                filename = os.path.basename(parsed.path)
                if not filename:
                    filename = f"image_{hash(image_url)}.jpg"

                save_path = os.path.join(self.temp_dir, filename)

            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 保存文件
            with open(save_path, "wb") as f:
                f.write(response.content)

            logger.info(f"图片已下载到: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"下载图片失败: {e}")
            return None

    def cleanup_temp_files(self):
        """清理临时文件"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"已清理临时目录: {self.temp_dir}")
                self.temp_dir = None
            except Exception as e:
                logger.error(f"清理临时目录失败: {e}")

    def validate_image_url(self, image_url: str) -> bool:
        """
        验证图片URL是否有效

        Args:
            image_url: 图片URL

        Returns:
            是否有效
        """
        try:
            # 检查URL格式
            parsed = urlparse(image_url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # 检查文件扩展名
            path = parsed.path.lower()
            for ext in self.supported_formats:
                if path.endswith(ext):
                    return True

            # 对于没有扩展名的URL，尝试HEAD请求检查Content-Type
            try:
                response = requests.head(image_url, timeout=5, allow_redirects=True)
                content_type = response.headers.get("Content-Type", "").lower()

                if "image" in content_type:
                    return True
            except:
                pass

            return False

        except Exception as e:
            logger.error(f"验证图片URL失败: {e}")
            return False

    def get_platform_info(self) -> Dict:
        """获取Git平台信息"""
        return {
            "repo_url": self.config.repo_url,
            "repo_branch": self.config.repo_branch,
            "image_path": self.config.image_path,
            "supported_platforms": list(self.git_platforms.keys()),
            "supported_formats": self.supported_formats,
        }


# 单例实例
git_image_support = GitImageSupport()
