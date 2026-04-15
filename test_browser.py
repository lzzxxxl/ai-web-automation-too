import time
from browser_manager import browser_manager

print("Testing browser manager...")

# Test 1: Open browser with debug
print("\n1. Opening browser with debug...")
success = browser_manager.open_browser_with_debug("chrome", 9222)
print(f"Browser opened: {success}")

# Test 2: Connect to browser
print("\n2. Connecting to browser...")
browser = browser_manager.connect_to_browser("chrome", 9222, "test")
print(f"Browser connected: {browser is not None}")

if browser:
    print("\n3. Getting page...")
    page = browser_manager.get_or_create_page("test")
    print(f"Page obtained: {page is not None}")
    
    if page:
        print("\n4. Navigating to Google...")
        try:
            page.goto("https://www.google.com")
            print("Navigation successful")
            print(f"Page title: {page.title()}")
        except Exception as e:
            print(f"Navigation failed: {e}")
    
    # Close browser
    print("\n5. Closing browser...")
    browser_manager.close_browser("test")

# Close all
browser_manager.close_all()
print("\nTest completed")
