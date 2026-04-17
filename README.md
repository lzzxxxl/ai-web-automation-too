# AI网页全自动批量处理工具

一个整合网页自动化操作与剪贴板保存功能的一体化工具，用于批量向网页版AI（如ChatGPT、DeepSeek、Grok等）提交问题并自动保存回复结果。

## 功能特性

- **浏览器控制**：支持连接已打开的Chrome、Edge和Firefox浏览器，保留登录状态，支持同时连接多个浏览器实例，自动检测浏览器路径
- **现代化GUI界面**：使用CustomTkinter构建美观的图形界面，支持深色/浅色主题切换、托盘图标和快捷键
- **任务管理系统**：完整的任务队列管理，支持批量操作、任务模板、导入导出和优先级设置
- **标题管理**：支持从TXT文件读取或手动粘贴批量标题，自动去重，生成有序任务队列
- **AI交互**：自动定位输入框、发送按钮，监控AI输出状态，处理生成中断，完成后自动复制内容，支持AI平台自动检测（ChatGPT、Claude、Gemini等）
- **智能重试策略**：网络异常和操作失败自动重试，提高成功率
- **剪贴板整合**：内嵌用户现有剪贴板保存程序，自动读取剪贴板内容，匹配标题并保存到对应文件
- **自动保存与崩溃恢复**：运行过程中自动保存状态，崩溃后可从断点继续执行
- **插件系统**：支持动态加载插件，提供钩子机制扩展功能
- **API接口**：提供RESTful API服务，方便与其他系统集成
- **无人值守**：全程自动执行任务，支持异常重试，记录错误日志，支持手动终止
- **多平台支持**：兼容Windows和macOS系统

## 系统要求

- Python 3.8及以上
- Chrome、Edge或Firefox浏览器
- 操作系统：Windows 10+ 或 macOS

## 安装步骤

### 1. 克隆或下载项目

### 2. 安装依赖

```bash
pip install -r requirements.txt
playwright install
```

### 3. 配置浏览器

方式一：使用提供的脚本启动浏览器并开启远程调试模式：

- **Windows**：双击 `start_chrome_debug.bat`、`start_edge_debug.bat` 或 `start_firefox_debug.bat`
- **macOS/Linux**：运行 `./start_chrome_debug.sh`、`./start_edge_debug.sh` 或 `./start_firefox_debug.sh`

方式二：程序会自动检测浏览器路径并启动，无需手动启动

### 4. 准备标题文件

在项目目录创建 `questions.txt` 文件，每行一个标题/问题：

```
什么是Python?
如何学习Python编程?
Python有哪些常用库?
```

### 5. 配置参数

编辑 `config.json` 文件，根据需要修改配置：

```json
{
  "BROWSER_TYPE": "chrome",  // 可选: chrome, edge, firefox
  "INSTANCE_ID": "default",   // 浏览器实例ID
  "QUESTION_FILE": "questions.txt",
  "CONTINUE_MAX_CLICK": 10,  // 最大点击继续生成次数
  "WAIT_STABLE_TIME": 5,  // 内容稳定判定时间（秒）
  "RETRY_COUNT": 3,  // 异常重试次数
  "SAVE_PATH": "./output",  // 保存路径
  "DEBUG_PORT": 9222  // 调试端口
}
```

## 使用方法

### 方法一：使用图形界面（推荐）

1. 运行GUI程序：

```bash
python modern_gui.py
```

2. 在界面中配置参数、粘贴标题或选择标题文件
3. 点击"开始运行"按钮开始执行任务

### 方法二：使用命令行（默认标题文件）

1. 启动浏览器（使用提供的脚本开启远程调试模式）或让程序自动启动
2. 在浏览器中登录所需的网页AI平台（如ChatGPT、DeepSeek等）
3. 运行主程序：

```bash
python main.py
```

### 方法三：指定标题文件（支持拖拽）

1. 启动浏览器
2. 在浏览器中登录所需的网页AI平台
3. 运行主程序并指定标题文件路径：

```bash
python main.py path/to/questions.txt
```

或者直接拖拽txt文件到命令行：

```bash
python main.py [拖拽txt文件到这里]
```

### 方法四：从剪贴板粘贴标题

1. 启动浏览器
2. 在浏览器中登录所需的网页AI平台
3. 复制要处理的标题（每行一个）
4. 运行主程序：

```bash
python main.py --paste
```

### 方法五：使用API接口

1. 启动API服务器：

```bash
python api_server.py
```

