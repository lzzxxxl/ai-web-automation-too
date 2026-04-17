import time
import logging
from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAutomation:
    def __init__(self, page: Page):
        self.page = page
        self.continue_max_click = 10  # 最大点击继续生成次数
        self.wait_stable_time = 5  # 内容稳定判定时间（秒）
        self.retry_count = 3  # 重试次数
        self.retry_delay = 2  # 重试延迟（秒）
        self.ai_platform = "unknown"  # AI平台类型
    
    def set_continue_max_click(self, max_click: int):
        """设置最大点击继续生成次数"""
        self.continue_max_click = max_click
    
    def set_wait_stable_time(self, wait_time: int):
        """设置内容稳定判定时间"""
        self.wait_stable_time = wait_time
    
    def set_retry_count(self, retry_count: int):
        """设置重试次数"""
        self.retry_count = retry_count
    
    def set_retry_delay(self, retry_delay: int):
        """设置重试延迟"""
        self.retry_delay = retry_delay
    
    def detect_ai_platform(self) -> str:
        """
        自动检测AI平台类型
        
        Returns:
            AI平台类型
        """
        try:
            url = self.page.url.lower()
            
            # 检测常见AI平台
            if "chatgpt" in url:
                self.ai_platform = "chatgpt"
                logger.info("检测到ChatGPT平台")
            elif "claude" in url:
                self.ai_platform = "claude"
                logger.info("检测到Claude平台")
            elif "gemini" in url or "bard" in url:
                self.ai_platform = "gemini"
                logger.info("检测到Gemini/Bard平台")
            elif "perplexity" in url:
                self.ai_platform = "perplexity"
                logger.info("检测到Perplexity平台")
            elif "coze" in url:
                self.ai_platform = "coze"
                logger.info("检测到Coze平台")
            else:
                # 通过页面特征检测
                if self.page.locator('text="ChatGPT"').is_visible():
                    self.ai_platform = "chatgpt"
                    logger.info("通过页面特征检测到ChatGPT平台")
                elif self.page.locator('text="Claude"').is_visible():
                    self.ai_platform = "claude"
                    logger.info("通过页面特征检测到Claude平台")
                elif self.page.locator('text="Gemini"').is_visible() or self.page.locator('text="Bard"').is_visible():
                    self.ai_platform = "gemini"
                    logger.info("通过页面特征检测到Gemini/Bard平台")
                else:
                    self.ai_platform = "unknown"
                    logger.info("未检测到已知AI平台")
            
            return self.ai_platform
        except Exception as e:
            logger.error(f"检测AI平台失败: {e}")
            self.ai_platform = "unknown"
            return self.ai_platform
    
    def _retry_operation(self, operation, *args, **kwargs) -> Tuple[bool, Any]:
        """
        智能重试操作
        
        Args:
            operation: 要执行的操作函数
            *args: 操作函数的位置参数
            **kwargs: 操作函数的关键字参数
        
        Returns:
            (是否成功, 操作结果)
        """
        for attempt in range(self.retry_count + 1):
            try:
                result = operation(*args, **kwargs)
                return True, result
            except PlaywrightTimeoutError:
                logger.warning(f"操作超时，正在重试 ({attempt + 1}/{self.retry_count + 1})...")
            except Exception as e:
                logger.warning(f"操作失败: {e}，正在重试 ({attempt + 1}/{self.retry_count + 1})...")
            
            if attempt < self.retry_count:
                time.sleep(self.retry_delay)
            else:
                logger.error("操作重试失败")
                return False, None
    
    def locate_input_box(self) -> Optional[Locator]:
        """
        自动定位网页AI的输入框
        
        Returns:
            输入框定位器，如果未找到则返回None
        """
        def _locate():
            # 根据AI平台使用不同的定位策略
            if self.ai_platform == "chatgpt":
                # ChatGPT特定定位
                selectors = ['textarea', '[data-testid="text-area"]', '.text-area']
            elif self.ai_platform == "claude":
                # Claude特定定位
                selectors = ['textarea', '[data-testid="message-input"]', '.message-input']
            elif self.ai_platform == "gemini":
                # Gemini特定定位
                selectors = ['textarea', '[aria-label*="Message"]', '.ql-editor']
            else:
                # 通用定位策略
                selectors = [
                    'textarea',
                    '[contenteditable="true"]',
                    '.chat-input', '.message-input', '.input-area',
                    '.text-input', '.prompt-input', '.user-input'
                ]
            
            for selector in selectors:
                input_box = self.page.locator(selector).first
                if input_box.is_visible():
                    logger.info(f"找到输入框: {selector}")
                    return input_box
            
            logger.warning("未找到输入框")
            return None
        
        success, result = self._retry_operation(_locate)
        return result if success else None
    
    def locate_send_button(self) -> Optional[Locator]:
        """
        自动定位发送按钮
        
        Returns:
            发送按钮定位器，如果未找到则返回None
        """
        def _locate():
            # 根据AI平台使用不同的定位策略
            if self.ai_platform == "chatgpt":
                # ChatGPT特定定位
                selectors = [
                    'button:has-text("发送")',
                    'button:has-text("Send")',
                    '[data-testid="send-button"]',
                    '.send-button'
                ]
            elif self.ai_platform == "claude":
                # Claude特定定位
                selectors = [
                    'button:has-text("发送")',
                    'button:has-text("Send")',
                    '[data-testid="send-button"]',
                    '.send-button'
                ]
            elif self.ai_platform == "gemini":
                # Gemini特定定位
                selectors = [
                    'button:has-text("发送")',
                    'button:has-text("Send")',
                    '[aria-label*="发送"]',
                    '[aria-label*="Send"]'
                ]
            else:
                # 通用定位策略
                selectors = [
                    'button:has-text("发送")',
                    'button:has-text("Send")',
                    'button:has-text("Submit")',
                    'button:has-text("提交")',
                    '.send-button',
                    '.submit-button',
                    '[aria-label*="发送"]',
                    '[aria-label*="Send"]'
                ]
            
            for selector in selectors:
                button = self.page.locator(selector).first
                if button.is_visible():
                    logger.info(f"找到发送按钮: {selector}")
                    return button
            
            # 尝试定位具有特定图标的按钮
            icon_buttons = [
                'button:has(svg)',
                'button:has(i)',
                '.icon-button'
            ]
            
            for selector in icon_buttons:
                buttons = self.page.locator(selector).all()
                for button in buttons:
                    if button.is_visible():
                        logger.info(f"找到可能的发送按钮: {selector}")
                        return button
            
            logger.warning("未找到发送按钮")
            return None
        
        success, result = self._retry_operation(_locate)
        return result if success else None
    
    def send_message(self, message: str) -> bool:
        """
        发送消息
        
        Args:
            message: 要发送的消息
            
        Returns:
            是否发送成功
        """
        # 检测AI平台
        self.detect_ai_platform()
        
        def _send():
            # 定位输入框
            input_box = self.locate_input_box()
            if not input_box:
                return False
            
            # 输入消息
            input_box.fill(message)
            logger.info(f"已输入消息: {message[:50]}...")
            
            # 尝试点击发送按钮
            send_button = self.locate_send_button()
            if send_button:
                send_button.click()
                logger.info("已点击发送按钮")
            else:
                # 如果没找到发送按钮，尝试回车发送
                input_box.press('Enter')
                logger.info("已使用回车发送")
            
            return True
        
        success, result = self._retry_operation(_send)
        return result if success else False
    
    def is_generating(self) -> bool:
        """
        检查AI是否正在生成回复
        
        Returns:
            是否正在生成
        """
        def _check():
            # 根据AI平台使用不同的检测策略
            if self.ai_platform == "chatgpt":
                # ChatGPT特定检测
                indicators = [
                    'text="加载中"',
                    'text="Thinking"',
                    'text="Generating"',
                    '[data-testid="loading"]',
                    '.loading',
                    '.spinner'
                ]
            elif self.ai_platform == "claude":
                # Claude特定检测
                indicators = [
                    'text="加载中"',
                    'text="Thinking"',
                    'text="Generating"',
                    '[data-testid="loading"]',
                    '.loading'
                ]
            elif self.ai_platform == "gemini":
                # Gemini特定检测
                indicators = [
                    'text="加载中"',
                    'text="Thinking"',
                    'text="Generating"',
                    '.loading',
                    '.spinner'
                ]
            else:
                # 通用检测
                indicators = [
                    'text="加载中"',
                    'text="思考中"',
                    'text="生成中"',
                    'text="Thinking"',
                    'text="Generating"',
                    '.loading',
                    '.loading-indicator',
                    '.spinner',
                    '[aria-label*="加载"]',
                    '[aria-label*="Loading"]'
                ]
            
            for selector in indicators:
                if self.page.locator(selector).is_visible():
                    return True
            
            return False
        
        success, result = self._retry_operation(_check)
        return result if success else False
    
    def locate_continue_button(self) -> Optional[Locator]:
        """
        定位继续生成按钮
        
        Returns:
            继续生成按钮定位器，如果未找到则返回None
        """
        def _locate():
            # 根据AI平台使用不同的定位策略
            if self.ai_platform == "chatgpt":
                # ChatGPT特定定位
                selectors = [
                    'button:has-text("继续生成")',
                    'button:has-text("Continue generating")',
                    'button:has-text("Continue")',
                    '[data-testid="continue-button"]',
                    '.continue-button'
                ]
            elif self.ai_platform == "claude":
                # Claude特定定位
                selectors = [
                    'button:has-text("继续生成")',
                    'button:has-text("Continue generating")',
                    'button:has-text("Continue")',
                    '.continue-button'
                ]
            elif self.ai_platform == "gemini":
                # Gemini特定定位
                selectors = [
                    'button:has-text("继续生成")',
                    'button:has-text("Continue generating")',
                    'button:has-text("Continue")',
                    '.continue-button'
                ]
            else:
                # 通用定位策略
                selectors = [
                    'button:has-text("继续生成")',
                    'button:has-text("继续写")',
                    'button:has-text("Continue generating")',
                    'button:has-text("Continue")',
                    '.continue-button',
                    '.continue-generating'
                ]
            
            for selector in selectors:
                button = self.page.locator(selector).first
                if button.is_visible():
                    logger.info(f"找到继续生成按钮: {selector}")
                    return button
            
            return None
        
        success, result = self._retry_operation(_locate)
        return result if success else None
    
    def locate_copy_button(self) -> Optional[Locator]:
        """
        定位复制按钮
        
        Returns:
            复制按钮定位器，如果未找到则返回None
        """
        def _locate():
            # 根据AI平台使用不同的定位策略
            if self.ai_platform == "chatgpt":
                # ChatGPT特定定位
                selectors = [
                    'button:has-text("复制")',
                    'button:has-text("Copy")',
                    '[data-testid="copy-button"]',
                    '.copy-button'
                ]
            elif self.ai_platform == "claude":
                # Claude特定定位
                selectors = [
                    'button:has-text("复制")',
                    'button:has-text("Copy")',
                    '.copy-button'
                ]
            elif self.ai_platform == "gemini":
                # Gemini特定定位
                selectors = [
                    'button:has-text("复制")',
                    'button:has-text("Copy")',
                    '.copy-button'
                ]
            else:
                # 通用定位策略
                selectors = [
                    'button:has-text("复制")',
                    'button:has-text("Copy")',
                    '.copy-button',
                    '[aria-label*="复制"]',
                    '[aria-label*="Copy"]'
                ]
            
            for selector in selectors:
                button = self.page.locator(selector).first
                if button.is_visible():
                    logger.info(f"找到复制按钮: {selector}")
                    return button
            
            return None
        
        success, result = self._retry_operation(_locate)
        return result if success else None
    
    def monitor_output(self) -> bool:
        """
        监控AI输出
        
        Returns:
            是否成功完成监控
        """
        def _monitor():
            continue_click_count = 0
            last_content = ""
            stable_time = 0
            
            while True:
                # 检查是否正在生成
                if self.is_generating():
                    logger.info("AI正在生成回复...")
                    time.sleep(2)
                    continue
                
                # 检查是否需要继续生成
                continue_button = self.locate_continue_button()
                if continue_button and continue_click_count < self.continue_max_click:
                    continue_button.click()
                    continue_click_count += 1
                    logger.info(f"已点击继续生成按钮，次数: {continue_click_count}")
                    time.sleep(2)
                    continue
                
                # 检查内容是否稳定
                try:
                    # 根据AI平台使用不同的选择器
                    if self.ai_platform == "chatgpt":
                        # ChatGPT特定选择器
                        response_elements = [
                            '.response',
                            '.answer',
                            '.message-content',
                            '.chat-message',
                            '.ai-message',
                            '[data-testid="message-content"]'
                        ]
                    elif self.ai_platform == "claude":
                        # Claude特定选择器
                        response_elements = [
                            '.response',
                            '.answer',
                            '.message-content',
                            '.chat-message',
                            '.ai-message',
                            '[data-testid="message-content"]'
                        ]
                    elif self.ai_platform == "gemini":
                        # Gemini特定选择器
                        response_elements = [
                            '.response',
                            '.answer',
                            '.message-content',
                            '.chat-message',
                            '.ai-message',
                            '.ql-editor'
                        ]
                    else:
                        # 通用选择器
                        response_elements = [
                            '.response',
                            '.answer',
                            '.message-content',
                            '.chat-message',
                            '.ai-message'
                        ]
                    
                    current_content = ""
                    for selector in response_elements:
                        elements = self.page.locator(selector).all()
                        if elements:
                            # 获取最后一个元素的内容
                            current_content = elements[-1].inner_text()
                            break
                    
                    if current_content == last_content:
                        stable_time += 1
                        if stable_time >= self.wait_stable_time:
                            logger.info("AI输出已稳定")
                            break
                    else:
                        last_content = current_content
                        stable_time = 0
                except Exception as e:
                    logger.error(f"获取回复内容失败: {e}")
                
                time.sleep(1)
            
            # 检查是否出现复制按钮
            copy_button = self.locate_copy_button()
            if copy_button:
                copy_button.click()
                logger.info("已点击复制按钮")
                return True
            else:
                logger.warning("未找到复制按钮")
                return False
        
        success, result = self._retry_operation(_monitor)
        return result if success else False

if __name__ == "__main__":
    # 示例用法
    from browser_manager import browser_manager
    
    # 连接浏览器
    browser = browser_manager.connect_to_browser("chrome", 9222)
    if browser:
        page = browser_manager.get_or_create_page()
        if page:
            # 打开ChatGPT
            page.goto("https://chatgpt.com")
            time.sleep(5)
            
            # 初始化AI自动化
            ai = AIAutomation(page)
            
            # 发送消息
            ai.send_message("Hello, how are you?")
            
            # 监控输出
            ai.monitor_output()
            
            # 关闭浏览器
            browser_manager.close_all()