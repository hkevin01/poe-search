#!/usr/bin/env python3
"""
Test script for Poe conversation sync functionality.

This script tests the complete sync pipeline:
1. Configuration loading
2. API client creation
3. Database setup
4. Sync worker execution
5. Results verification
"""

import sys
import logging
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from poe_search.utils.config import load_config
from poe_search.storage.database_manager import DatabaseManager
from poe_search.workers.sync_worker import SyncWorker
from poe_search.api.client_factory import create_poe_client
from PyQt6.QtCore import QCoreApplication

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SyncTester:
    """Test harness for sync functionality."""
    
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        self.config = None
        self.db_manager = None
        self.sync_worker = None
        self.results = {
            'config_loaded': False,
            'credentials_found': False,
            'database_initialized': False,
            'api_client_created': False,
            'sync_started': False,
            'sync_completed': False,
            'conversations_found': 0,
            'errors': []
        }
        
    def log_result(self, key: str, value, message: str = ""):
        """Log a test result."""
        self.results[key] = value
        status = "✅" if value else "❌"
        logger.info(f"{status} {key}: {value} {message}")
        
    def test_config_loading(self):
        """Test configuration loading."""
        try:
            logger.info("=== Testing Configuration Loading ===")
            self.config = load_config()
            self.log_result('config_loaded', True, "Configuration loaded successfully")
            
            # Check for tokens
            tokens = self.config.get_poe_tokens()
            has_formkey = bool(tokens.get('formkey'))
            has_p_b = bool(tokens.get('p-b'))
            
            logger.info(f"Formkey present: {has_formkey}")
            logger.info(f"P-B cookie present: {has_p_b}")
            
            if has_formkey and has_p_b:
                self.log_result('credentials_found', True, "Valid credentials found")
            else:
                self.log_result('credentials_found', False, "Missing credentials")
                self.results['errors'].append("Missing Poe.com credentials")
                
        except Exception as e:
            logger.error(f"Config loading failed: {e}")
            self.log_result('config_loaded', False, str(e))
            self.results['errors'].append(f"Config loading: {e}")
            
    def test_database_setup(self):
        """Test database initialization."""
        try:
            logger.info("=== Testing Database Setup ===")
            
            # Use data directory like the main app
            db_path = Path(__file__).parent.parent / "data" / "poe_search.db"
            db_path.parent.mkdir(exist_ok=True)
            
            logger.info(f"Database path: {db_path}")
            
            self.db_manager = DatabaseManager(str(db_path))
            self.log_result('database_initialized', True, f"Database at {db_path}")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            self.log_result('database_initialized', False, str(e))
            self.results['errors'].append(f"Database setup: {e}")
            
    def test_api_client(self):
        """Test API client creation."""
        try:
            logger.info("=== Testing API Client ===")
            
            if not self.results['credentials_found']:
                logger.warning("Skipping API client test - no credentials")
                return
                
            tokens = self.config.get_poe_tokens()
            client = create_poe_client(
                formkey=tokens['formkey'],
                p_b_cookie=tokens['p-b']
            )
            
            self.log_result('api_client_created', True, "API client created")
            
            # Test connection
            logger.info("Testing API connection...")
            if client.test_connection():
                logger.info("✅ API connection successful")
            else:
                logger.warning("⚠️ API connection test failed")
                self.results['errors'].append("API connection test failed")
                
        except Exception as e:
            logger.error(f"API client test failed: {e}")
            self.log_result('api_client_created', False, str(e))
            self.results['errors'].append(f"API client: {e}")
            
    def test_sync_worker(self):
        """Test the sync worker."""
        try:
            logger.info("=== Testing Sync Worker ===")
            
            if not all([
                self.results['config_loaded'],
                self.results['credentials_found'], 
                self.results['database_initialized']
            ]):
                logger.error("Prerequisites not met for sync test")
                return
                
            # Prepare credentials
            tokens = self.config.get_poe_tokens()
            credentials = {
                'formkey': tokens['formkey'],
                'p_b_cookie': tokens['p-b']
            }
            
            # Create sync worker
            self.sync_worker = SyncWorker(self.db_manager, credentials)
            
            # Connect signals
            self.sync_worker.progress.connect(self.on_sync_progress)
            self.sync_worker.status_update.connect(self.on_sync_status)
            self.sync_worker.error.connect(self.on_sync_error)
            self.sync_worker.finished.connect(self.on_sync_finished)
            self.sync_worker.conversation_synced.connect(self.on_conversation_synced)
            
            self.log_result('sync_started', True, "Sync worker started")
            
            # Start sync
            logger.info("Starting sync worker...")
            self.sync_worker.start()
            
            # Run Qt event loop for a limited time
            from PyQt6.QtCore import QTimer
            timeout_timer = QTimer()
            timeout_timer.timeout.connect(self.on_timeout)
            timeout_timer.start(30000)  # 30 second timeout
            
            self.app.exec()
            
        except Exception as e:
            logger.error(f"Sync worker test failed: {e}")
            self.log_result('sync_started', False, str(e))
            self.results['errors'].append(f"Sync worker: {e}")
            
    def on_sync_progress(self, progress: int):
        """Handle sync progress."""
        logger.info(f"Sync progress: {progress}%")
        
    def on_sync_status(self, status: str):
        """Handle sync status updates."""
        logger.info(f"Sync status: {status}")
        
    def on_sync_error(self, error: str):
        """Handle sync errors."""
        logger.error(f"Sync error: {error}")
        self.results['errors'].append(f"Sync error: {error}")
        self.app.quit()
        
    def on_sync_finished(self):
        """Handle sync completion."""
        logger.info("Sync completed successfully!")
        self.log_result('sync_completed', True, "Sync worker finished")
        
        # Count conversations
        try:
            # The DatabaseManager doesn't have a direct count method,
            # so we'll quit here and let the final report handle verification
            pass
        except Exception as e:
            logger.error(f"Error counting conversations: {e}")
            
        self.app.quit()
        
    def on_conversation_synced(self, conversation: dict):
        """Handle individual conversation sync."""
        title = conversation.get('title', 'Unknown')
        conv_id = conversation.get('id', 'Unknown')
        logger.info(f"Synced conversation: {title} (ID: {conv_id[:8]}...)")
        self.results['conversations_found'] += 1
        
    def on_timeout(self):
        """Handle sync timeout."""
        logger.warning("Sync test timed out after 30 seconds")
        self.results['errors'].append("Sync timeout")
        if self.sync_worker and self.sync_worker.isRunning():
            self.sync_worker.stop()
        self.app.quit()
        
    def print_final_report(self):
        """Print final test results."""
        logger.info("=== FINAL TEST RESULTS ===")
        
        # Print results
        for key, value in self.results.items():
            if key == 'errors':
                continue
            status = "✅" if value else "❌"
            logger.info(f"{status} {key}: {value}")
            
        # Print errors
        if self.results['errors']:
            logger.info("❌ ERRORS:")
            for error in self.results['errors']:
                logger.info(f"   - {error}")
        else:
            logger.info("✅ No errors detected")
            
        # Overall status
        critical_tests = ['config_loaded', 'database_initialized']
        critical_passed = all(self.results[test] for test in critical_tests)
        
        if critical_passed and not self.results['errors']:
            logger.info("🎉 ALL TESTS PASSED - Sync system is working!")
        elif critical_passed:
            logger.info("⚠️ BASIC TESTS PASSED - Some issues detected")
        else:
            logger.info("❌ CRITICAL TESTS FAILED - Sync system needs fixes")
            
    def run_all_tests(self):
        """Run all tests in sequence."""
        logger.info("🚀 Starting Poe Search Sync Test Suite")
        
        self.test_config_loading()
        self.test_database_setup()
        self.test_api_client()
        self.test_sync_worker()
        
        self.print_final_report()


if __name__ == "__main__":
    tester = SyncTester()
    tester.run_all_tests()
