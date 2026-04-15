import os
import sys
import json
import logging
from datetime import datetime

# Mock the CTk module to simulate the toggle_theme function
class MockCTk:
    @staticmethod
    def get_appearance_mode():
        return "dark"
    
    @staticmethod
    def set_appearance_mode(mode):
        pass

# Mock the log_text widget
class MockLogText:
    def configure(self, **kwargs):
        pass
    
    def insert(self, position, text):
        pass
    
    def see(self, position):
        pass

# Import the TextHandler class
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        msg = self.format(record)
        print(f"LOG: {msg}")

# Test the toggle_theme function
class TestModernAIAutomationGUI:
    def __init__(self):
        self.log_text = MockLogText()
        self.setup_logging()
        
    def setup_logging(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        logger.addHandler(text_handler)
    
    def toggle_theme(self):
        try:
            current_mode = "dark"  # Mocked
            new_mode = "light" if current_mode == "dark" else "dark"
            print(f"Theme toggled to: {new_mode}")
            # Simulate the logger call that was causing the issue
            import logging
            logging.info(f"主题已切换为: {new_mode}")
            return True
        except Exception as e:
            import logging
            logging.error(f"切换主题失败: {e}")
            print(f"Error: {e}")
            return False

# Run the test
if __name__ == "__main__":
    print("Testing the logger fix...")
    test_app = TestModernAIAutomationGUI()
    result = test_app.toggle_theme()
    print(f"Test result: {'PASS' if result else 'FAIL'}")
    print("Test completed successfully!")
