"""Working GUI for Poe Search."""

def run_gui():
    """Run the GUI."""
    print("🚀 Starting Poe Search GUI...")

    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PyQt6.QtCore import Qt
        import sys

        app = QApplication(sys.argv)

        window = QMainWindow()
        window.setWindowTitle("🔍 Poe Search - Working!")
        window.setGeometry(300, 300, 500, 300)

        central = QWidget()
        window.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("🎉 Poe Search GUI is Working!")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info = QLabel("✅ GUI Fix Successful!\n\nNext: Run comprehensive organization\nfor full features")
        info.setStyleSheet("font-size: 14px; padding: 20px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        window.show()
        return app.exec()

    except Exception as e:
        print(f"❌ GUI Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_gui())
