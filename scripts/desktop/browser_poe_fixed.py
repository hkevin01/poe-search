from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import tempfile
import os

class BrowserPoeClient:
    def __init__(self):
        # Set up Chrome options with unique user data directory
        chrome_options = Options()
        
        # Create a temporary directory for this session
        temp_dir = tempfile.mkdtemp()
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        # Alternative: Don't use user data directory at all
        # chrome_options.add_argument("--no-first-run")
        # chrome_options.add_argument("--disable-default-apps")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize driver
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def connect_to_poe(self):
        try:
            print("🌐 Opening Poe.com...")
            self.driver.get("https://poe.com")
            time.sleep(5)
            
            print("Please log in to your Poe account manually in the browser window...")
            print("After logging in, navigate to any chat and press Enter here...")
            input("Press Enter when you're ready to continue...")
            
            # Check if we can find chat interface
            try:
                # Look for message input area
                message_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea, [contenteditable='true']"))
                )
                print("✅ Found chat interface!")
                return True
            except:
                print("❌ Could not find chat interface. Make sure you're in a chat.")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting: {e}")
            return False
    
    def send_message_manual(self, message):
        """Manual approach - you type the message"""
        try:
            print(f"\n📝 Please manually type this message in the browser: '{message}'")
            print("Then press Enter here after you see the response...")
            input("Press Enter when response is complete...")
            
            # Try to get the latest response
            try:
                # Look for recent messages (adjust selector as needed)
                messages = self.driver.find_elements(By.CSS_SELECTOR, "[class*='Message'], [class*='message'], [data-testid*='message']")
                if messages:
                    latest = messages[-1].text
                    return latest
                else:
                    return "Could not extract response automatically"
            except:
                return "Response received (could not extract automatically)"
                
        except Exception as e:
            return f"Error: {e}"
    
    def close(self):
        self.driver.quit()

# Test the fixed version
if __name__ == "__main__":
    print("🚀 Starting Poe Browser Client...")
    client = BrowserPoeClient()
    
    try:
        if client.connect_to_poe():
            # Test message
            response = client.send_message_manual("Hello! Testing my paid Poe account.")
            print(f"\n📋 Response: {response}")
            
            # Keep testing
            while True:
                user_message = input("\nEnter message (or 'quit' to exit): ")
                if user_message.lower() == 'quit':
                    break
                    
                response = client.send_message_manual(user_message)
                print(f"📋 Response: {response}")
        
    finally:
        print("🔚 Closing browser...")
        client.close()