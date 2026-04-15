import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import logging
from datetime import datetime

from browser_manager import browser_manager
from title_manager import title_manager
from ai_automation import AIAutomation
from clipboard_integration import clipboard_integration

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self._append_text, msg)
    
    def _append_text(self, msg):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

class AIAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI网页全自动批量处理工具")
        self.root.geometry("900x700")
        
        self.config_file = "config.json"
        self.config = self.load_config()
        self.is_running = False
        self.tool = None
        
        self.setup_ui()
        self.setup_logging()
    
    def load_config(self):
        default_config = {
            "BROWSER_TYPE": "chrome",
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
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except:
                pass
        return default_config
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        ttk.Label(main_frame, text="浏览器类型:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.browser_type = ttk.Combobox(main_frame, values=["chrome", "edge"], state="readonly")
        self.browser_type.set(self.config["BROWSER_TYPE"])
        self.browser_type.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="调试端口:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.debug_port = ttk.Entry(main_frame)
        self.debug_port.insert(0, str(self.config["DEBUG_PORT"]))
        self.debug_port.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="标题文件:").grid(row=row, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        self.question_file = ttk.Entry(file_frame)
        self.question_file.insert(0, self.config["QUESTION_FILE"])
        self.question_file.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(file_frame, text="浏览", command=self.browse_file).grid(row=0, column=1, padx=(5, 0))
        row += 1
        
        ttk.Label(main_frame, text="保存路径:").grid(row=row, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        self.save_path = ttk.Entry(path_frame)
        self.save_path.insert(0, self.config["SAVE_PATH"])
        self.save_path.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(path_frame, text="浏览", command=self.browse_path).grid(row=0, column=1, padx=(5, 0))
        row += 1
        
        ttk.Label(main_frame, text="最大点击继续生成次数:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.continue_max_click = ttk.Entry(main_frame)
        self.continue_max_click.insert(0, str(self.config["CONTINUE_MAX_CLICK"]))
        self.continue_max_click.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="内容稳定判定时间(秒):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.wait_stable_time = ttk.Entry(main_frame)
        self.wait_stable_time.insert(0, str(self.config["WAIT_STABLE_TIME"]))
        self.wait_stable_time.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(main_frame, text="重试次数:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.retry_count = ttk.Entry(main_frame)
        self.retry_count.insert(0, str(self.config["RETRY_COUNT"]))
        self.retry_count.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="或直接粘贴标题（每行一个）:").grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        self.titles_text = scrolledtext.ScrolledText(main_frame, height=8, wrap=tk.WORD)
        self.titles_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        row += 1
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="开始运行", command=self.start_tool)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_tool, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_config_btn = ttk.Button(btn_frame, text="保存配置", command=self.save_current_config)
        self.save_config_btn.pack(side=tk.LEFT, padx=5)
        row += 1
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        ttk.Label(main_frame, text="运行日志:").grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(row, weight=1)
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="选择标题文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.question_file.delete(0, tk.END)
            self.question_file.insert(0, filename)
    
    def browse_path(self):
        path = filedialog.askdirectory(title="选择保存路径")
        if path:
            self.save_path.delete(0, tk.END)
            self.save_path.insert(0, path)
    
    def save_current_config(self):
        self.config["BROWSER_TYPE"] = self.browser_type.get()
        self.config["DEBUG_PORT"] = int(self.debug_port.get())
        self.config["QUESTION_FILE"] = self.question_file.get()
        self.config["SAVE_PATH"] = self.save_path.get()
        self.config["CONTINUE_MAX_CLICK"] = int(self.continue_max_click.get())
        self.config["WAIT_STABLE_TIME"] = int(self.wait_stable_time.get())
        self.config["RETRY_COUNT"] = int(self.retry_count.get())
        self.save_config()
        messagebox.showinfo("成功", "配置已保存！")
    
    def start_tool(self):
        self.save_current_config()
        
        paste_text = self.titles_text.get("1.0", tk.END).strip()
        file_path = self.question_file.get()
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.run_tool, args=(file_path, paste_text))
        thread.daemon = True
        thread.start()
    
    def stop_tool(self):
        self.is_running = False
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "正在停止...\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def run_tool(self, file_path, paste_text):
        try:
            from main import AIAutomationTool
            
            self.tool = AIAutomationTool(self.config_file)
            self.tool.config = self.config
            
            if not self.tool.initialize(file_path if os.path.exists(file_path) else None, paste_text if paste_text else None):
                self.root.after(0, lambda: messagebox.showerror("错误", "初始化失败，请检查日志"))
                self.root.after(0, self.reset_buttons)
                return
            
            self.tool.is_running = True
            self.tool.current_task_index = 0
            
            self.progress['maximum'] = len(self.tool.tasks)
            self.progress['value'] = 0
            
            while self.is_running and self.tool.current_task_index < len(self.tool.tasks):
                title = self.tool.tasks[self.tool.current_task_index]
                
                self.tool.process_task(title)
                self.tool.current_task_index += 1
                
                self.root.after(0, lambda v=self.tool.current_task_index: self.progress.configure(value=v))
                
                if self.tool.current_task_index < len(self.tool.tasks):
                    import time
                    time.sleep(2)
            
            self.tool.print_summary()
            self.tool.cleanup()
            
            self.root.after(0, lambda: messagebox.showinfo("完成", "所有任务处理完成！"))
            
        except Exception as e:
            logging.error(f"运行失败: {e}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"运行失败: {e}"))
        finally:
            self.root.after(0, self.reset_buttons)
    
    def reset_buttons(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AIAutomationGUI(root)
    root.mainloop()
