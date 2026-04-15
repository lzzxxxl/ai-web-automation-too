import os
import sys
import importlib.util
import logging
from typing import Dict, Any, List, Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PluginSystem:
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.initialize()
    
    def initialize(self):
        """初始化插件系统"""
        # 创建插件目录
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir, exist_ok=True)
            logger.info(f"创建插件目录: {self.plugin_dir}")
        
        # 加载插件
        self.load_plugins()
    
    def load_plugins(self):
        """加载所有插件"""
        try:
            # 遍历插件目录
            for file in os.listdir(self.plugin_dir):
                if file.endswith(".py") and not file.startswith("_"):
                    plugin_name = file[:-3]
                    plugin_path = os.path.join(self.plugin_dir, file)
                    
                    try:
                        # 导入插件模块
                        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[plugin_name] = module
                            spec.loader.exec_module(module)
                            
                            # 检查插件是否有setup函数
                            if hasattr(module, "setup"):
                                plugin_instance = module.setup(self)
                                self.plugins[plugin_name] = plugin_instance
                                logger.info(f"加载插件成功: {plugin_name}")
                            else:
                                logger.warning(f"插件 {plugin_name} 缺少setup函数")
                    except Exception as e:
                        logger.error(f"加载插件 {plugin_name} 失败: {e}")
        except Exception as e:
            logger.error(f"加载插件失败: {e}")
    
    def register_hook(self, hook_name: str, callback: Callable):
        """注册钩子"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
        logger.info(f"注册钩子: {hook_name}")
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """触发钩子"""
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"执行钩子 {hook_name} 失败: {e}")
        return results
    
    def get_plugin(self, plugin_name: str) -> Any:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """列出所有插件"""
        return list(self.plugins.keys())
    
    def reload_plugins(self):
        """重新加载所有插件"""
        self.plugins.clear()
        self.hooks.clear()
        self.load_plugins()
        logger.info("插件已重新加载")

# 全局插件系统实例
plugin_system = PluginSystem()

# 插件示例模板
"""
# 插件示例 (plugins/example_plugin.py)
def setup(plugin_system):
    class ExamplePlugin:
        def __init__(self, plugin_system):
            self.plugin_system = plugin_system
            # 注册钩子
            self.plugin_system.register_hook("before_task", self.before_task)
            self.plugin_system.register_hook("after_task", self.after_task)
        
        def before_task(self, task):
            print(f"执行任务前: {task}")
            return task
        
        def after_task(self, task, result):
            print(f"执行任务后: {task}, 结果: {result}")
            return result
    
    return ExamplePlugin(plugin_system)
"""
