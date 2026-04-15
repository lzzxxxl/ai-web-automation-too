# 剪贴板自动保存

一个简洁高效的 Windows 剪贴板监听工具，自动将剪贴板内容保存到匹配的本地文件中。

## 功能特性

- **智能标题提取**：自动从剪贴板内容中识别文章/文件标题
- **自动匹配保存**：根据标题匹配本地 TXT 文件，自动保存内容
- **多主题支持**：支持黑色极简、白色极简、粉色三种主题
- **窗口置顶**：可选择将窗口始终保持在最前面
- **轻量高效**：占用资源少，后台静默运行

## 界面预览

[待添加截图]

## 使用方法

### 方式一：直接运行

1. 双击 `剪贴板自动保存.exe` 运行程序
2. 点击"选择"按钮，选择包含 TXT 文件的文件夹
3. 点击"开始监听"启动剪贴板监控
4. 在任意应用中复制内容，程序自动匹配并保存

### 方式二：从源码运行

```bash
# 安装依赖
pip install pyperclip

# 运行程序
python clipboard_watcher.py
```

### 方式三：打包为 exe

```bash
pip install pyinstaller
pyinstaller 剪贴板自动保存.spec
```

## 工作原理

1. 监听剪贴板变化，检测复制的内容
2. 从内容中提取标题（支持多种格式）
3. 清洗标题（只保留中文、英文、数字）
4. 在指定文件夹中匹配同名的 TXT 文件
5. 如果开启自动保存，内容直接写入匹配的文件

## 标题识别格式

程序支持识别以下格式的标题：

| 格式 | 示例 |
|------|------|
| 原文章标题 | `原文章标题：如何学习Python -->`

| 原文件标题 | `原文件标题：技术文档.txt -->`
| HTML title | `<title>页面标题</title>` |
| Markdown title | `title: 文章标题` |

## 配置文件

程序配置存储在 `watcher_config.json` 中：

```json
{
  "last_folder": "上次使用的文件夹路径",
  "auto_save": true,
  "always_on_top": true,
  "theme": "pink"
}
```

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `last_folder` | string | 上次使用的文件夹路径 |
| `auto_save` | boolean | 是否自动保存到匹配文件 |
| `always_on_top` | boolean | 窗口是否置顶 |
| `theme` | string | 主题：`black`、`white` 或 `pink` |

## 项目结构

```
├── clipboard_watcher.py    # 主程序源代码
├── watcher_config.json     # 配置文件
├── zi.ico                  # 程序图标
├── zi.jpg                  # 图片素材
└── 剪贴板自动保存.spec      # PyInstaller 打包配置
```

## 系统要求

- Windows 操作系统
- 无需 Python 环境（使用打包后的 exe）

## 技术栈

- **GUI**：tkinter（Python 内置）
- **剪贴板**：pyperclip
- **打包**：PyInstaller

## License

MIT License
