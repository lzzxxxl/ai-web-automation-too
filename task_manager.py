import os
import json
import time
import logging
from typing import List, Dict, Optional, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Task:
    def __init__(self, title: str, status: str = "pending", priority: int = 1, created_at: float = None):
        self.title = title
        self.status = status  # pending, running, completed, failed
        self.priority = priority
        self.created_at = created_at or time.time()
        self.started_at = None
        self.completed_at = None
        self.error_message = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        task = cls(
            title=data["title"],
            status=data.get("status", "pending"),
            priority=data.get("priority", 1),
            created_at=data.get("created_at")
        )
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.error_message = data.get("error_message")
        return task

class TaskManager:
    def __init__(self, save_file: str = "tasks.json"):
        self.save_file = save_file
        self.tasks: List[Task] = []
        self.load_tasks()
    
    def load_tasks(self):
        """加载任务列表"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.tasks = [Task.from_dict(task_data) for task_data in data]
                logger.info(f"已加载 {len(self.tasks)} 个任务")
            except Exception as e:
                logger.error(f"加载任务失败: {e}")
                self.tasks = []
    
    def save_tasks(self):
        """保存任务列表"""
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存 {len(self.tasks)} 个任务")
        except Exception as e:
            logger.error(f"保存任务失败: {e}")
    
    def add_task(self, title: str, priority: int = 1) -> Task:
        """添加任务"""
        task = Task(title, priority=priority)
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def add_tasks(self, titles: List[str], priority: int = 1):
        """批量添加任务"""
        for title in titles:
            self.add_task(title, priority)
    
    def get_task(self, index: int) -> Optional[Task]:
        """获取任务"""
        if 0 <= index < len(self.tasks):
            return self.tasks[index]
        return None
    
    def get_tasks(self) -> List[Task]:
        """获取所有任务"""
        return self.tasks
    
    def remove_task(self, index: int):
        """删除任务"""
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save_tasks()
    
    def remove_tasks(self, indices: List[int]):
        """批量删除任务"""
        # 按降序删除，避免索引变化
        for index in sorted(indices, reverse=True):
            self.remove_task(index)
    
    def update_task(self, index: int, **kwargs):
        """更新任务"""
        task = self.get_task(index)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.save_tasks()
    
    def reorder_tasks(self, old_index: int, new_index: int):
        """重新排序任务"""
        if 0 <= old_index < len(self.tasks) and 0 <= new_index < len(self.tasks):
            task = self.tasks.pop(old_index)
            self.tasks.insert(new_index, task)
            self.save_tasks()
    
    def get_pending_tasks(self) -> List[Task]:
        """获取待处理任务"""
        return [task for task in self.tasks if task.status == "pending"]
    
    def get_running_tasks(self) -> List[Task]:
        """获取正在运行的任务"""
        return [task for task in self.tasks if task.status == "running"]
    
    def get_completed_tasks(self) -> List[Task]:
        """获取已完成任务"""
        return [task for task in self.tasks if task.status == "completed"]
    
    def get_failed_tasks(self) -> List[Task]:
        """获取失败任务"""
        return [task for task in self.tasks if task.status == "failed"]
    
    def get_task_queue(self) -> List[str]:
        """获取任务队列（按优先级和创建时间排序）"""
        # 按优先级降序，创建时间升序排序
        sorted_tasks = sorted(
            self.get_pending_tasks(),
            key=lambda t: (-t.priority, t.created_at)
        )
        return [task.title for task in sorted_tasks]
    
    def import_tasks(self, file_path: str):
        """从文件导入任务"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and "title" in item:
                                self.add_task(item["title"], item.get("priority", 1))
                            elif isinstance(item, str):
                                self.add_task(item)
                else:
                    # 文本文件，每行一个任务
                    lines = f.readlines()
                    for line in lines:
                        title = line.strip()
                        if title:
                            self.add_task(title)
            logger.info(f"从 {file_path} 导入任务成功")
        except Exception as e:
            logger.error(f"导入任务失败: {e}")
    
    def export_tasks(self, file_path: str):
        """导出任务到文件"""
        try:
            if file_path.endswith('.json'):
                data = [task.to_dict() for task in self.tasks]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                # 导出为文本文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    for task in self.tasks:
                        f.write(f"{task.title}\n")
            logger.info(f"导出任务到 {file_path} 成功")
        except Exception as e:
            logger.error(f"导出任务失败: {e}")
    
    def load_template(self, template_name: str):
        """加载任务模板"""
        template_path = f"templates/{template_name}.json"
        if os.path.exists(template_path):
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for item in data:
                    if isinstance(item, dict) and "title" in item:
                        self.add_task(item["title"], item.get("priority", 1))
                    elif isinstance(item, str):
                        self.add_task(item)
                logger.info(f"加载模板 {template_name} 成功")
            except Exception as e:
                logger.error(f"加载模板失败: {e}")
        else:
            logger.error(f"模板文件不存在: {template_path}")
    
    def save_template(self, template_name: str):
        """保存任务模板"""
        template_dir = "templates"
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        
        template_path = f"{template_dir}/{template_name}.json"
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存模板 {template_name} 成功")
        except Exception as e:
            logger.error(f"保存模板失败: {e}")
    
    def clear_tasks(self):
        """清空所有任务"""
        self.tasks = []
        self.save_tasks()
    
    def get_task_count(self) -> Dict[str, int]:
        """获取任务统计"""
        return {
            "total": len(self.tasks),
            "pending": len(self.get_pending_tasks()),
            "running": len(self.get_running_tasks()),
            "completed": len(self.get_completed_tasks()),
            "failed": len(self.get_failed_tasks())
        }

# 全局任务管理器实例
task_manager = TaskManager()

if __name__ == "__main__":
    # 示例用法
    manager = TaskManager()
    
    # 添加任务
    manager.add_task("测试任务1", priority=2)
    manager.add_task("测试任务2", priority=1)
    manager.add_task("测试任务3", priority=3)
    
    # 获取任务队列
    queue = manager.get_task_queue()
    print("任务队列:", queue)
    
    # 导出任务
    manager.export_tasks("tasks_export.txt")
    
    # 导入任务
    manager.import_tasks("tasks_export.txt")
    
    # 保存模板
    manager.save_template("test_template")
    
    # 加载模板
    manager.load_template("test_template")
    
    print("任务统计:", manager.get_task_count())
