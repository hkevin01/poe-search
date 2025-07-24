"""Background worker for syncing Poe conversations."""

import logging
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)

class SyncWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    def run(self):
        try:
            self.progress.emit("Starting conversation sync...")
            conversations = self.client.get_conversation_history(days=3650, limit=10000)
            self.progress.emit(f"Synced {len(conversations)} conversations")
            self.finished.emit(True, "Sync completed successfully")
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.finished.emit(False, str(e))