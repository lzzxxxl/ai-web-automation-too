# AI网页全自动批量处理工具

一个整合网页自动化操作与剪贴板保存功能的一体化工具，用于批量向网页版AI（如ChatGPT、DeepSeek、Grok等）提交问题并自动保存回复结果。

## 功能特性

- **浏览器控制**：支持连接已打开的Chrome和Edge浏览器，保留登录状态，支持同时连接多个浏览器实例
- **标题管理**：支持从TXT文件读取或手动粘贴批量标题，自动去重，生成有序任务队列
- **AI交互**：自动定位输入框、发送按钮，监控AI输出状态，处理生成中断，完成后自动复制内容
- **剪贴板整合**：内嵌用户现有剪贴板保存程序，自动读取剪贴板内容，匹配标题并保存到对应文件
- **无人值守**：全程自动执行任务，支持异常重试，记录错误日志，支持手动终止
- **多平台支持**：兼容Windows和macOS系统

## 系统要求

- Python 3.8及以上
- Chrome或Edge浏览器
- 操作系统：Windows 10+ 或 macOS

## 安装步骤

### 1. 克隆或下载项目

### 2. 安装依赖

```bash
cd ai-web-automation
pip install -r requirements.txt
playwright install
```

### 3. 配置浏览器

使用提供的脚本启动浏览器并开启远程调试模式：

- **Windows**：双击 `start_chrome_debug.bat` 或 `start_edge_debug.bat`
- **macOS/Linux**：运行 `./start_chrome_debug.sh` 或 `./start_edge_debug.sh`

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
  "BROWSER_TYPE": "chrome",  // 可选: chrome, edge
  "QUESTION_FILE": "questions.txt",
  "CONTINUE_MAX_CLICK": 10,  // 最大点击继续生成次数
  "WAIT_STABLE_TIME": 5,  // 内容稳定判定时间（秒）
  "RETRY_COUNT": 3,  // 异常重试次数
  "SAVE_PATH": "./output",  // 保存路径
  "DEBUG_PORT": 9222  // 调试端口
}
```

## 使用方法

1. 启动浏览器（使用提供的脚本开启远程调试模式）
2. 在浏览器中登录所需的网页AI平台（如ChatGPT、DeepSeek等）
3. 运行主程序：

```bash
python main.py
```

4. 程序会自动执行以下操作：
   - 读取标题文件
   - 连接浏览器
   - 按顺序处理每个标题
   - 自动发送问题
   - 监控AI输出
   - 复制回复内容
   - 保存到对应文件

## 项目结构

```
ai-web-automation/
├── browser_manager.py    # 浏览器管理模块
├── title_manager.py      # 标题管理模块
├── ai_automation.py      # AI自动化交互模块
├── clipboard_integration.py  # 剪贴板集成模块
├── clipboard_watcher.py  # 剪贴板监听程序（用户现有程序）
├── main.py              # 主程序
├── test_system.py       # 测试脚本
├── requirements.txt     # 依赖文件
├── config.json          # 配置文件
├── questions.txt        # 标题文件
├── start_chrome_debug.bat  # Windows启动Chrome调试模式
├── start_edge_debug.bat    # Windows启动Edge调试模式
├── start_chrome_debug.sh   # macOS/Linux启动Chrome调试模式
└── start_edge_debug.sh     # macOS/Linux启动Edge调试模式
```

## 注意事项

1. 确保浏览器已开启远程调试模式
2. 确保在浏览器中已登录所需的网页AI平台
3. 标题文件编码支持UTF-8和ANSI
4. 程序会自动去重标题，确保每个标题只处理一次
5. 遇到异常时会自动重试，重试失败后会跳过当前任务继续执行
6. 运行过程中请保持浏览器后台运行，不要关闭浏览器窗口

## 常见问题

### Q: 浏览器连接失败怎么办？
A: 请确保：
- 浏览器已启动
- 已使用提供的脚本开启远程调试模式
- 配置文件中的浏览器类型和端口正确

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
A: 可以按 Ctrl+C 终止程序，然后检查日志文件分析问题

## 扩展功能

- 支持多账号并行操作（同时连接多个浏览器实例）
- 支持自定义保存格式
- 支持任务进度保存与恢复
- 支持批量导出日志

## 许可证

MIT License