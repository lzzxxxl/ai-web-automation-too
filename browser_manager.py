import os
import subprocess
import time
import logging
from typing import List, Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, Page

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.browsers: Dict[str, Browser] = {}
        self.pages: Dict[str, Page] = {}
        self.playwright = None
    
    def start_playwright(self):
        """启动Playwright"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        return self.playwright
    
    def connect_to_browser(self, browser_type: str, debug_port: int = 9222, instance_id: str = "default") -> Optional[Browser]:
        """
        连接到已打开的浏览器，如果未打开则尝试启动
        
        Args:
            browser_type: 浏览器类型 (chrome, edge, firefox)
            debug_port: 远程调试端口
            instance_id: 实例ID，用于区分多个浏览器实例
            
        Returns:
            浏览器实例，如果连接失败则返回None
        """
        try:
            playwright = self.start_playwright()
            ws_endpoint = f"ws://localhost:{debug_port}/devtools/browser"
            
            if browser_type.lower() == "chrome":
                browser = playwright.chromium.connect_over_cdp(ws_endpoint)
            elif browser_type.lower() == "edge":
                browser = playwright.chromium.connect_over_cdp(ws_endpoint)
            elif browser_type.lower() == "firefox":
                browser = playwright.firefox.connect_over_cdp(ws_endpoint)
            else:
                logger.error(f"不支持的浏览器类型: {browser_type}")
                return None
            
            self.browsers[instance_id] = browser
            logger.info(f"成功连接到{browser_type}浏览器实例 {instance_id}")
            return browser
        except Exception as e:
            logger.error(f"连接浏览器失败: {e}")
            logger.info("尝试自动启动浏览器...")
            
            # 尝试自动启动浏览器
            if self.open_browser_with_debug(browser_type, debug_port):
                # 等待浏览器启动
                time.sleep(2)
                # 再次尝试连接
                try:
                    if browser_type.lower() == "chrome":
                        browser = playwright.chromium.connect_over_cdp(ws_endpoint)
                    elif browser_type.lower() == "edge":
                        browser = playwright.chromium.connect_over_cdp(ws_endpoint)
                    elif browser_type.lower() == "firefox":
                        browser = playwright.firefox.connect_over_cdp(ws_endpoint)
                    
                    self.browsers[instance_id] = browser
                    logger.info(f"成功连接到{browser_type}浏览器实例 {instance_id}")
                    return browser
                except Exception as e2:
                    logger.error(f"再次连接失败: {e2}")
                    logger.info("请手动启动浏览器并开启远程调试模式")
                    return None
            else:
                logger.error("启动浏览器失败，请手动启动")
                return None
    
    def get_or_create_page(self, instance_id: str = "default") -> Optional[Page]:
        """
        获取或创建页面
        
        Args:
            instance_id: 浏览器实例ID
            
        Returns:
            页面实例，如果获取失败则返回None
        """
        if instance_id not in self.browsers:
            logger.error(f"浏览器实例 {instance_id} 不存在")
            return None
        
        if instance_id in self.pages:
            return self.pages[instance_id]
        
        try:
            browser = self.browsers[instance_id]
            page = browser.new_page()
            self.pages[instance_id] = page
            logger.info(f"为实例 {instance_id} 创建新页面")
            return page
        except Exception as e:
            logger.error(f"创建页面失败: {e}")
            return None
    
    def close_browser(self, instance_id: str = "default"):
        """
        关闭浏览器实例
        
        Args:
            instance_id: 浏览器实例ID
        """
        if instance_id in self.pages:
            try:
                self.pages[instance_id].close()
                del self.pages[instance_id]
            except Exception as e:
                logger.error(f"关闭页面失败: {e}")
        
        if instance_id in self.browsers:
            try:
                self.browsers[instance_id].close()
                del self.browsers[instance_id]
                logger.info(f"已关闭浏览器实例 {instance_id}")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")
    
    def close_all(self):
        """关闭所有浏览器实例"""
        for instance_id in list(self.browsers.keys()):
            self.close_browser(instance_id)
        
        if self.playwright:
            try:
                self.playwright.stop()
                self.playwright = None
                logger.info("已停止Playwright")
            except Exception as e:
                logger.error(f"停止Playwright失败: {e}")
    
    def check_connection(self, instance_id: str = "default") -> bool:
        """
        检查浏览器连接状态
        
        Args:
            instance_id: 浏览器实例ID
            
        Returns:
            连接状态
        """
        if instance_id not in self.browsers:
            return False
        
        try:
            browser = self.browsers[instance_id]
            # 尝试获取浏览器版本信息来验证连接
            browser.version()
            return True
        except Exception:
            return False
    
    def _get_browser_path_from_registry(self, browser_type: str) -> str:
        """
        从Windows注册表中获取浏览器路径
        
        Args:
            browser_type: 浏览器类型
            
        Returns:
            浏览器可执行文件路径，如果未找到则返回空字符串
        """
        import winreg
        
        try:
            if browser_type.lower() == "chrome":
                # Chrome 注册表路径
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
                    r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
                ]
            elif browser_type.lower() == "edge":
                # Edge 注册表路径
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
                    r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"
                ]
            elif browser_type.lower() == "firefox":
                # Firefox 注册表路径
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
                    r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe"
                ]
            else:
                return ""
            
            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    path, _ = winreg.QueryValueEx(key, "")
                    winreg.CloseKey(key)
                    if os.path.exists(path):
                        return path
                except:
                    pass
            
            return ""
        except Exception as e:
            logger.debug(f"从注册表获取浏览器路径失败: {e}")
            return ""
    
    def _get_browser_path_from_path(self, browser_type: str) -> str:
        """
        从环境变量PATH中获取浏览器路径
        
        Args:
            browser_type: 浏览器类型
            
        Returns:
            浏览器可执行文件路径，如果未找到则返回空字符串
        """
        import shutil
        
        try:
            if browser_type.lower() == "chrome":
                exe_name = "chrome.exe" if os.name == "nt" else "google-chrome"
            elif browser_type.lower() == "edge":
                exe_name = "msedge.exe" if os.name == "nt" else "microsoft-edge"
            elif browser_type.lower() == "firefox":
                exe_name = "firefox.exe" if os.name == "nt" else "firefox"
            else:
                return ""
            
            # 尝试在PATH中查找
            path = shutil.which(exe_name)
            if path and os.path.exists(path):
                return path
            
            # 尝试其他变体
            if browser_type.lower() == "chrome" and os.name != "nt":
                path = shutil.which("chromium")
                if path and os.path.exists(path):
                    return path
            elif browser_type.lower() == "edge" and os.name != "nt":
                path = shutil.which("edge")
                if path and os.path.exists(path):
                    return path
            
            return ""
        except Exception as e:
            logger.debug(f"从PATH获取浏览器路径失败: {e}")
            return ""
    
    def open_browser_with_debug(self, browser_type: str, debug_port: int = 9222) -> bool:
        """
        打开带远程调试模式的浏览器
        
        Args:
            browser_type: 浏览器类型 (chrome, edge, firefox)
            debug_port: 远程调试端口
            
        Returns:
            是否成功打开
        """
        try:
            browser_path = ""
            
            # 1. 尝试从Windows注册表获取（仅Windows）
            if os.name == "nt":
                browser_path = self._get_browser_path_from_registry(browser_type)
                if browser_path:
                    logger.info(f"从注册表找到{browser_type}浏览器: {browser_path}")
            
            # 2. 尝试从PATH环境变量获取
            if not browser_path:
                browser_path = self._get_browser_path_from_path(browser_type)
                if browser_path:
                    logger.info(f"从PATH找到{browser_type}浏览器: {browser_path}")
            
            # 3. 尝试默认路径
            if not browser_path:
                if browser_type.lower() == "chrome":
                    # 查找Chrome可执行文件路径
                    if os.name == "nt":  # Windows
                        browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                        if not os.path.exists(browser_path):
                            browser_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                    else:  # macOS/Linux
                        browser_path = "/usr/bin/google-chrome"
                        if not os.path.exists(browser_path):
                            browser_path = "/usr/bin/chromium"
                
                elif browser_type.lower() == "edge":
                    # 查找Edge可执行文件路径
                    if os.name == "nt":  # Windows
                        browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                        if not os.path.exists(browser_path):
                            browser_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                    else:  # macOS/Linux
                        browser_path = "/usr/bin/microsoft-edge"
                        if not os.path.exists(browser_path):
                            browser_path = "/usr/bin/edge"
                
                elif browser_type.lower() == "firefox":
                    # 查找Firefox可执行文件路径
                    if os.name == "nt":  # Windows
                        browser_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
                        if not os.path.exists(browser_path):
                            browser_path = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
                    elif os.name == "darwin":  # macOS
                        browser_path = "/Applications/Firefox.app/Contents/MacOS/firefox"
                    else:  # Linux
                        browser_path = "/usr/bin/firefox"
                        if not os.path.exists(browser_path):
                            browser_path = "/usr/bin/firefox-bin"
                else:
                    logger.error(f"不支持的浏览器类型: {browser_type}")
                    return False
            
            if not os.path.exists(browser_path):
                logger.error(f"找不到{browser_type}浏览器可执行文件")
                return False
            
            # 启动浏览器
            cmd = [
                browser_path,
                f"--remote-debugging-port={debug_port}",
                "--user-data-dir=./browser_profile"
            ]
            
            subprocess.Popen(cmd)
            logger.info(f"已启动{browser_type}浏览器，调试端口: {debug_port}")
            # 等待浏览器启动
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"启动浏览器失败: {e}")
            return False

# 全局浏览器管理器实例
browser_manager = BrowserManager()

if __name__ == "__main__":
    # 示例用法
    manager = BrowserManager()
    
    # 打开带调试模式的Chrome
    # manager.open_browser_with_debug("chrome", 9222)
    
    # 连接到浏览器
    browser = manager.connect_to_browser("chrome", 9222, "instance1")
    
    if browser:
        # 获取页面
        page = manager.get_or_create_page("instance1")
        if page:
            page.goto("https://chatgpt.com")
            print("已打开ChatGPT")
            time.sleep(5)
        
        # 关闭浏览器
        manager.close_browser("instance1")
    
    # 关闭所有
    manager.close_all()