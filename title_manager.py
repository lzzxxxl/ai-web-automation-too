import os
import chardet
import logging
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TitleManager:
    def __init__(self):
        self.titles: List[str] = []
        self.deduplicated_titles: List[str] = []
    
    def read_titles_from_file(self, file_path: str) -> List[str]:
        """
        从TXT文件中读取标题
        
        Args:
            file_path: TXT文件路径
            
        Returns:
            标题列表
        """
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            # 处理每一行，去除空白字符
            self.titles = [line.strip() for line in lines if line.strip()]
            logger.info(f"从文件 {file_path} 读取到 {len(self.titles)} 个标题")
            return self.titles
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return []
    
    def read_titles_from_paste(self, text: str) -> List[str]:
        """
        从粘贴的文本中读取标题
        
        Args:
            text: 粘贴的文本
            
        Returns:
            标题列表
        """
        try:
            # 按换行符分割
            lines = text.split('\n')
            # 处理每一行，去除空白字符
            self.titles = [line.strip() for line in lines if line.strip()]
            logger.info(f"从粘贴文本中读取到 {len(self.titles)} 个标题")
            return self.titles
        except Exception as e:
            logger.error(f"处理粘贴文本失败: {e}")
            return []
    
    def deduplicate_titles(self) -> List[str]:
        """
        去重标题，保留原始顺序
        
        Returns:
            去重后的标题列表
        """
        seen = set()
        self.deduplicated_titles = []
        
        for title in self.titles:
            if title not in seen:
                seen.add(title)
                self.deduplicated_titles.append(title)
        
        logger.info(f"去重前: {len(self.titles)} 个标题, 去重后: {len(self.deduplicated_titles)} 个标题")
        return self.deduplicated_titles
    
    def get_task_queue(self) -> List[str]:
        """
        获取任务队列
        
        Returns:
            任务队列（去重后的标题列表）
        """
        if not self.deduplicated_titles:
            self.deduplicate_titles()
        return self.deduplicated_titles
    
    def clear(self):
        """
        清空标题列表
        """
        self.titles = []
        self.deduplicated_titles = []

# 全局标题管理器实例
title_manager = TitleManager()

if __name__ == "__main__":
    # 示例用法
    manager = TitleManager()
    
    # 从文件读取标题
    # manager.read_titles_from_file("questions.txt")
    
    # 从粘贴文本读取标题
    test_text = "标题1\n标题2\n标题1\n标题3"
    manager.read_titles_from_paste(test_text)
    
    # 去重
    deduplicated = manager.deduplicate_titles()
    print("去重后的标题:", deduplicated)
    
    # 获取任务队列
    queue = manager.get_task_queue()
    print("任务队列:", queue)