import sys
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QPushButton, QTextEdit, QComboBox, QLabel, 
                            QLineEdit, QMessageBox, QProgressBar)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import tempfile

class PoeAutomationThread(QThread):
    response_ready = pyqtSignal(str)
    status_update = pyqtSignal(str)
    
    def __init__(self, driver, message):
        super().__init__()
        self.driver = driver
        self.message = message
    
    def run(self):
        try:
            self.status_update.emit("🔄 Sending message...")
            
            # Find message input
            message_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
            )
            
            # Clear and send message
            message_input.clear()
            message_input.send_keys(self.message)
            message_input.send_keys(Keys.RETURN)
            
            self.status_update.emit("⏳ Waiting for response...")
            
            # Wait for response (adjust timing as needed)
            time.sleep(3)
            
            # Try to get response with multiple selectors
            response_selectors = [
                "[data-testid*='message']",
                "[class*='Message']", 
                "[class*='message']",
                ".prose",
                "div[dir='auto']"
            ]
            
            response_text = "Response received (check browser for details)"
            
            for selector in response_selectors:
                try:
                    messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if messages:
                        # Get the last few messages
                        recent_messages = messages[-3:]
                        combined_text = "\n".join([msg.text for msg in recent_messages if msg.text.strip()])
                        if combined_text and len(combined_text) > 10:
                            response_text = combined_text
                            break
                except:
                    continue
            
            self.response_ready.emit(response_text)
            
        except Exception as e:
            self.response_ready.emit(f"❌ Error: {str(e)}")

class PoeSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver = None
        self.init_ui()
        self.setup_browser()
    
    def init_ui(self):
        self.setWindowTitle("Poe Search Tool - Automated Browser")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Connection status
        self.status_label = QLabel("🔄 Setting up browser...")
        layout.addWidget(self.status_label)
        
        # Bot selection
        bot_layout = QHBoxLayout()
        bot_layout.addWidget(QLabel("Bot:"))
        self.bot_combo = QComboBox()
        self.bot_combo.addItems([
            "Assistant (Claude)", 
            "GPT-4o", 
            "GPT-4o-Mini",
            "GPT-3.5-Turbo",
            "Gemini-Pro",
            "Current Bot"
        ])
        bot_layout.addWidget(self.bot_combo)
        layout.addLayout(bot_layout)
        
        # Query input
        layout.addWidget(QLabel("Enter your query:"))
        self.query_input = QTextEdit()
        self.query_input.setMaximumHeight(100)
        self.query_input.setPlaceholderText("Type your message here...")
        layout.addWidget(self.query_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.send_button = QPushButton("🚀 Send Message")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setEnabled(False)
        button_layout.addWidget(self.send_button)
        
        self.reconnect_button = QPushButton("🔄 Reconnect")
        self.reconnect_button.clicked.connect(self.setup_browser)
        button_layout.addWidget(self.reconnect_button)
        
        self.open_browser_button = QPushButton("🌐 Show Browser")
        self.open_browser_button.clicked.connect(self.show_browser)
        button_layout.addWidget(self.open_browser_button)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results
        layout.addWidget(QLabel("Response:"))
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        layout.addWidget(self.results_output)
        
        central_widget.setLayout(layout)
    
    def setup_browser(self):
        try:
            self.status_label.setText("🔄 Starting browser...")
            
            if self.driver:
                self.driver.quit()
            
            # Set up Chrome options
            chrome_options = Options()
            temp_dir = tempfile.mkdtemp()
            chrome_options.add_argument(f"--user-data-dir={temp_dir}")
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
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.status_label.setText("🌐 Opening Poe.com...")
            self.driver.get("https://poe.com")
            
            # Show login message
            QMessageBox.information(
                self, 
                "Login Required", 
                "Please log in to your Poe account in the browser window.\n\n"
                "After logging in and navigating to any chat, click 'Test Connection' below."
            )
            
            self.status_label.setText("⏳ Please log in to Poe in the browser window")
            self.send_button.setText("🧪 Test Connection")
            self.send_button.setEnabled(True)
            
        except Exception as e:
            self.status_label.setText(f"❌ Browser setup failed: {str(e)}")
            self.results_output.setText(f"❌ Failed to start browser: {str(e)}")
    
    def send_message(self):
        if not self.driver:
            self.results_output.setText("❌ Browser not connected")
            return
        
        # Check if this is a test connection
        if self.send_button.text() == "🧪 Test Connection":
            self.test_connection()
            return
        
        query = self.query_input.toPlainText().strip()
        if not query:
            self.results_output.setText("❌ Please enter a message")
            return
        
        self.send_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start automation thread
        self.automation_thread = PoeAutomationThread(self.driver, query)
        self.automation_thread.response_ready.connect(self.on_response_ready)
        self.automation_thread.status_update.connect(self.on_status_update)
        self.automation_thread.start()
    
    def test_connection(self):
        try:
            # Check if we can find chat interface
            message_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
            )
            
            self.status_label.setText("✅ Connected to Poe! Ready to send messages.")
            self.send_button.setText("🚀 Send Message")
            self.results_output.setText("✅ Successfully connected to your Poe account!\n\nYou can now send messages.")
            
        except:
            self.status_label.setText("❌ Not connected - please navigate to a chat")
            self.results_output.setText("❌ Could not find chat interface.\n\nPlease:\n1. Make sure you're logged in\n2. Navigate to any chat conversation\n3. Click 'Test Connection' again")
    
    def on_response_ready(self, response):
        self.results_output.setText(response)
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("✅ Message sent successfully!")
    
    def on_status_update(self, status):
        self.status_label.setText(status)
    
    def show_browser(self):
        if self.driver:
            self.driver.switch_to.window(self.driver.window_handles[0])
        else:
            QMessageBox.warning(self, "Warning", "Browser not connected")
    
    def closeEvent(self, event):
        if self.driver:
            self.driver.quit()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PoeSearchApp()
    window.show()
    sys.exit(app.exec())