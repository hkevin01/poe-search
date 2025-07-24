from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class BrowserPoeClient:
    def __init__(self):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--user-data-dir=/home/kevin/.config/google-chrome")  # Use your existing profile
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize driver
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def connect_to_poe(self):
        try:
            self.driver.get("https://poe.com")
            time.sleep(3)
            
            # Check if we're logged in
            try:
                # Look for chat interface elements
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='chatMessageInputContainer']"))
                )
                print("✅ Successfully connected to Poe!")
                return True
            except:
                print("❌ Not logged in to Poe. Please log in manually.")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting: {e}")
            return False
    
    def send_message(self, bot_name, message):
        try:
            # Click on bot selector or find the right bot
            # This is a simplified version - you might need to adjust selectors
            
            # Find message input
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
            )
            
            # Clear and type message
            message_input.clear()
            message_input.send_keys(message)
            
            # Find and click send button
            send_button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='sendButton']")
            send_button.click()
            
            # Wait for response
            time.sleep(5)
            
            # Get the latest response (this selector might need adjustment)
            responses = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='botMessage']")
            if responses:
                return responses[-1].text
            else:
                return "No response received"
                
        except Exception as e:
            return f"Error sending message: {e}"
    
    def close(self):
        self.driver.quit()

# Test
if __name__ == "__main__":
    client = BrowserPoeClient()
    
    if client.connect_to_poe():
        # Keep browser open for manual testing
        input("Press Enter after you've navigated to a chat in your browser...")
        
        response = client.send_message("Assistant", "Hello! Testing automated browser.")
        print(f"Response: {response}")
    
    input("Press Enter to close browser...")
    client.close()