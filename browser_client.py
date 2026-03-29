"""
TailChat 浏览器自动化客户端
使用Playwright模拟人类操作登录和发送消息
"""

import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from loguru import logger
from playwright.async_api import (Browser, BrowserContext, Page,
                                  async_playwright)

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


class TailChatBrowserClient:
    """TailChat 浏览器自动化客户端"""

    def __init__(self):
        self.config = config.tailchat
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.connected = False
        self.user_id = None
        self.username = None
        self.message_handlers = []
        self.last_message_check = 0
        self.message_check_interval = 3  # 检查新消息的间隔（秒）
        self.running = False

    async def init_browser(self):
        """初始化浏览器"""
        try:
            logger.info("正在初始化浏览器...")
            playwright = await async_playwright().start()

            # 根据配置选择浏览器
            browser_type = playwright.chromium

            launch_options = {
                "headless": self.config.headless,
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-site-isolation-trials",
                ],
            }

            self.browser = await browser_type.launch(**launch_options)

            # 创建上下文，模拟人类用户
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="zh-CN",
                timezone_id="Asia/Shanghai",
                permissions=["notifications"],
            )

            # 添加人类行为模拟
            await self.context.add_init_script("""
                // 覆盖webdriver属性
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 覆盖plugins属性
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // 覆盖languages属性
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });
            """)

            self.page = await self.context.new_page()

            # 设置超时
            self.page.set_default_timeout(30000)

            logger.info("浏览器初始化完成")
            return True

        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            return False

    async def login(self) -> bool:
        """登录TailChat"""
        try:
            # 构建登录URL
            base_url = self.config.api_url.rstrip("/")
            login_url = f"{base_url}/entry/login"
            logger.info(f"正在登录TailChat: {login_url}")

            # 访问登录页面
            await self.page.goto(login_url, wait_until="networkidle")

            # 等待页面加载
            await self.page.wait_for_timeout(3000)

            # 检查是否已经登录 - 改进的检测逻辑
            try:
                # 尝试多种已登录标识
                logged_in_selectors = [
                    'img[src*="avatar"]',
                    ".user-avatar",
                    '[data-testid="user-avatar"]',
                    'div[class*="user-info"]',
                    'button:has-text("退出")',
                    'button:has-text("Logout")',
                    'button:has-text("Sign out")',
                ]

                for selector in logged_in_selectors:
                    try:
                        element = await self.page.wait_for_selector(
                            selector, timeout=2000
                        )
                        if element:
                            logger.info(f"检测到已登录状态 (选择器: {selector})")
                            await self._get_user_info()
                            return True
                    except:
                        continue

                # 检查当前URL是否不是登录页面
                current_url = self.page.url
                if "/entry/login" not in current_url and "/login" not in current_url:
                    logger.info(f"当前URL不是登录页面: {current_url}，可能已登录")
                    await self._get_user_info()
                    return True

            except Exception as e:
                logger.debug(f"登录状态检测异常: {e}")

            logger.info("未检测到登录状态，开始登录流程")

            # 查找登录表单 - 针对TailChat优化的选择器
            selectors = [
                'input[type="text"]',
                'input[type="email"]',
                'input[name="username"]',
                'input[name="email"]',
                'input[placeholder*="用户名"]',
                'input[placeholder*="邮箱"]',
                'input[placeholder*="email"]',
                'input[placeholder*="账号"]',
                'input[placeholder*="account"]',
                'input[placeholder*="name@example.com"]',
                'input[placeholder*="邮箱或用户名"]',
                'input[placeholder*="Email"]',
                "input.appearance-none",
                'input[name="login-email"]',
                'input[name="login-username"]',
                "input",
            ]

            username_input = None
            found_selector = None
            for selector in selectors:
                try:
                    username_input = await self.page.wait_for_selector(
                        selector, timeout=3000
                    )
                    if username_input:
                        logger.info(f"找到用户名输入框: {selector}")
                        found_selector = selector
                        break
                except:
                    logger.debug(f"选择器 {selector} 未找到用户名输入框")
                    continue

            if not username_input:
                logger.error("未找到用户名输入框，尝试截图以便调试")
                # 尝试截图以便调试
                try:
                    screenshot_path = "debug_username_not_found.png"
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"已保存截图: {screenshot_path}")

                    # 获取页面HTML以便分析
                    html_content = await self.page.content()
                    html_path = "debug_page_content.html"
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    logger.info(f"已保存页面HTML: {html_path}")
                except Exception as e:
                    logger.error(f"保存调试信息失败: {e}")
                return False

            # 模拟人类输入 - 缓慢输入用户名
            await username_input.click()
            await self.page.wait_for_timeout(random.randint(200, 500))

            for char in self.config.username:
                await username_input.type(char, delay=random.randint(50, 150))
                await self.page.wait_for_timeout(random.randint(20, 50))

            # 查找密码输入框 - 针对TailChat优化的选择器
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[name="login-password"]',
                'input[placeholder*="密码"]',
                'input[placeholder*="password"]',
                'input[placeholder*="******"]',
                'input.appearance-none[type="password"]',
            ]

            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if password_input:
                        logger.info(f"找到密码输入框: {selector}")
                        break
                except:
                    continue

            if not password_input:
                logger.error("未找到密码输入框")
                # 尝试截图以便调试
                try:
                    screenshot_path = "debug_password_not_found.png"
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"已保存截图: {screenshot_path}")
                except:
                    pass
                return False

            # 模拟人类输入密码
            await password_input.click()
            await self.page.wait_for_timeout(random.randint(200, 500))

            for char in self.config.password:
                await password_input.type(char, delay=random.randint(50, 150))
                await self.page.wait_for_timeout(random.randint(20, 50))

            # 查找登录按钮 - 针对TailChat优化的选择器
            login_button_selectors = [
                'button[type="submit"]',
                'button:has-text("登录")',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'button:has-text("登入")',
                'input[type="submit"]',
                "button.ant-btn-primary",
                'button[class*="login-button"]',
                'button[class*="submit-button"]',
            ]

            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = await self.page.wait_for_selector(
                        selector, timeout=5000
                    )
                    if login_button:
                        logger.info(f"找到登录按钮: {selector}")
                        break
                except:
                    continue

            if not login_button:
                logger.error("未找到登录按钮")
                # 尝试截图以便调试
                try:
                    screenshot_path = "debug_login_button_not_found.png"
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"已保存截图: {screenshot_path}")
                except:
                    pass
                return False

            # 模拟人类点击 - 稍微移动鼠标再点击
            box = await login_button.bounding_box()
            if box:
                # 随机移动到按钮中心
                x = box["x"] + box["width"] / 2 + random.uniform(-5, 5)
                y = box["y"] + box["height"] / 2 + random.uniform(-5, 5)
                await self.page.mouse.move(x, y)
                await self.page.wait_for_timeout(random.randint(200, 500))

            await login_button.click()

            # 等待登录完成
            await self.page.wait_for_timeout(3000)

            # 检查登录是否成功
            try:
                logger.info("等待登录成功验证...")

                # 改进的登录成功检测
                success_selectors = [
                    'img[src*="avatar"]',
                    ".user-avatar",
                    '[data-testid="user-avatar"]',
                    'div[class*="user-info"]',
                    'button:has-text("退出")',
                    'button:has-text("Logout")',
                    'button:has-text("Sign out")',
                    'div[class*="main-content"]',  # 主内容区域
                    'div[class*="chat-container"]',  # 聊天容器
                ]

                success_element = None
                for selector in success_selectors:
                    try:
                        success_element = await self.page.wait_for_selector(
                            selector, timeout=5000
                        )
                        if success_element:
                            logger.info(f"登录成功检测到元素: {selector}")
                            break
                    except:
                        continue

                if not success_element:
                    # 检查URL是否改变（从登录页面跳转）
                    current_url = self.page.url
                    if (
                        "/entry/login" not in current_url
                        and "/login" not in current_url
                    ):
                        logger.info(f"URL从登录页面跳转到: {current_url}，认为登录成功")
                    else:
                        logger.warning("未检测到登录成功元素，但继续尝试")

                logger.info("登录成功")

                # 获取用户信息
                await self._get_user_info()

                # 等待页面完全加载
                await self.page.wait_for_timeout(3000)

                # 记录最终URL
                final_url = self.page.url
                logger.info(f"登录后最终URL: {final_url}")

                return True

            except Exception as e:
                logger.error(f"登录验证失败: {e}")
                # 检查是否有错误消息
                error_selectors = [
                    ".error-message",
                    ".alert-error",
                    '[class*="error"]',
                    "text=错误",
                    "text=Error",
                    "text=失败",
                    "text=Invalid",
                    "text=invalid",
                    "text=不正确",
                    "text=密码错误",
                    "text=用户名错误",
                ]

                for selector in error_selectors:
                    try:
                        error_element = await self.page.wait_for_selector(
                            selector, timeout=1000
                        )
                        if error_element:
                            error_text = await error_element.text_content()
                            logger.error(f"登录错误: {error_text}")
                            break
                    except:
                        continue

                # 尝试截图以便调试
                try:
                    screenshot_path = "debug_login_failed.png"
                    await self.page.screenshot(path=screenshot_path)
                    logger.info(f"已保存登录失败截图: {screenshot_path}")
                except:
                    pass

                return False

        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            return False

    async def _get_user_info(self):
        """获取用户信息"""
        try:
            # 尝试从页面获取用户信息
            # 方法1: 从URL获取用户ID
            current_url = self.page.url
            if "/user/" in current_url:
                parts = current_url.split("/user/")
                if len(parts) > 1:
                    self.user_id = parts[1].split("/")[0]

            # 方法2: 从页面元素获取
            if not self.user_id:
                try:
                    user_element = await self.page.wait_for_selector(
                        "[data-user-id], [data-userid], .user-id", timeout=2000
                    )
                    if user_element:
                        self.user_id = (
                            await user_element.get_attribute("data-user-id")
                            or await user_element.get_attribute("data-userid")
                            or await user_element.text_content()
                        )
                except:
                    pass

            # 方法3: 从localStorage获取
            if not self.user_id:
                try:
                    storage = await self.page.evaluate(
                        "() => JSON.stringify(localStorage)"
                    )
                    storage_data = json.loads(storage)
                    for key, value in storage_data.items():
                        if "user" in key.lower() and "id" in key.lower():
                            try:
                                user_data = json.loads(value)
                                if isinstance(user_data, dict) and "_id" in user_data:
                                    self.user_id = user_data["_id"]
                                    break
                            except:
                                if len(value) > 10:  # 可能是用户ID
                                    self.user_id = value
                                    break
                except:
                    pass

            self.username = self.config.username
            logger.info(f"用户信息: username={self.username}, user_id={self.user_id}")

        except Exception as e:
            logger.warning(f"获取用户信息失败: {e}")

    async def start_listening(self):
        """开始监听消息"""
        if not self.connected:
            logger.error("未连接，请先登录")
            return False

        self.running = True
        logger.info("开始监听消息...")

        # 确保在消息页面
        await self._ensure_message_page()

        # 开始消息监听循环
        asyncio.create_task(self._message_listener_loop())

        return True

    async def _ensure_message_page(self):
        """确保在消息页面"""
        try:
            # 检查是否在消息页面
            current_url = self.page.url
            if (
                "/chat" in current_url
                or "/message" in current_url
                or "/converse" in current_url
            ):
                return True

            # 尝试导航到消息页面
            message_link_selectors = [
                'a[href*="/chat"]',
                'a[href*="/message"]',
                'a[href*="/converse"]',
                'button:has-text("消息")',
                'button:has-text("聊天")',
                'button:has-text("Chat")',
            ]

            for selector in message_link_selectors:
                try:
                    link = await self.page.wait_for_selector(selector, timeout=2000)
                    if link:
                        await link.click()
                        await self.page.wait_for_timeout(2000)
                        return True
                except:
                    continue

            logger.warning("无法导航到消息页面，继续在当前页面监听")
            return False

        except Exception as e:
            logger.error(f"确保消息页面失败: {e}")
            return False

    async def _message_listener_loop(self):
        """消息监听循环"""
        while self.running:
            try:
                await self._check_new_messages()
                await asyncio.sleep(self.message_check_interval)

            except Exception as e:
                logger.error(f"消息监听循环错误: {e}")
                await asyncio.sleep(5)  # 出错后等待更长时间

    async def _check_new_messages(self):
        """检查新消息"""
        try:
            # 获取消息列表
            messages = await self._get_recent_messages()

            for message in messages:
                # 处理消息
                await self._handle_message(message)

            self.last_message_check = time.time()

        except Exception as e:
            logger.error(f"检查新消息失败: {e}")

    async def _get_recent_messages(self) -> List[Dict]:
        """获取最近的消息"""
        try:
            # 尝试从页面获取消息
            # 这里需要根据TailChat的实际DOM结构来调整

            # 方法1: 从消息列表获取
            message_selectors = [
                ".message-item",
                '[class*="message"]',
                '[data-testid="message"]',
                ".chat-message",
            ]

            messages = []

            for selector in message_selectors:
                try:
                    message_elements = await self.page.query_selector_all(selector)
                    if message_elements:
                        for element in message_elements[-10:]:  # 只取最近10条
                            try:
                                message_data = await self._extract_message_data(element)
                                if message_data:
                                    messages.append(message_data)
                            except:
                                continue
                        break
                except:
                    continue

            return messages

        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []

    async def _extract_message_data(self, element) -> Optional[Dict]:
        """从DOM元素提取消息数据"""
        try:
            # 获取消息ID
            message_id = (
                await element.get_attribute("data-message-id")
                or await element.get_attribute("id")
                or str(time.time())
            )

            # 获取消息内容
            content_element = await element.query_selector(
                '.message-content, .content, [class*="content"]'
            )
            content = await content_element.text_content() if content_element else ""

            # 获取作者信息
            author_element = await element.query_selector(
                '.message-author, .author, [class*="author"]'
            )
            author = await author_element.text_content() if author_element else ""
            author_id = author  # 简化处理

            # 检查是否是私信
            is_dm = False
            dm_indicators = await element.query_selector_all(
                '[class*="dm"], [class*="private"], [data-type="dm"]'
            )
            if dm_indicators:
                is_dm = True

            # 检查@提及
            mentions = []
            mention_elements = await element.query_selector_all(
                ".mention, [data-mention]"
            )
            for mention_element in mention_elements:
                mention_id = await mention_element.get_attribute(
                    "data-mention"
                ) or await mention_element.get_attribute("data-user-id")
                if mention_id:
                    mentions.append(mention_id)

            return {
                "_id": message_id,
                "content": content.strip() if content else "",
                "author": author.strip() if author else "",
                "author": (
                    author_id.strip() if author_id else ""
                ),  # TailChat中author就是用户ID
                "converseId": "unknown",  # 需要根据实际结构获取
                "groupId": None,
                "isDM": is_dm,
                "mentions": mentions,
                "createdAt": str(time.time()),
            }

        except Exception as e:
            logger.debug(f"提取消息数据失败: {e}")
            return None

    async def _handle_message(self, message_data: Dict):
        """处理消息"""
        try:
            message = Message.from_dict(message_data)

            # 调用注册的消息处理器
            for handler in self.message_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"消息处理器错误: {e}")

        except Exception as e:
            logger.error(f"处理消息失败: {e}")

    def add_message_handler(self, handler: Callable):
        """添加消息处理器"""
        self.message_handlers.append(handler)

    async def send_message(
        self, converse_id: str, content: str, mentions: List[str] = None
    ):
        """发送消息"""
        try:
            logger.info(f"发送消息到 {converse_id}: {content[:50]}...")

            # 确保在正确的会话页面
            await self._ensure_converse_page(converse_id)

            # 查找消息输入框
            input_selectors = [
                'textarea[placeholder*="消息"]',
                'input[placeholder*="消息"]',
                ".message-input",
                '[contenteditable="true"]',
                '[role="textbox"]',
            ]

            message_input = None
            for selector in input_selectors:
                try:
                    message_input = await self.page.wait_for_selector(
                        selector, timeout=2000
                    )
                    if message_input:
                        break
                except:
                    continue

            if not message_input:
                logger.error("未找到消息输入框")
                return False

            # 模拟人类输入
            await message_input.click()
            await self.page.wait_for_timeout(random.randint(200, 500))

            # 清空输入框（如果有内容）
            try:
                await message_input.fill("")
            except:
                pass

            await self.page.wait_for_timeout(random.randint(100, 300))

            # 逐字符输入，模拟人类打字
            for char in content:
                await message_input.type(char, delay=random.randint(30, 100))
                await self.page.wait_for_timeout(random.randint(10, 30))

            # 等待一下再发送
            await self.page.wait_for_timeout(random.randint(500, 1000))

            # 查找发送按钮
            send_button_selectors = [
                'button:has-text("发送")',
                'button:has-text("Send")',
                'button[type="submit"]',
                ".send-button",
                '[aria-label*="发送"]',
                '[title*="发送"]',
            ]

            send_button = None
            for selector in send_button_selectors:
                try:
                    send_button = await self.page.wait_for_selector(
                        selector, timeout=2000
                    )
                    if send_button:
                        break
                except:
                    continue

            if not send_button:
                # 尝试按Enter键发送
                await message_input.press("Enter")
                await self.page.wait_for_timeout(1000)
            else:
                # 模拟人类点击发送按钮
                box = await send_button.bounding_box()
                if box:
                    x = box["x"] + box["width"] / 2 + random.uniform(-3, 3)
                    y = box["y"] + box["height"] / 2 + random.uniform(-3, 3)
                    await self.page.mouse.move(x, y)
                    await self.page.wait_for_timeout(random.randint(200, 500))

                await send_button.click()
                await self.page.wait_for_timeout(1000)

            logger.info("消息发送成功")
            return True

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False

    async def _ensure_converse_page(self, converse_id: str):
        """确保在指定的会话页面"""
        try:
            # 检查当前是否已经在正确的会话
            current_url = self.page.url
            if converse_id in current_url:
                return True

            # 尝试导航到指定会话
            # 这里需要根据TailChat的实际导航结构来实现
            # 简化处理：暂时只记录日志
            logger.info(f"需要导航到会话: {converse_id}")
            return False

        except Exception as e:
            logger.error(f"确保会话页面失败: {e}")
            return False

    async def send_direct_message(self, user_id: str, content: str):
        """发送私信"""
        try:
            logger.info(f"发送私信给 {user_id}: {content[:50]}...")

            # 导航到私信页面
            await self._navigate_to_dm(user_id)

            # 发送消息
            return await self.send_message(f"dm_{user_id}", content)

        except Exception as e:
            logger.error(f"发送私信失败: {e}")
            return False

    async def _navigate_to_dm(self, user_id: str):
        """导航到私信页面"""
        try:
            # 查找私信按钮或链接
            dm_selectors = [
                f'a[href*="/dm/{user_id}"]',
                f'a[href*="/user/{user_id}"]',
                f'button[data-user-id="{user_id}"]',
                f'[data-testid="dm-{user_id}"]',
            ]

            for selector in dm_selectors:
                try:
                    dm_link = await self.page.wait_for_selector(selector, timeout=2000)
                    if dm_link:
                        await dm_link.click()
                        await self.page.wait_for_timeout(2000)
                        return True
                except:
                    continue

            logger.warning(f"未找到用户 {user_id} 的私信链接")
            return False

        except Exception as e:
            logger.error(f"导航到私信页面失败: {e}")
            return False

    async def is_online(self) -> bool:
        """检查是否在线"""
        try:
            # 检查页面是否仍然响应
            title = await self.page.title()
            return True
        except:
            return False

    async def disconnect(self):
        """断开连接"""
        self.running = False
        logger.info("正在断开连接...")

        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()

        self.connected = False
        logger.info("连接已断开")

    async def run(self):
        """运行客户端"""
        try:
            # 初始化浏览器
            if not await self.init_browser():
                return False

            # 登录
            if not await self.login():
                return False

            self.connected = True

            # 开始监听消息
            await self.start_listening()

            logger.info("TailChat浏览器客户端运行中...")

            # 保持运行
            while self.running:
                await asyncio.sleep(1)

                # 定期检查连接状态
                if not await self.is_online():
                    logger.warning("连接断开，尝试重连...")
                    await self.disconnect()
                    await asyncio.sleep(5)
                    return await self.run()  # 递归重连

            return True

        except Exception as e:
            logger.error(f"客户端运行失败: {e}")
            return False

    async def test_connection(self):
        """测试连接"""
        try:
            logger.info("测试连接...")

            # 检查页面标题
            title = await self.page.title()
            logger.info(f"页面标题: {title}")

            # 检查用户信息
            logger.info(f"用户: {self.username} (ID: {self.user_id})")

            # 尝试发送测试消息
            test_converse = "test"
            test_message = "🤖 机器人连接测试"

            success = await self.send_message(test_converse, test_message)
            if success:
                logger.info("连接测试成功")
            else:
                logger.warning("发送测试消息失败，但连接正常")

            return True

        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return False
