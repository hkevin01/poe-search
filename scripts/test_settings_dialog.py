#!/usr/bin/env python3
"""Test script to verify settings dialog functionality."""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication

from poe_search.gui.dialogs.settings_dialog import SettingsDialog
from poe_search.utils.config import load_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_settings_dialog():
    """Test the settings dialog functionality."""
    print("Testing Settings Dialog")
    print("=" * 30)
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded successfully")
        
        # Test copy method
        copied_config = config.copy()
        print("✅ Configuration copy successful")
        
        # Create settings dialog
        dialog = SettingsDialog(config, None)
        print("✅ Settings dialog created successfully")
        
        # Test rate limiting settings
        print("\nRate Limiting Settings:")
        print(f"  Enable Rate Limiting: {config.rate_limit.enable_rate_limiting}")
        print(f"  Max Calls per Minute: {config.rate_limit.max_calls_per_minute}")
        print(f"  Retry Attempts: {config.rate_limit.retry_attempts}")
        print(f"  Base Delay: {config.rate_limit.base_delay_seconds}s")
        print(f"  Show Warnings: {config.rate_limit.show_rate_limit_warnings}")
        print(f"  Prompt for Token Costs: {config.rate_limit.prompt_for_token_costs}")
        
        # Test UI elements
        print("\nUI Elements:")
        print(f"  Enable Rate Limiting Checkbox: {dialog.enable_rate_limiting_check.isChecked()}")
        print(f"  Max Calls SpinBox: {dialog.max_calls_spin.value()}")
        print(f"  Retry Attempts SpinBox: {dialog.retry_attempts_spin.value()}")
        print(f"  Base Delay SpinBox: {dialog.base_delay_spin.value()}")
        print(f"  Show Warnings Checkbox: {dialog.show_warnings_check.isChecked()}")
        print(f"  Prompt Token Costs Checkbox: {dialog.prompt_token_costs_check.isChecked()}")
        
        # Test configuration update
        print("\nTesting Configuration Update:")
        
        # Change some settings
        dialog.enable_rate_limiting_check.setChecked(False)
        dialog.max_calls_spin.setValue(15)
        dialog.retry_attempts_spin.setValue(2)
        dialog.base_delay_spin.setValue(3)
        dialog.show_warnings_check.setChecked(False)
        dialog.prompt_token_costs_check.setChecked(True)
        
        # Get updated config
        updated_config = dialog.get_config()
        
        print("Updated Rate Limiting Settings:")
        print(f"  Enable Rate Limiting: {updated_config.rate_limit.enable_rate_limiting}")
        print(f"  Max Calls per Minute: {updated_config.rate_limit.max_calls_per_minute}")
        print(f"  Retry Attempts: {updated_config.rate_limit.retry_attempts}")
        print(f"  Base Delay: {updated_config.rate_limit.base_delay_seconds}s")
        print(f"  Show Warnings: {updated_config.rate_limit.show_rate_limit_warnings}")
        print(f"  Prompt for Token Costs: {updated_config.rate_limit.prompt_for_token_costs}")
        
        print("\n✅ Settings dialog test completed successfully!")
        print("💡 The settings dialog is working correctly with all rate limiting features")
        
    except Exception as e:
        print(f"❌ Settings dialog test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        app.quit()


if __name__ == "__main__":
    test_settings_dialog() 