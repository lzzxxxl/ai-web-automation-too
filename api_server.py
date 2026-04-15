import os
import sys
import logging
from flask import Flask, request, jsonify
from threading import Thread

from main import AIAutomationTool
from plugin_system import plugin_system

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 全局工具实例
tool = None

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "plugins": plugin_system.list_plugins()
    })

@app.route('/api/v1/tasks', methods=['POST'])
def create_task():
    """创建任务"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        file_path = data.get('file_path')
        paste_text = data.get('paste_text')
        
        global tool
        tool = AIAutomationTool()
        
        # 触发插件钩子
        plugin_system.trigger_hook("before_create_task", data)
        
        # 启动任务处理
        def run_task():
            try:
                tool.run(file_path, paste_text)
                # 触发任务完成钩子
                plugin_system.trigger_hook("after_task_completed", tool.results)
            except Exception as e:
                logger.error(f"任务执行失败: {e}")
        
        thread = Thread(target=run_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "任务已启动"
        })
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/tasks/status', methods=['GET'])
def get_task_status():
    """获取任务状态"""
    try:
        global tool
        if not tool:
            return jsonify({"status": "idle", "message": "无任务运行"})
        
        status = "running" if tool.is_running else "completed"
        progress = 0
        if tool.tasks:
            progress = (tool.current_task_index / len(tool.tasks)) * 100
        
        return jsonify({
            "status": status,
            "progress": progress,
            "current_task": tool.current_task_index,
            "total_tasks": len(tool.tasks),
            "results": tool.results
        })
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/tasks/stop', methods=['POST'])
def stop_task():
    """停止任务"""
    try:
        global tool
        if tool and tool.is_running:
            tool.stop()
            return jsonify({"status": "success", "message": "任务已停止"})
        else:
            return jsonify({"status": "error", "message": "无任务运行"})
    except Exception as e:
        logger.error(f"停止任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/plugins', methods=['GET'])
def list_plugins():
    """列出所有插件"""
    try:
        plugins = plugin_system.list_plugins()
        return jsonify({"plugins": plugins})
    except Exception as e:
        logger.error(f"列出插件失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/plugins/reload', methods=['POST'])
def reload_plugins():
    """重新加载插件"""
    try:
        plugin_system.reload_plugins()
        return jsonify({"status": "success", "plugins": plugin_system.list_plugins()})
    except Exception as e:
        logger.error(f"重新加载插件失败: {e}")
        return jsonify({"error": str(e)}), 500

def start_api_server(host='0.0.0.0', port=5000):
    """启动API服务器"""
    logger.info(f"启动API服务器: http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    start_api_server()
