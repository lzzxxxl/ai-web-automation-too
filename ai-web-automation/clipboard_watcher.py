import os
import re
import threading
import time
import json
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import pyperclip

def get_resource_path(relative_path):
    """获取资源文件的绝对路径（支持开发环境和 PyInstaller 打包后）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 创建的临时文件夹
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def get_icon_path():
    """获取图标路径"""
    # 尝试从资源路径获取（打包后）
    resource_icon = get_resource_path("zi.ico")
    if os.path.exists(resource_icon):
        return resource_icon
    
    # 尝试其他可能的路径
    possible_paths = [
        "zi.ico",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "zi.ico"),
        os.path.join(os.path.dirname(sys.executable), "zi.ico"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

CONFIG_FILE = "watcher_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"last_folder": "", "auto_save": True, "always_on_top": True, "theme": "pink"}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

THEMES = {
    "black": {
        "name": "黑色极简",
        "bg": "#0d0d0d",
        "surface": "#1a1a1a",
        "accent": "#60a5fa",
        "accent_hover": "#3b82f6",
        "text": "#f5f5f5",
        "text_muted": "#9ca3af",
        "border": "#2d2d2d",
        "success": "#4ade80",
        "warning": "#fbbf24",
        "error": "#f87171"
    },
    "white": {
        "name": "白色极简",
        "bg": "#fafafa",
        "surface": "#ffffff",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "text": "#1f2937",
        "text_muted": "#6b7280",
        "border": "#e5e7eb",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "error": "#ef4444"
    },
    "pink": {
        "name": "粉色",
        "bg": "#fdf2f8",
        "surface": "#ffffff",
        "accent": "#ec4899",
        "accent_hover": "#db2777",
        "text": "#374151",
        "text_muted": "#9ca3af",
        "border": "#fbcfe8",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444"
    }
}

class ClipboardWatcher:
    def __init__(self, folder_path, callback, interval=0.3):
        self.folder_path = folder_path
        self.callback = callback
        self.interval = interval
        self.running = False
        self.last_content = ""
        
    def extract_title_from_content(self, content):
        patterns = [
            r'原文章标题[：:]\s*([^\n]+?)(?:\s*-->\s*$|\.txt\s*-->\s*$)',
            r'原文件标题[：:]\s*([^\n]+?)(?:\s*-->\s*$|\.txt\s*-->\s*$)',
            r'title[：:]\s*([^\n<]+)',
            r'<title>(.+?)</title>',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                title = re.sub(r'\.txt$', '', title, flags=re.IGNORECASE)
                title = title.strip()
                if title and len(title) > 1:
                    return title
        
        lines = content.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 5 and len(line) < 100 and not line.startswith('```') and not line.startswith('<!--'):
                return line
        
        return None
    
    def clean_filename(self, title):
        """清洗标题用于文件名匹配 - 只保留中文、英文、数字"""
        # 只保留中文、英文、数字
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', title)
        return cleaned
    
    def normalize(self, text):
        """标准化文本：转小写"""
        return str(text).lower()
    
    def match_file(self, title):
        if not title:
            return None, 0
        
        if not self.folder_path or not os.path.exists(self.folder_path):
            return None, 0
        
        txt_files = [f for f in os.listdir(self.folder_path) if f.endswith('.txt')]
        if not txt_files:
            return None, 0
        
        clean_title = self.clean_filename(title)
        norm_title = self.normalize(clean_title)
        
        candidates = []
        for filename in txt_files:
            name_without_ext = os.path.splitext(filename)[0]
            clean_name = self.clean_filename(name_without_ext)
            norm_name = self.normalize(clean_name)
            
            if norm_title == norm_name:
                return filename, 1.0
            
            if norm_title in norm_name or norm_name in norm_title:
                candidates.append((filename, 0.5))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0]
        
        return None, 0
    
    def check_clipboard(self):
        try:
            current_content = pyperclip.paste()
            
            if current_content and current_content != self.last_content and len(current_content) > 30:
                self.last_content = current_content
                
                title = self.extract_title_from_content(current_content)
                
                if title:
                    matched_file, similarity = self.match_file(title)
                    
                    if matched_file and similarity == 1.0:
                        file_path = os.path.join(self.folder_path, matched_file)
                        self.callback(file_path, matched_file, title, current_content, True)
                    else:
                        self.callback(None, None, title, current_content, False, matched_file, similarity)
                else:
                    self.callback(None, None, "", current_content, False, None, 0)
                            
        except Exception as e:
            print(f"检查剪贴板出错: {e}")
    
    def run(self):
        self.running = True
        self.last_content = pyperclip.paste() or ""
        
        while self.running:
            self.check_clipboard()
            time.sleep(self.interval)
    
    def stop(self):
        self.running = False


class ModernApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("剪贴板自动保存")
        self.root.geometry("600x520")
        self.root.resizable(False, False)
        
        # 设置窗口图标
        self.set_window_icon()
        
        self.folder_path = ""
        self.watcher = None
        self.watcher_thread = None
        self.auto_save = tk.BooleanVar(value=True)
        self.always_on_top = tk.BooleanVar(value=True)
        self.theme_var = tk.StringVar(value="pink")
        self.is_running = False
        
        self.current_theme = "pink"
        
        self.setup_ui()
        self.load_last_folder()
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = get_icon_path()
            if icon_path:
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"设置图标失败: {e}")
        
    def setup_ui(self):
        self.root.configure(bg=THEMES[self.current_theme]["bg"])
        
        # 主容器
        main_frame = tk.Frame(self.root, bg=THEMES[self.current_theme]["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)
        
        # 标题
        title_frame = tk.Frame(main_frame, bg=THEMES[self.current_theme]["bg"])
        title_frame.pack(fill=tk.X, pady=(0, 16))
        
        tk.Label(
            title_frame, 
            text="剪贴板自动保存",
            font=("Microsoft YaHei", 20, "bold"),
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["accent"]
        ).pack(side=tk.LEFT)
        
        # 主题选择
        theme_frame = tk.Frame(main_frame, bg=THEMES[self.current_theme]["bg"])
        theme_frame.pack(fill=tk.X, pady=(0, 16))
        
        for theme_id, theme_data in THEMES.items():
            rb = tk.Radiobutton(
                theme_frame,
                text=theme_data["name"],
                variable=self.theme_var,
                value=theme_id,
                command=self.change_theme,
                font=("Microsoft YaHei", 10),
                bg=THEMES[self.current_theme]["bg"],
                fg=THEMES[self.current_theme]["text"],
                selectcolor=THEMES[self.current_theme]["surface"],
                activebackground=THEMES[self.current_theme]["bg"],
                cursor="hand2"
            )
            rb.pack(side=tk.LEFT, padx=(0, 16))
        
        # 文件夹选择区域
        folder_section = tk.Frame(main_frame, bg=THEMES[self.current_theme]["bg"])
        folder_section.pack(fill=tk.X, pady=(0, 12))
        
        self.folder_entry = tk.Entry(
            folder_section, 
            font=("Microsoft YaHei", 11),
            bg=THEMES[self.current_theme]["surface"],
            fg=THEMES[self.current_theme]["text"],
            insertbackground=THEMES[self.current_theme]["text"],
            relief=tk.FLAT,
            highlightthickness=1,
            highlightcolor=THEMES[self.current_theme]["accent"],
            highlightbackground=THEMES[self.current_theme]["border"]
        )
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.btn_folder = tk.Button(
            folder_section,
            text="选择",
            command=self.select_folder,
            font=("Microsoft YaHei", 10),
            bg=THEMES[self.current_theme]["surface"],
            fg=THEMES[self.current_theme]["text"],
            relief=tk.FLAT,
            padx=16,
            pady=4,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=0
        )
        self.btn_folder.pack(side=tk.LEFT)
        
        # 文件列表
        list_frame = tk.Frame(main_frame, bg=THEMES[self.current_theme]["border"])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        
        self.file_listbox = tk.Listbox(
            list_frame,
            font=("Microsoft YaHei", 10),
            bg=THEMES[self.current_theme]["surface"],
            fg=THEMES[self.current_theme]["text"],
            selectbackground=THEMES[self.current_theme]["accent"],
            selectforeground=THEMES[self.current_theme]["surface"],
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        scrollbar = tk.Scrollbar(list_frame, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 状态栏
        self.status_label = tk.Label(
            main_frame, 
            text="等待选择文件夹...",
            font=("Microsoft YaHei", 10),
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["text_muted"]
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 12))
        
        # 选项区域
        options_frame = tk.Frame(main_frame, bg=THEMES[self.current_theme]["bg"])
        options_frame.pack(fill=tk.X, pady=(0, 16))
        
        tk.Checkbutton(
            options_frame,
            text="自动保存",
            variable=self.auto_save,
            font=("Microsoft YaHei", 10),
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["text"],
            selectcolor=THEMES[self.current_theme]["surface"],
            activebackground=THEMES[self.current_theme]["bg"],
            cursor="hand2"
        ).pack(side=tk.LEFT)
        
        tk.Checkbutton(
            options_frame,
            text="窗口置顶",
            variable=self.always_on_top,
            command=self.toggle_topmost,
            font=("Microsoft YaHei", 10),
            bg=THEMES[self.current_theme]["bg"],
            fg=THEMES[self.current_theme]["text"],
            selectcolor=THEMES[self.current_theme]["surface"],
            activebackground=THEMES[self.current_theme]["bg"],
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=24)
        
        # 控制按钮
        btn_frame = tk.Frame(main_frame, bg=THEMES[self.current_theme]["bg"])
        btn_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.start_btn = tk.Button(
            btn_frame, 
            text="开始监听", 
            command=self.start_watching,
            font=("Microsoft YaHei", 12, "bold"),
            bg=THEMES[self.current_theme]["accent"],
            fg=THEMES[self.current_theme]["surface"],
            activebackground=THEMES[self.current_theme]["accent_hover"],
            relief=tk.FLAT,
            padx=32,
            pady=8,
            cursor="hand2",
            borderwidth=0
        )
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        
        self.stop_btn = tk.Button(
            btn_frame, 
            text="停止", 
            command=self.stop_watching,
            font=("Microsoft YaHei", 12, "bold"),
            bg=THEMES[self.current_theme]["surface"],
            fg=THEMES[self.current_theme]["text"],
            relief=tk.FLAT,
            padx=32,
            pady=8,
            cursor="hand2",
            borderwidth=1,
            highlightthickness=0,
            highlightbackground=THEMES[self.current_theme]["border"],
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        
        # 日志
        log_frame = tk.Frame(main_frame, bg=THEMES[self.current_theme]["border"])
        log_frame.pack(fill=tk.X)
        
        self.log_text = tk.Text(
            log_frame, 
            height=3, 
            font=("Consolas", 9),
            state=tk.DISABLED,
            bg=THEMES[self.current_theme]["surface"],
            fg=THEMES[self.current_theme]["text_muted"],
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0
        )
        self.log_text.pack(fill=tk.X, padx=1, pady=1)
    
    def change_theme(self):
        self.current_theme = self.theme_var.get()
        t = THEMES[self.current_theme]
        
        # 更新根窗口
        self.root.configure(bg=t["bg"])
        
        # 递归更新所有组件
        self._update_theme_recursive(self.root, t)
        
        # 保存配置
        config = load_config()
        config["theme"] = self.current_theme
        save_config(config)
    
    def _update_theme_recursive(self, parent, t):
        for widget in parent.winfo_children():
            widget_class = widget.winfo_class()
            
            try:
                if widget_class == "Frame":
                    widget.configure(bg=t["bg"])
                elif widget_class == "Label":
                    # 根据内容判断颜色
                    current_fg = widget.cget("fg")
                    if current_fg in [THEMES[k]["accent"] for k in THEMES]:
                        widget.configure(bg=t["bg"], fg=t["accent"])
                    elif current_fg in [THEMES[k]["text_muted"] for k in THEMES]:
                        widget.configure(bg=t["bg"], fg=t["text_muted"])
                    else:
                        widget.configure(bg=t["bg"], fg=t["text"])
                elif widget_class == "Entry":
                    widget.configure(
                        bg=t["surface"], 
                        fg=t["text"], 
                        insertbackground=t["text"],
                        highlightcolor=t["accent"],
                        highlightbackground=t["border"]
                    )
                elif widget_class == "Listbox":
                    widget.configure(
                        bg=t["surface"], 
                        fg=t["text"], 
                        selectbackground=t["accent"],
                        selectforeground=t["surface"]
                    )
                elif widget_class == "Text":
                    widget.configure(bg=t["surface"], fg=t["text_muted"])
                elif widget_class == "Checkbutton":
                    widget.configure(
                        bg=t["bg"], 
                        fg=t["text"], 
                        selectcolor=t["surface"],
                        activebackground=t["bg"]
                    )
                elif widget_class == "Radiobutton":
                    widget.configure(
                        bg=t["bg"], 
                        fg=t["text"], 
                        selectcolor=t["surface"],
                        activebackground=t["bg"]
                    )
                elif widget_class == "Button":
                    text = widget.cget("text")
                    if text == "开始监听":
                        widget.configure(bg=t["accent"], fg=t["surface"], activebackground=t["accent_hover"])
                    elif text == "停止":
                        if widget.cget("state") == "normal":
                            widget.configure(
                                bg=t["surface"], 
                                fg=t["text"],
                                highlightbackground=t["border"]
                            )
                        else:
                            widget.configure(
                                bg=t["surface"], 
                                fg=t["text_muted"],
                                highlightbackground=t["border"]
                            )
                    else:  # 选择按钮
                        widget.configure(
                            bg=t["surface"], 
                            fg=t["text"],
                            highlightbackground=t["border"]
                        )
                elif widget_class == "Scrollbar":
                    pass  # 滚动条保持默认
            except:
                pass
            
            # 递归处理子组件
            if widget.winfo_children():
                self._update_theme_recursive(widget, t)
    
    def toggle_topmost(self):
        self.root.attributes('-topmost', self.always_on_top.get())
        config = load_config()
        config["always_on_top"] = self.always_on_top.get()
        save_config(config)
        
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="选择TXT文件夹")
        if folder:
            self.folder_path = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            
            self.file_listbox.delete(0, tk.END)
            txt_files = sorted([f for f in os.listdir(folder) if f.endswith('.txt')])
            
            for f in txt_files:
                self.file_listbox.insert(tk.END, f)
            
            count = len(txt_files)
            t = THEMES[self.current_theme]
            self.status_label.config(text=f"已加载 {count} 个文件", fg=t["text"])
            self.log(f"已加载: {folder} ({count}个)")
            
            config = load_config()
            config["last_folder"] = folder
            save_config(config)
    
    def load_last_folder(self):
        config = load_config()
        
        self.always_on_top.set(config.get("always_on_top", True))
        self.root.attributes('-topmost', self.always_on_top.get())
        
        theme = config.get("theme", "pink")
        self.theme_var.set(theme)
        self.current_theme = theme
        
        # 应用主题
        self.change_theme()
        
        if config.get("last_folder") and os.path.exists(config["last_folder"]):
            self.folder_path = config["last_folder"]
            self.folder_entry.insert(0, config["last_folder"])
            
            self.file_listbox.delete(0, tk.END)
            txt_files = sorted([f for f in os.listdir(config["last_folder"]) if f.endswith('.txt')])
            
            for f in txt_files:
                self.file_listbox.insert(tk.END, f)
            
            t = THEMES[self.current_theme]
            self.status_label.config(text=f"已加载 {len(txt_files)} 个文件", fg=t["text"])
    
    def flash_window(self):
        for _ in range(3):
            self.root.attributes('-alpha', 0.6)
            self.root.update()
            time.sleep(0.15)
            self.root.attributes('-alpha', 1.0)
            self.root.update()
            time.sleep(0.15)
    
    def on_clipboard_change(self, file_path, filename, title, content, matched, matched_file=None, similarity=0):
        t = THEMES[self.current_theme]
        
        if not title:
            self.log("未提取到标题")
            self.status_label.config(text="未提取到标题", fg=t["error"])
            return
        
        if matched and file_path:
            if self.auto_save.get():
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.log(f"已保存: {filename}")
                    self.status_label.config(text=f"已保存: {filename}", fg=t["success"])
                except Exception as e:
                    self.log(f"失败: {e}")
                    self.status_label.config(text=f"保存失败", fg=t["error"])
                    self.flash_window()
            else:
                self.log(f"匹配: {filename}")
                self.status_label.config(text=f"匹配: {filename}", fg=t["warning"])
        else:
            self.log(f"未匹配 标题:{title[:15]}... 最佳:{matched_file} 相似度:{similarity}")
            self.status_label.config(text="未匹配", fg=t["error"])
    
    def start_watching(self):
        if not self.folder_path:
            messagebox.showwarning("提示", "请先选择文件夹！")
            return
        
        if not os.path.exists(self.folder_path):
            messagebox.showerror("错误", "文件夹不存在！")
            return
        
        self.watcher = ClipboardWatcher(self.folder_path, self.on_clipboard_change)
        
        self.watcher_thread = threading.Thread(target=self.watcher.run, daemon=True)
        self.watcher_thread.start()
        
        self.is_running = True
        t = THEMES[self.current_theme]
        self.start_btn.config(state=tk.DISABLED, bg=t["surface"], fg=t["text_muted"])
        self.stop_btn.config(state=tk.NORMAL, bg=t["surface"], fg=t["text"])
        self.status_label.config(text="监听中... 在剪切板中复制", fg=t["accent"])
        self.log("开始监听")
        
        config = load_config()
        config["auto_save"] = self.auto_save.get()
        config["always_on_top"] = self.always_on_top.get()
        save_config(config)
    
    def stop_watching(self):
        if self.watcher:
            self.watcher.stop()
        
        self.is_running = False
        t = THEMES[self.current_theme]
        self.start_btn.config(state=tk.NORMAL, bg=t["accent"], fg=t["surface"])
        self.stop_btn.config(state=tk.DISABLED, bg=t["surface"], fg=t["text_muted"])
        self.status_label.config(text="已停止", fg=t["text_muted"])
        self.log("已停止")
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        import pyperclip
    except ImportError:
        print("需要安装 pyperclip: pip install pyperclip")
        exit(1)
    
    app = ModernApp()
    app.run()
