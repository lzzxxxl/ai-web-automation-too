import os
import sys
import threading
import json
import logging
from datetime import datetime

try:
    import customtkinter as ctk
    from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkEntry, CTkComboBox, CTkTextbox, CTkProgressBar, CTkScrollableFrame, CTkTabview, CTkCheckBox, CTkOptionMenu
except ImportError:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    ctk = None

try:
    from pystray import MenuItem as item
    import pystray
    from PIL import Image, ImageDraw
    has_tray = True
except ImportError:
    has_tray = False

from browser_manager import browser_manager
from title_manager import title_manager
from ai_automation import AIAutomation
from clipboard_integration import clipboard_integration
from task_manager import task_manager

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        if hasattr(self.text_widget, 'after'):
            self.text_widget.after(0, self._append_text, msg)
    
    def _append_text(self, msg):
        if hasattr(self.text_widget, 'insert'):
            if hasattr(self.text_widget, 'configure'):
                self.text_widget.configure(state='normal')
            self.text_widget.insert('end', msg + '\n')
            self.text_widget.see('end')
            if hasattr(self.text_widget, 'configure'):
                self.text_widget.configure(state='disabled')

class ModernAIAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI网页全自动批量处理工具")
        self.root.geometry("1100x800")
        
        if ctk:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
        
        self.config_file = "config.json"
        self.config = self.load_config()
        self.is_running = False
        self.tool = None
        self.tray_icon = None
        
        self.setup_ui()
        self.setup_logging()
        self.setup_shortcuts()
        if has_tray:
            self.setup_tray_icon()
    
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
        if ctk:
            self.setup_ctk_ui()
        else:
            self.setup_tk_ui()
    
    def setup_ctk_ui(self):
        main_container = CTkFrame(self.root, corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        header = CTkFrame(main_container, height=70, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        
        header_left = CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", padx=20, pady=10)
        
        title_label = CTkLabel(header_left, text="🤖 AI网页全自动批量处理工具", 
                                font=("Microsoft YaHei", 24, "bold"))
        title_label.pack()
        
        header_right = CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right", padx=20, pady=10)
        
        self.theme_button = CTkButton(header_right, text="☀️ 浅色模式", 
                                     command=self.toggle_theme, width=120, height=30)
        self.theme_button.pack(side="right", padx=10)
        
        tabview = CTkTabview(main_container)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        config_tab = tabview.add("⚙️ 配置")
        self.setup_config_tab_ctk(config_tab)
        
        browser_tab = tabview.add("🌐 浏览器")
        self.setup_browser_tab_ctk(browser_tab)
        
        titles_tab = tabview.add("📝 标题")
        self.setup_titles_tab_ctk(titles_tab)
        
        tasks_tab = tabview.add("📋 任务")
        self.setup_tasks_tab_ctk(tasks_tab)
        
        run_tab = tabview.add("▶️ 运行")
        self.setup_run_tab_ctk(run_tab)
    
    def setup_config_tab_ctk(self, parent):
        scroll_frame = CTkScrollableFrame(parent, label_text="配置参数")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        row = 0
        
        self.create_label_ctk(scroll_frame, "浏览器类型:", row, 0)
        self.browser_type = CTkComboBox(scroll_frame, values=["chrome", "edge", "firefox"], state="readonly", width=300)
        self.browser_type.set(self.config["BROWSER_TYPE"])
        self.browser_type.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, "调试端口:", row, 0)
        self.debug_port = CTkEntry(scroll_frame, placeholder_text="9222", width=300)
        self.debug_port.insert(0, str(self.config["DEBUG_PORT"]))
        self.debug_port.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, "浏览器实例ID:", row, 0)
        self.instance_id = CTkEntry(scroll_frame, placeholder_text="default", width=300)
        self.instance_id.insert(0, "default")
        self.instance_id.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, "标题文件:", row, 0)
        file_frame = CTkFrame(scroll_frame, fg_color="transparent")
        file_frame.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        
        self.question_file = CTkEntry(file_frame, placeholder_text="选择标题文件", width=220)
        self.question_file.insert(0, self.config["QUESTION_FILE"])
        self.question_file.pack(side="left", padx=(0, 10))
        
        CTkButton(file_frame, text="📁 浏览", command=self.browse_file, width=70).pack(side="left")
        row += 1
        
        self.create_label_ctk(scroll_frame, "保存路径:", row, 0)
        path_frame = CTkFrame(scroll_frame, fg_color="transparent")
        path_frame.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        
        self.save_path = CTkEntry(path_frame, placeholder_text="选择保存路径", width=220)
        self.save_path.insert(0, self.config["SAVE_PATH"])
        self.save_path.pack(side="left", padx=(0, 10))
        
        CTkButton(path_frame, text="📁 浏览", command=self.browse_path, width=70).pack(side="left")
        row += 1
        
        self.create_label_ctk(scroll_frame, "最大点击继续生成次数:", row, 0)
        self.continue_max_click = CTkEntry(scroll_frame, placeholder_text="10", width=300)
        self.continue_max_click.insert(0, str(self.config["CONTINUE_MAX_CLICK"]))
        self.continue_max_click.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, "内容稳定判定时间(秒):", row, 0)
        self.wait_stable_time = CTkEntry(scroll_frame, placeholder_text="5", width=300)
        self.wait_stable_time.insert(0, str(self.config["WAIT_STABLE_TIME"]))
        self.wait_stable_time.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, "重试次数:", row, 0)
        self.retry_count = CTkEntry(scroll_frame, placeholder_text="3", width=300)
        self.retry_count.insert(0, str(self.config["RETRY_COUNT"]))
        self.retry_count.grid(row=row, column=1, sticky="w", pady=10, padx=10)
        row += 1
        
        CTkButton(scroll_frame, text="💾 保存配置", command=self.save_current_config, 
                   width=200, height=40, font=("Microsoft YaHei", 14)).grid(
            row=row, column=0, columnspan=2, pady=20)
    
    def create_label_ctk(self, parent, text, row, col):
        CTkLabel(parent, text=text, font=('Microsoft YaHei', 12)).grid(
            row=row, column=col, sticky='e', pady=10, padx=10)
    
    def setup_browser_tab_ctk(self, parent):
        scroll_frame = CTkScrollableFrame(parent, label_text='浏览器管理')
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        row = 0
        
        self.create_label_ctk(scroll_frame, '浏览器类型:', row, 0)
        self.browser_type_browser = CTkComboBox(scroll_frame, values=['chrome', 'edge', 'firefox'], state='readonly', width=300)
        self.browser_type_browser.set(self.config['BROWSER_TYPE'])
        self.browser_type_browser.grid(row=row, column=1, sticky='w', pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, '调试端口:', row, 0)
        self.debug_port_browser = CTkEntry(scroll_frame, placeholder_text='9222', width=300)
        self.debug_port_browser.insert(0, str(self.config['DEBUG_PORT']))
        self.debug_port_browser.grid(row=row, column=1, sticky='w', pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, '浏览器实例ID:', row, 0)
        self.instance_id_browser = CTkEntry(scroll_frame, placeholder_text='default', width=300)
        self.instance_id_browser.insert(0, 'default')
        self.instance_id_browser.grid(row=row, column=1, sticky='w', pady=10, padx=10)
        row += 1
        
        # 浏览器操作按钮
        btn_frame = CTkFrame(scroll_frame, fg_color='transparent')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20, padx=10)
        
        CTkButton(btn_frame, text='🚀 启动浏览器', command=self.start_browser, 
                  width=150, height=40, font=('Microsoft YaHei', 14)).pack(side='left', padx=10)
        
        CTkButton(btn_frame, text='🔗 连接浏览器', command=self.connect_browser, 
                  width=150, height=40, font=('Microsoft YaHei', 14)).pack(side='left', padx=10)
        
        CTkButton(btn_frame, text='❌ 关闭浏览器', command=self.close_browser, 
                  width=150, height=40, font=('Microsoft YaHei', 14), fg_color='#ef4444', hover_color='#dc2626').pack(side='left', padx=10)
        row += 1
        
        # 浏览器状态
        self.browser_status = CTkLabel(scroll_frame, text='📊 浏览器状态: 未连接', 
                                      font=('Microsoft YaHei', 12))
        self.browser_status.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
    
    def setup_tasks_tab_ctk(self, parent):
        scroll_frame = CTkScrollableFrame(parent, label_text='任务管理')
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 任务输入
        row = 0
        self.create_label_ctk(scroll_frame, '任务标题:', row, 0)
        self.task_title = CTkEntry(scroll_frame, placeholder_text='输入任务标题', width=300)
        self.task_title.grid(row=row, column=1, sticky='w', pady=10, padx=10)
        row += 1
        
        self.create_label_ctk(scroll_frame, '优先级:', row, 0)
        self.task_priority = CTkComboBox(scroll_frame, values=['1', '2', '3', '4', '5'], state='readonly', width=300)
        self.task_priority.set('3')
        self.task_priority.grid(row=row, column=1, sticky='w', pady=10, padx=10)
        row += 1
        
        # 任务操作按钮
        btn_frame = CTkFrame(scroll_frame, fg_color='transparent')
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20, padx=10)
        
        CTkButton(btn_frame, text='➕ 添加任务', command=self.add_task, 
                  width=120, height=35, font=('Microsoft YaHei', 12)).pack(side='left', padx=10)
        
        CTkButton(btn_frame, text='🗑️ 清空任务', command=self.clear_tasks, 
                  width=120, height=35, font=('Microsoft YaHei', 12), fg_color='#ef4444', hover_color='#dc2626').pack(side='left', padx=10)
        
        CTkButton(btn_frame, text='📥 导入任务', command=self.import_tasks, 
                  width=120, height=35, font=('Microsoft YaHei', 12)).pack(side='left', padx=10)
        
        CTkButton(btn_frame, text='📤 导出任务', command=self.export_tasks, 
                  width=120, height=35, font=('Microsoft YaHei', 12)).pack(side='left', padx=10)
        row += 1
        
        # 任务列表
        CTkLabel(scroll_frame, text='任务列表:', font=('Microsoft YaHei', 14)).grid(row=row, column=0, columnspan=2, sticky='w', pady=10, padx=10)
        row += 1
        
        self.tasks_list = CTkTextbox(scroll_frame, height=200, font=('Consolas', 11), state='disabled')
        self.tasks_list.grid(row=row, column=0, columnspan=2, sticky='we', pady=10, padx=10)
        row += 1
        
        # 任务统计
        self.tasks_stats = CTkLabel(scroll_frame, text='📊 任务统计: 0 个任务', 
                                   font=('Microsoft YaHei', 12))
        self.tasks_stats.grid(row=row, column=0, columnspan=2, pady=10, padx=10)
        
        # 加载任务列表
        self.update_tasks_list()
    
    def setup_titles_tab_ctk(self, parent):
        CTkLabel(parent, text="在此处粘贴标题（每行一个）", 
                font=("Microsoft YaHei", 14)).pack(pady=(10, 5))
        
        self.titles_text = CTkTextbox(parent, height=300, font=("Consolas", 11))
        self.titles_text.pack(fill="both", expand=True, padx=20, pady=10)
        
        if os.path.exists(self.config["QUESTION_FILE"]):
            try:
                with open(self.config["QUESTION_FILE"], 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.titles_text.insert("1.0", content)
            except:
                pass
    
    def setup_run_tab_ctk(self, parent):
        btn_frame = CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        self.start_btn = CTkButton(btn_frame, text="▶️ 开始运行", command=self.start_tool,
                                   height=50, font=("Microsoft YaHei", 16, "bold"))
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.stop_btn = CTkButton(btn_frame, text="⏹️ 停止", command=self.stop_tool,
                                  height=50, font=("Microsoft YaHei", 16, "bold"),
                                  state="disabled", fg_color="#ef4444", hover_color="#dc2626")
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        CTkLabel(parent, text="📊 运行日志", font=("Microsoft YaHei", 14)).pack(pady=(20, 5))
        
        self.log_text = CTkTextbox(parent, height=250, font=("Consolas", 10), state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.progress = CTkProgressBar(parent, height=15)
        self.progress.pack(fill="x", padx=20, pady=(10, 20))
        self.progress.set(0)
    
    def setup_tk_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        config_frame = ttk.Frame(notebook, padding="10")
        notebook.add(config_frame, text="配置")
        
        titles_frame = ttk.Frame(notebook, padding="10")
        notebook.add(titles_frame, text="标题")
        
        run_frame = ttk.Frame(notebook, padding="10")
        notebook.add(run_frame, text="运行")
        
        self.setup_config_tab_tk(config_frame)
        self.setup_titles_tab_tk(titles_frame)
        self.setup_run_tab_tk(run_frame)
    
    def setup_config_tab_tk(self, parent):
        row = 0
        
        ttk.Label(parent, text="浏览器类型:").grid(row=row, column=0, sticky=tk.E, pady=5)
        self.browser_type = ttk.Combobox(parent, values=["chrome", "edge", "firefox"], state="readonly", width=30)
        self.browser_type.set(self.config["BROWSER_TYPE"])
        self.browser_type.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(parent, text="调试端口:").grid(row=row, column=0, sticky=tk.E, pady=5)
        self.debug_port = ttk.Entry(parent, width=33)
        self.debug_port.insert(0, str(self.config["DEBUG_PORT"]))
        self.debug_port.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(parent, text="标题文件:").grid(row=row, column=0, sticky=tk.E, pady=5)
        file_frame = ttk.Frame(parent)
        file_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        
        self.question_file = ttk.Entry(file_frame, width=25)
        self.question_file.insert(0, self.config["QUESTION_FILE"])
        self.question_file.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(file_frame, text="浏览", command=self.browse_file).pack(side=tk.LEFT)
        row += 1
        
        ttk.Label(parent, text="保存路径:").grid(row=row, column=0, sticky=tk.E, pady=5)
        path_frame = ttk.Frame(parent)
        path_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        
        self.save_path = ttk.Entry(path_frame, width=25)
        self.save_path.insert(0, self.config["SAVE_PATH"])
        self.save_path.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(path_frame, text="浏览", command=self.browse_path).pack(side=tk.LEFT)
        row += 1
        
        ttk.Label(parent, text="最大点击继续生成次数:").grid(row=row, column=0, sticky=tk.E, pady=5)
        self.continue_max_click = ttk.Entry(parent, width=33)
        self.continue_max_click.insert(0, str(self.config["CONTINUE_MAX_CLICK"]))
        self.continue_max_click.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(parent, text="内容稳定判定时间(秒):").grid(row=row, column=0, sticky=tk.E, pady=5)
        self.wait_stable_time = ttk.Entry(parent, width=33)
        self.wait_stable_time.insert(0, str(self.config["WAIT_STABLE_TIME"]))
        self.wait_stable_time.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Label(parent, text="重试次数:").grid(row=row, column=0, sticky=tk.E, pady=5)
        self.retry_count = ttk.Entry(parent, width=33)
        self.retry_count.insert(0, str(self.config["RETRY_COUNT"]))
        self.retry_count.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        ttk.Button(parent, text="保存配置", command=self.save_current_config).grid(
            row=row, column=0, columnspan=2, pady=20)
    
    def setup_titles_tab_tk(self, parent):
        ttk.Label(parent, text="在此处粘贴标题（每行一个）:").pack(anchor=tk.W, pady=5)
        
        self.titles_text = scrolledtext.ScrolledText(parent, height=15, wrap=tk.WORD)
        self.titles_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        if os.path.exists(self.config["QUESTION_FILE"]):
            try:
                with open(self.config["QUESTION_FILE"], 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.titles_text.insert("1.0", content)
            except:
                pass
    
    def setup_run_tab_tk(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="开始运行", command=self.start_tool)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_tool, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        ttk.Label(parent, text="运行日志:").pack(anchor=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(parent, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.progress = ttk.Progressbar(parent, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)
    
    def setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)
    
    def browse_file(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="选择标题文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.question_file.delete(0, tk.END if not ctk else "0")
            self.question_file.insert(0 if not ctk else "0", filename)
    
    def browse_path(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="选择保存路径")
        if path:
            self.save_path.delete(0, tk.END if not ctk else "0")
            self.save_path.insert(0 if not ctk else "0", path)
    
    def save_current_config(self):
        self.config["BROWSER_TYPE"] = self.browser_type.get()
        self.config["DEBUG_PORT"] = int(self.debug_port.get())
        self.config["INSTANCE_ID"] = self.instance_id.get()
        self.config["QUESTION_FILE"] = self.question_file.get()
        self.config["SAVE_PATH"] = self.save_path.get()
        self.config["CONTINUE_MAX_CLICK"] = int(self.continue_max_click.get())
        self.config["WAIT_STABLE_TIME"] = int(self.wait_stable_time.get())
        self.config["RETRY_COUNT"] = int(self.retry_count.get())
        self.save_config()
        
        if ctk:
            from tkinter import messagebox
        messagebox.showinfo("成功", "配置已保存！")
    
    def start_tool(self):
        self.save_current_config()
        
        paste_text = self.titles_text.get("1.0", "end").strip()
        file_path = self.question_file.get()
        
        self.is_running = True
        if ctk:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.run_tool, args=(file_path, paste_text))
        thread.daemon = True
        thread.start()
    
    def stop_tool(self):
        self.is_running = False
        if ctk:
            self.log_text.configure(state='normal')
        self.log_text.insert("end" if ctk else tk.END, "正在停止...\n")
        self.log_text.see("end" if ctk else tk.END)
        if ctk:
            self.log_text.configure(state='disabled')
    
    def run_tool(self, file_path, paste_text):
        try:
            from main import AIAutomationTool
            
            self.tool = AIAutomationTool(self.config_file)
            self.tool.config = self.config
            
            if not self.tool.initialize(file_path if os.path.exists(file_path) else None, paste_text if paste_text else None):
                if ctk:
                    from tkinter import messagebox
                self.root.after(0, lambda: messagebox.showerror("错误", "初始化失败，请检查日志"))
                self.root.after(0, self.reset_buttons)
                return
            
            self.tool.is_running = True
            self.tool.current_task_index = 0
            
            self.progress['maximum'] = len(self.tool.tasks)
            self.progress.set(0) if ctk else None
            
            while self.is_running and self.tool.current_task_index < len(self.tool.tasks):
                title = self.tool.tasks[self.tool.current_task_index]
                
                self.tool.process_task(title)
                self.tool.current_task_index += 1
                
                self.root.after(0, lambda v=self.tool.current_task_index: self._update_progress(v))
                
                if self.tool.current_task_index < len(self.tool.tasks):
                    import time
                    time.sleep(2)
            
            self.tool.print_summary()
            self.tool.cleanup()
            
            if ctk:
                from tkinter import messagebox
            self.root.after(0, lambda: messagebox.showinfo("完成", "所有任务处理完成！"))
            
        except Exception as e:
            logging.error(f"运行失败: {e}")
            if ctk:
                from tkinter import messagebox
            self.root.after(0, lambda: messagebox.showerror("错误", f"运行失败: {e}"))
        finally:
            self.root.after(0, self.reset_buttons)
    
    def _update_progress(self, value):
        if ctk:
            self.progress.set(value / self.progress['maximum'])
        else:
            self.progress['value'] = value
    
    def reset_buttons(self):
        if ctk:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def setup_shortcuts(self):
        if ctk:
            self.root.bind('<Control-s>', lambda e: self.save_current_config())
            self.root.bind('<Control-q>', lambda e: self.exit_app())
            self.root.bind('<F5>', lambda e: self.start_tool())
            self.root.bind('<F6>', lambda e: self.stop_tool())
        else:
            self.root.bind('<Control-s>', lambda e: self.save_current_config())
            self.root.bind('<Control-q>', lambda e: self.exit_app())
            self.root.bind('<F5>', lambda e: self.start_tool())
            self.root.bind('<F6>', lambda e: self.stop_tool())
    
    def setup_tray_icon(self):
        try:
            def create_image():    
                width = 64
                height = 64
                image = Image.new('RGB', (width, height), color=(20, 20, 60))
                d = ImageDraw.Draw(image)
                d.text((10, 10), "🤖", fill=(255, 255, 255), font_size=40)
                return image
            
            menu = (
                item('显示窗口', lambda: self.show_window()),
                item('退出', lambda: self.exit_app())
            )
            
            self.tray_icon = pystray.Icon('AI自动化工具', create_image(), 'AI网页全自动批量处理工具', menu)
            
            def run_tray():
                try:
                    self.tray_icon.run()
                except Exception:
                    pass
            
            threading.Thread(target=run_tray, daemon=True).start()
        except Exception:
            # 在无头环境中跳过托盘图标
            pass
    
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
    
    def exit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()
    
    def toggle_theme(self):
        if ctk:
            try:
                current_mode = ctk.get_appearance_mode()
                new_mode = "light" if current_mode == "dark" else "dark"
                ctk.set_appearance_mode(new_mode)
                if hasattr(self, 'theme_button'):
                    self.theme_button.configure(text="🌙 深色模式" if new_mode == "light" else "☀️ 浅色模式")
                logger.info(f"主题已切换为: {new_mode}")
            except Exception as e:
                logger.error(f"切换主题失败: {e}")
    
    def start_browser(self):
        """启动浏览器"""
        try:
            browser_type = self.browser_type_browser.get()
            debug_port = int(self.debug_port_browser.get())
            
            # 启动浏览器
            success = browser_manager.open_browser_with_debug(browser_type, debug_port)
            
            if success:
                self.browser_status.configure(text=f"📊 浏览器状态: {browser_type} 已启动")
                if ctk:
                    from tkinter import messagebox
                messagebox.showinfo("成功", f"{browser_type}浏览器已成功启动！")
            else:
                self.browser_status.configure(text="📊 浏览器状态: 启动失败")
                if ctk:
                    from tkinter import messagebox
                messagebox.showerror("错误", "浏览器启动失败，请检查日志！")
        except Exception as e:
            logging.error(f"启动浏览器失败: {e}")
            self.browser_status.configure(text="📊 浏览器状态: 启动失败")
            if ctk:
                from tkinter import messagebox
            messagebox.showerror("错误", f"启动浏览器失败: {e}")
    
    def connect_browser(self):
        """连接浏览器"""
        try:
            browser_type = self.browser_type_browser.get()
            debug_port = int(self.debug_port_browser.get())
            instance_id = self.instance_id_browser.get()
            
            # 连接浏览器（不自动启动）
            browser = browser_manager.connect_to_browser(browser_type, debug_port, instance_id)
            
            if browser:
                self.browser_status.configure(text=f"📊 浏览器状态: 已连接到 {browser_type} 实例 {instance_id}")
                if ctk:
                    from tkinter import messagebox
                messagebox.showinfo("成功", f"已成功连接到{browser_type}浏览器！")
            else:
                self.browser_status.configure(text="📊 浏览器状态: 连接失败")
                if ctk:
                    from tkinter import messagebox
                messagebox.showerror("错误", "浏览器连接失败，请先点击'启动浏览器'按钮启动浏览器！")
        except Exception as e:
            logging.error(f"连接浏览器失败: {e}")
            self.browser_status.configure(text="📊 浏览器状态: 连接失败")
            if ctk:
                from tkinter import messagebox
            messagebox.showerror("错误", f"连接浏览器失败: {e}")
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            instance_id = self.instance_id_browser.get()
            
            # 关闭浏览器
            browser_manager.close_browser(instance_id)
            
            self.browser_status.configure(text="📊 浏览器状态: 已关闭")
            if ctk:
                from tkinter import messagebox
            messagebox.showinfo("成功", f"浏览器实例 {instance_id} 已关闭！")
        except Exception as e:
            logging.error(f"关闭浏览器失败: {e}")
            if ctk:
                from tkinter import messagebox
            messagebox.showerror("错误", f"关闭浏览器失败: {e}")
    
    def add_task(self):
        """添加任务"""
        try:
            title = self.task_title.get().strip()
            if not title:
                if ctk:
                    from tkinter import messagebox
                messagebox.showwarning("警告", "请输入任务标题！")
                return
            
            priority = int(self.task_priority.get())
            task = task_manager.add_task(title, priority)
            
            self.task_title.delete(0, 'end')
            self.update_tasks_list()
            
            if ctk:
                from tkinter import messagebox
            messagebox.showinfo("成功", "任务添加成功！")
        except Exception as e:
            logging.error(f"添加任务失败: {e}")
            if ctk:
                from tkinter import messagebox
            messagebox.showerror("错误", f"添加任务失败: {e}")
    
    def clear_tasks(self):
        """清空任务"""
        try:
            if ctk:
                from tkinter import messagebox
            if messagebox.askyesno("确认", "确定要清空所有任务吗？"):
                task_manager.clear_tasks()
                self.update_tasks_list()
                messagebox.showinfo("成功", "任务已清空！")
        except Exception as e:
            logging.error(f"清空任务失败: {e}")
            if ctk:
                from tkinter import messagebox
            messagebox.showerror("错误", f"清空任务失败: {e}")
    
    def import_tasks(self):
        """导入任务"""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="选择任务文件",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                task_manager.import_tasks(filename)
                self.update_tasks_list()
                if ctk:
                    from tkinter import messagebox
                messagebox.showinfo("成功", f"任务导入成功！")
        except Exception as e:
            logging.error(f"导入任务失败: {e}")
            if ctk:
                from tkinter import messagebox
            messagebox.showerror("错误", f"导入任务失败: {e}")
    
    def export_tasks(self):
        """导出任务"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                title="保存任务文件",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
            )
            if filename:
                task_manager.export_tasks(filename)
                if ctk:
                    from tkinter import messagebox
                messagebox.showinfo("成功", f"任务导出成功！")
        except Exception as e:
            logging.error(f"导出任务失败: {e}")
            if ctk:
                from tkinter import messagebox
            messagebox.showerror("错误", f"导出任务失败: {e}")
    
    def update_tasks_list(self):
        """更新任务列表"""
        try:
            tasks = task_manager.get_tasks()
            stats = task_manager.get_task_count()
            
            # 更新任务列表
            self.tasks_list.configure(state='normal')
            self.tasks_list.delete('1.0', 'end')
            
            for i, task in enumerate(tasks):
                status_emoji = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(task.status, '📋')
                
                self.tasks_list.insert('end', f"{i+1}. {status_emoji} [{task.status}] 优先级: {task.priority} - {task.title}\n")
            
            self.tasks_list.configure(state='disabled')
            
            # 更新任务统计
            self.tasks_stats.configure(
                text=f"📊 任务统计: 总计 {stats['total']} 个任务 | 待处理 {stats['pending']} | 运行中 {stats['running']} | 已完成 {stats['completed']} | 失败 {stats['failed']}"
            )
        except Exception as e:
            logging.error(f"更新任务列表失败: {e}")

if __name__ == "__main__":
    if ctk:
        root = CTk()
    else:
        root = tk.Tk()
    app = ModernAIAutomationGUI(root)
    root.mainloop()
