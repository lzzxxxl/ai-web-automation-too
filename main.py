import os
import time
import logging
import json
import sys
import argparse
from typing import List, Optional

from browser_manager import browser_manager
from title_manager import title_manager
from ai_automation import AIAutomation
from clipboard_integration import clipboard_integration

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIAutomationTool:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.is_running = False
        self.current_task_index = 0
        self.tasks = []
        self.results = []
    
    def load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            "BROWSER_TYPE": "chrome",
            "INSTANCE_ID": "default",
            "QUESTION_FILE": "questions.txt",
            "CONTINUE_MAX_CLICK": 10,
            "WAIT_STABLE_TIME": 5,
            "RETRY_COUNT": 3,
            "SAVE_PATH": "./output",
            "DEBUG_PORT": 9222
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置和用户配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"读取配置文件失败: {e}")
                return default_config
        else:
            # 保存默认配置
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=2)
                logger.info(f"已创建默认配置文件: {self.config_file}")
            except Exception as e:
                logger.error(f"创建配置文件失败: {e}")
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存配置文件: {self.config_file}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
    
    def set_config(self, key: str, value):
        """设置配置"""
        self.config[key] = value
        self.save_config()
    
    def initialize(self, file_path: Optional[str] = None, paste_text: Optional[str] = None) -> bool:
        """初始化工具"""
        try:
            # 创建保存目录
            if not os.path.exists(self.config["SAVE_PATH"]):
                os.makedirs(self.config["SAVE_PATH"], exist_ok=True)
            
            # 读取标题
            titles = []
            if file_path and os.path.exists(file_path):
                titles = title_manager.read_titles_from_file(file_path)
                logger.info(f"从文件 {file_path} 读取标题")
            elif paste_text:
                titles = title_manager.read_titles_from_paste(paste_text)
                logger.info("从粘贴文本读取标题")
            elif os.path.exists(self.config["QUESTION_FILE"]):
                titles = title_manager.read_titles_from_file(self.config["QUESTION_FILE"])
                logger.info(f"从默认文件 {self.config['QUESTION_FILE']} 读取标题")
            else:
                logger.warning(f"未找到标题文件: {self.config['QUESTION_FILE']}")
                # 尝试交互式输入
                paste_text = self._get_user_input()
                if paste_text:
                    titles = title_manager.read_titles_from_paste(paste_text)
                    logger.info("从交互式输入读取标题")
                else:
                    return False
            
            if not titles:
                logger.warning("未读取到标题")
                return False
            
            # 去重
            self.tasks = title_manager.get_task_queue()
            logger.info(f"任务队列已生成，共 {len(self.tasks)} 个任务")
            
            # 连接浏览器
            browser = browser_manager.connect_to_browser(
                self.config["BROWSER_TYPE"],
                self.config["DEBUG_PORT"],
                self.config["INSTANCE_ID"]
            )
            
            if not browser:
                logger.error("连接浏览器失败")
                return False
            
            # 启动剪贴板监听
            clipboard_integration.set_save_folder(self.config["SAVE_PATH"])
            clipboard_integration.start_watching()
            
            logger.info("工具初始化完成")
            return True
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            return False
    
    def process_task(self, title: str) -> bool:
        """处理单个任务"""
        try:
            # 获取页面
            page = browser_manager.get_or_create_page(self.config["INSTANCE_ID"])
            if not page:
                logger.error("获取页面失败")
                return False
            
            # 初始化AI自动化
            ai = AIAutomation(page)
            ai.set_continue_max_click(self.config["CONTINUE_MAX_CLICK"])
            ai.set_wait_stable_time(self.config["WAIT_STABLE_TIME"])
            
            # 发送消息
            retry_count = 0
            while retry_count < self.config["RETRY_COUNT"]:
                if ai.send_message(title):
                    break
                retry_count += 1
                logger.warning(f"发送消息失败，重试 {retry_count}/{self.config['RETRY_COUNT']}")
                time.sleep(2)
            
            if retry_count >= self.config["RETRY_COUNT"]:
                logger.error(f"发送消息失败，已达到最大重试次数")
                return False
            
            # 监控输出
            retry_count = 0
            while retry_count < self.config["RETRY_COUNT"]:
                if ai.monitor_output():
                    break
                retry_count += 1
                logger.warning(f"监控输出失败，重试 {retry_count}/{self.config['RETRY_COUNT']}")
                time.sleep(2)
            
            if retry_count >= self.config["RETRY_COUNT"]:
                logger.error(f"监控输出失败，已达到最大重试次数")
                return False
            
            # 设置当前标题用于剪贴板保存
            clipboard_integration.set_current_title(title)
            
            # 等待剪贴板内容
            content = clipboard_integration.wait_for_clipboard_content()
            if not content:
                logger.error("未获取到剪贴板内容")
                return False
            
            # 等待保存完成
            time.sleep(2)
            
            logger.info(f"任务处理完成: {title}")
            return True
        except Exception as e:
            logger.error(f"处理任务失败: {e}")
            return False
    
    def run(self, file_path: Optional[str] = None, paste_text: Optional[str] = None):
        """运行工具"""
        try:
            if not self.initialize(file_path, paste_text):
                logger.error("初始化失败，无法运行")
                return
            
            self.is_running = True
            self.current_task_index = 0
            
            while self.is_running and self.current_task_index < len(self.tasks):
                title = self.tasks[self.current_task_index]
                logger.info(f"正在处理任务 {self.current_task_index + 1}/{len(self.tasks)}: {title}")
                
                success = self.process_task(title)
                self.results.append({"title": title, "success": success})
                
                self.current_task_index += 1
                
                # 避免操作过快
                if self.current_task_index < len(self.tasks):
                    time.sleep(2)
            
            logger.info("所有任务处理完成")
            self.print_summary()
        except KeyboardInterrupt:
            logger.info("用户终止程序")
        except Exception as e:
            logger.error(f"运行失败: {e}")
        finally:
            self.cleanup()
    
    def print_summary(self):
        """打印运行摘要"""
        total = len(self.results)
        success = sum(1 for r in self.results if r["success"])
        failure = total - success
        
        logger.info(f"运行摘要:")
        logger.info(f"总任务数: {total}")
        logger.info(f"成功: {success}")
        logger.info(f"失败: {failure}")
        
        if failure > 0:
            logger.info("失败任务:")
            for r in self.results:
                if not r["success"]:
                    logger.info(f"  - {r['title']}")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 停止剪贴板监听
            clipboard_integration.stop_watching()
            
            # 关闭浏览器
            browser_manager.close_all()
            
            logger.info("资源已清理")
        except Exception as e:
            logger.error(f"清理资源失败: {e}")
    
    def stop(self):
        """停止运行"""
        self.is_running = False
        logger.info("程序已停止")
    
    def _get_user_input(self) -> Optional[str]:
        """获取用户交互式输入"""
        print("\n未找到标题文件，请直接粘贴标题（每行一个，按Ctrl+D结束输入）:")
        print("=" * 60)
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        print("=" * 60)
        input_text = "\n".join(lines)
        if input_text.strip():
            return input_text
        return None

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="AI网页全自动批量处理工具")
    parser.add_argument("file", nargs="?", help="标题文件路径")
    parser.add_argument("--paste", action="store_true", help="从剪贴板粘贴标题")
    args = parser.parse_args()
    
    tool = AIAutomationTool()
    
    # 处理命令行参数
    file_path = args.file
    paste_text = None
    
    if args.paste:
        try:
            import pyperclip
            paste_text = pyperclip.paste()
            if not paste_text:
                print("剪贴板为空")
                exit(1)
        except Exception as e:
            print(f"读取剪贴板失败: {e}")
            exit(1)
    
    tool.run(file_path, paste_text)