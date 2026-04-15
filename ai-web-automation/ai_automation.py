import time
import logging
from typing import Optional, Dict, Any
from playwright.sync_api import Page, Locator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAutomation:
    def __init__(self, page: Page):
        self.page = page
        self.continue_max_click = 10  # 最大点击继续生成次数
        self.wait_stable_time = 5  # 内容稳定判定时间（秒）
    
    def set_continue_max_click(self, max_click: int):
        """设置最大点击继续生成次数"""
        self.continue_max_click = max_click
    
    def set_wait_stable_time(self, wait_time: int):
        """设置内容稳定判定时间"""
        self.wait_stable_time = wait_time
    
    def locate_input_box(self) -> Optional[Locator]:
        """
        自动定位网页AI的输入框
        
        Returns:
            输入框定位器，如果未找到则返回None
        """
        try:
            # 尝试定位textarea标签
            input_box = self.page.locator('textarea').first
            if input_box.is_visible():
                logger.info("找到textarea输入框")
                return input_box
            
            # 尝试定位contenteditable属性的元素
            input_box = self.page.locator('[contenteditable="true"]').first
            if input_box.is_visible():
                logger.info("找到contenteditable输入框")
                return input_box
            
            # 尝试定位具有特定class的输入框
            common_input_classes = [
                '.chat-input', '.message-input', '.input-area',
                '.text-input', '.prompt-input', '.user-input'
            ]
            
            for selector in common_input_classes:
                input_box = self.page.locator(selector).first
                if input_box.is_visible():
                    logger.info(f"找到输入框: {selector}")
                    return input_box
            
            logger.warning("未找到输入框")
            return None
        except Exception as e:
            logger.error(f"定位输入框失败: {e}")
            return None
    
    def locate_send_button(self) -> Optional[Locator]:
        """
        自动定位发送按钮
        
        Returns:
            发送按钮定位器，如果未找到则返回None
        """
        try:
            # 尝试定位具有发送功能的按钮
            send_buttons = [
                'button:has-text("发送")',
                'button:has-text("Send")',
                'button:has-text("Submit")',
                'button:has-text("提交")',
                '.send-button',
                '.submit-button',
                '[aria-label*="发送"]',
                '[aria-label*="Send"]'
            ]
            
            for selector in send_buttons:
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
        except Exception as e:
            logger.error(f"定位发送按钮失败: {e}")
            return None
    
    def send_message(self, message: str) -> bool:
        """
        发送消息
        
        Args:
            message: 要发送的消息
            
        Returns:
            是否发送成功
        """
        try:
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
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    def is_generating(self) -> bool:
        """
        检查AI是否正在生成回复
        
        Returns:
            是否正在生成
        """
        try:
            # 检查加载中提示
            loading_indicators = [
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
            
            for selector in loading_indicators:
                if self.page.locator(selector).is_visible():
                    return True
            
            return False
        except Exception as e:
            logger.error(f"检查生成状态失败: {e}")
            return False
    
    def locate_continue_button(self) -> Optional[Locator]:
        """
        定位继续生成按钮
        
        Returns:
            继续生成按钮定位器，如果未找到则返回None
        """
        try:
            continue_buttons = [
                'button:has-text("继续生成")',
                'button:has-text("继续写")',
                'button:has-text("Continue generating")',
                'button:has-text("Continue")',
                '.continue-button',
                '.continue-generating'
            ]
            
            for selector in continue_buttons:
                button = self.page.locator(selector).first
                if button.is_visible():
                    logger.info(f"找到继续生成按钮: {selector}")
                    return button
            
            return None
        except Exception as e:
            logger.error(f"定位继续生成按钮失败: {e}")
            return None
    
    def locate_copy_button(self) -> Optional[Locator]:
        """
        定位复制按钮
        
        Returns:
            复制按钮定位器，如果未找到则返回None
        """
        try:
            copy_buttons = [
                'button:has-text("复制")',
                'button:has-text("Copy")',
                '.copy-button',
                '[aria-label*="复制"]',
                '[aria-label*="Copy"]'
            ]
            
            for selector in copy_buttons:
                button = self.page.locator(selector).first
                if button.is_visible():
                    logger.info(f"找到复制按钮: {selector}")
                    return button
            
            return None
        except Exception as e:
            logger.error(f"定位复制按钮失败: {e}")
            return None
    
    def monitor_output(self) -> bool:
        """
        监控AI输出
        
        Returns:
            是否成功完成监控
        """
        try:
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
                    # 尝试获取回复内容
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
        except Exception as e:
            logger.error(f"监控输出失败: {e}")
            return False

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