import os
import time
import logging
import threading
from typing import Optional, Callable
import pyperclip

from clipboard_watcher import ClipboardWatcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClipboardIntegration:
    def __init__(self, save_folder: str = "."):
        self.save_folder = save_folder
        self.watcher = None
        self.watcher_thread = None
        self.is_running = False
        self.current_title = ""
        self.on_save_callback: Optional[Callable] = None
    
    def set_save_folder(self, folder: str):
        """设置保存文件夹"""
        self.save_folder = folder
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder, exist_ok=True)
    
    def set_current_title(self, title: str):
        """设置当前处理的标题"""
        self.current_title = title
    
    def set_on_save_callback(self, callback: Callable):
        """设置保存完成后的回调函数"""
        self.on_save_callback = callback
    
    def on_clipboard_change(self, file_path, filename, title, content, matched, matched_file=None, similarity=0):
        """
        剪贴板变化回调函数
        """
        if not title:
            logger.info("未提取到标题")
            return
        
        if matched and file_path:
            logger.info(f"已保存: {filename}")
            if self.on_save_callback:
                self.on_save_callback(filename)
        else:
            # 如果没有匹配到文件，尝试使用当前标题创建新文件
            if self.current_title:
                try:
                    # 清洗标题用于文件名
                    clean_title = self._clean_filename(self.current_title)
                    file_path = os.path.join(self.save_folder, f"{clean_title}.txt")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"已保存到新文件: {file_path}")
                    if self.on_save_callback:
                        self.on_save_callback(os.path.basename(file_path))
                except Exception as e:
                    logger.error(f"保存文件失败: {e}")
            else:
                logger.info(f"未匹配 标题:{title[:15]}... 最佳:{matched_file} 相似度:{similarity}")
    
    def _clean_filename(self, title: str) -> str:
        """清洗标题用于文件名"""
        import re
        # 移除无效字符
        cleaned = re.sub(r'[\\/:*?"<>|]', '', title)
        # 限制长度
        if len(cleaned) > 100:
            cleaned = cleaned[:100]
        return cleaned
    
    def start_watching(self):
        """开始监听剪贴板"""
        try:
            if not os.path.exists(self.save_folder):
                os.makedirs(self.save_folder, exist_ok=True)
            
            self.watcher = ClipboardWatcher(self.save_folder, self.on_clipboard_change)
            self.watcher_thread = threading.Thread(target=self.watcher.run, daemon=True)
            self.watcher_thread.start()
            self.is_running = True
            logger.info("已开始监听剪贴板")
            return True
        except Exception as e:
            logger.error(f"启动剪贴板监听失败: {e}")
            return False
    
    def stop_watching(self):
        """停止监听剪贴板"""
        try:
            if self.watcher:
                self.watcher.stop()
            self.is_running = False
            logger.info("已停止监听剪贴板")
        except Exception as e:
            logger.error(f"停止剪贴板监听失败: {e}")
    
    def wait_for_clipboard_content(self, timeout: int = 30) -> Optional[str]:
        """
        等待剪贴板内容变化
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            剪贴板内容，如果超时则返回None
        """
        start_time = time.time()
        last_content = pyperclip.paste() or ""
        
        while time.time() - start_time < timeout:
            current_content = pyperclip.paste() or ""
            if current_content != last_content and len(current_content) > 10:
                logger.info("剪贴板内容已更新")
                return current_content
            time.sleep(0.5)
        
        logger.warning("等待剪贴板内容超时")
        return None

# 全局剪贴板集成实例
clipboard_integration = ClipboardIntegration()

if __name__ == "__main__":
    # 示例用法
    integration = ClipboardIntegration("./test_output")
    integration.set_current_title("测试标题")
    
    def on_save(filename):
        print(f"保存完成: {filename}")
    
    integration.set_on_save_callback(on_save)
    integration.start_watching()
    
    print("请复制一些内容...")
    time.sleep(10)
    
    integration.stop_watching()