2. 使用curl或其他工具调用API：

```bash
# 健康检查
curl http://localhost:5000/api/v1/health

# 创建任务
curl -X POST http://localhost:5000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"file_path": "questions.txt"}'

# 查看任务状态
curl http://localhost:5000/api/v1/tasks/status

# 停止任务
curl -X POST http://localhost:5000/api/v1/tasks/stop
```

### 执行流程

程序会自动执行以下操作：
   - 读取标题（从文件、剪贴板、GUI或交互式输入）
   - 连接浏览器（自动启动或连接已启动的浏览器）
   - 按顺序处理每个标题
   - 自动发送问题
   - 监控AI输出
   - 复制回复内容
   - 保存到对应文件

## 项目结构

```
├── browser_manager.py       # 浏览器管理模块
├── title_manager.py         # 标题管理模块
├── ai_automation.py         # AI自动化交互模块
├── clipboard_integration.py  # 剪贴板集成模块
├── clipboard_watcher.py      # 剪贴板监听程序
├── main.py                   # 主程序
├── modern_gui.py            # 现代化GUI界面
├── task_manager.py          # 任务管理系统
├── plugin_system.py         # 插件系统
├── api_server.py            # API服务器
├── test_system.py           # 测试脚本
├── requirements.txt          # 依赖文件
├── build.spec               # PyInstaller打包配置
├── questions.txt            # 标题文件
├── start_chrome_debug.bat    # Windows启动Chrome调试模式
├── start_edge_debug.bat     # Windows启动Edge调试模式
├── start_firefox_debug.bat   # Windows启动Firefox调试模式
├── start_chrome_debug.sh    # macOS/Linux启动Chrome调试模式
├── start_edge_debug.sh      # macOS/Linux启动Edge调试模式
├── start_firefox_debug.sh    # macOS/Linux启动Firefox调试模式
├── plugins/                 # 插件目录
└── templates/               # 任务模板目录
```

## 插件开发

1. 在 `plugins/` 目录下创建新的Python文件
2. 实现 `setup(plugin_system)` 函数
3. 注册需要的钩子函数

示例插件：

```python
def setup(plugin_system):
    class ExamplePlugin:
        def __init__(self, plugin_system):
            self.plugin_system = plugin_system
            self.plugin_system.register_hook("before_task", self.before_task)
            self.plugin_system.register_hook("after_task", self.after_task)
        
        def before_task(self, task):
            print(f"执行任务前: {task}")
            return task
        
        def after_task(self, task, result):
            print(f"执行任务后: {task}, 结果: {result}")
            return result
    
    return ExamplePlugin(plugin_system)
```

## 快捷键

- `Ctrl+S`：保存配置
- `Ctrl+Q`：退出程序
- `F5`：开始运行
- `F6`：停止运行

## 注意事项

1. 浏览器路径自动检测支持Windows注册表和环境变量
2. 确保在浏览器中已登录所需的网页AI平台
3. 标题文件编码支持UTF-8和ANSI
4. 程序会自动去重标题，确保每个标题只处理一次
5. 遇到异常时会自动重试，重试失败后会跳过当前任务继续执行
6. 运行过程中会自动保存状态，崩溃后可继续执行
7. 可以通过托盘图标最小化和恢复窗口

## 常见问题

### Q: 浏览器连接失败怎么办？
A: 请确保：
- 浏览器已启动或程序可以自动启动
- 配置文件中的浏览器类型和端口正确
- 浏览器路径正确（程序会自动检测）

### Q: 标题读取失败怎么办？
A: 请确保：
- `questions.txt` 文件存在
- 文件编码正确（UTF-8或ANSI）
- 文件格式正确（每行一个标题）

### Q: 保存文件失败怎么办？
A: 请确保：
- 保存路径存在且有写入权限
- 标题不包含无效的文件名字符

### Q: 程序运行过程中卡住怎么办？
A: 可以按 Ctrl+C 终止程序，然后检查日志文件分析问题。程序会保存当前状态，下次运行时可以继续执行。

### Q: 如何打包成可执行文件？
A: 可以使用PyInstaller打包：

```bash
pyinstaller build.spec
```

打包后的文件在 `dist/` 目录下。

## 扩展功能

- 支持多账号并行操作（同时连接多个浏览器实例）
- 支持自定义保存格式
- 支持任务进度保存与恢复
- 支持批量导出日志
- 支持插件系统扩展功能
- 支持RESTful API接口

## 许可证

MIT License
