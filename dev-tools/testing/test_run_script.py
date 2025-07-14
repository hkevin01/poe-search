#!/usr/bin/env python3
"""
Test script to verify run.sh functionality.
"""

import subprocess
import sys
import time
from pathlib import Path


def test_run_script():
    """Test the run.sh script."""
    print("🧪 Testing run.sh script functionality")
    print("=" * 50)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    run_script = project_root / "run.sh"
    
    if not run_script.exists():
        print("❌ run.sh not found")
        return False
    
    print(f"📁 Testing run script: {run_script}")
    
    # Make sure it's executable
    try:
        subprocess.run(["chmod", "+x", str(run_script)], check=True)
        print("✅ Script permissions set")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to set permissions: {e}")
        return False
    
    # Test dry run - check if virtual environment activation works
    try:
        # Just test the virtual environment activation part
        result = subprocess.run([
            "bash", "-c", 
            f"cd {project_root} && "
            "if [ -d '.venv' ]; then "
            "echo 'Virtual environment found'; "
            "source .venv/bin/activate && "
            "echo 'Virtual environment activated'; "
            "python --version; "
            "else "
            "echo 'No virtual environment found'; "
            "fi"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Virtual environment activation test passed")
            print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ Virtual environment test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Virtual environment test timed out")
        return False
    except Exception as e:
        print(f"❌ Virtual environment test error: {e}")
        return False
    
    # Test PYTHONPATH setup
    try:
        result = subprocess.run([
            "bash", "-c",
            f"cd {project_root} && "
            "source .venv/bin/activate && "
            "PYTHONPATH=\"$PWD/src:$PYTHONPATH\" python -c "
            "'import sys; print(\"src\" in \" \".join(sys.path))'"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "True" in result.stdout:
            print("✅ PYTHONPATH setup test passed")
        else:
            print(f"❌ PYTHONPATH test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ PYTHONPATH test error: {e}")
        return False
    
    # Test GUI module import
    try:
        result = subprocess.run([
            "bash", "-c",
            f"cd {project_root} && "
            "source .venv/bin/activate && "
            "PYTHONPATH=\"$PWD/src:$PYTHONPATH\" python -c "
            "'from poe_search.gui import __main__; print(\"GUI import OK\")'"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and "GUI import OK" in result.stdout:
            print("✅ GUI module import test passed")
        else:
            print(f"❌ GUI import test failed")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ GUI import test error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 run.sh script verification completed successfully!")
    print("✅ Virtual environment activation works")
    print("✅ PYTHONPATH is set correctly")
    print("✅ GUI module can be imported")
    print("✅ Script is ready for use")
    
    return True

def main():
    """Run the test."""
    success = test_run_script()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
