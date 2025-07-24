from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class ChatViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        self.setLayout(layout)

    def display_conversation(self, conversation):
        html = self._format_conversation_html(conversation)
        self.chat_display.setHtml(html)

    def _format_conversation_html(self, conversation):
        html = f"<h2>{conversation.title} <span style='font-size:12pt;color:#888;'>({conversation.bot})</span></h2>"
        for msg in conversation.messages:
            role = msg.role.capitalize()
            html += f"<b>{role}:</b> {msg.content}<br><br>"
        return html
