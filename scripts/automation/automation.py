#!/usr/bin/env python3
"""
Automation script for Poe Search development tasks.

This script provides various automation utilities for development, testing,
and deployment tasks.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class PoeSearchAutomation:
    """Automation utilities for Poe Search development."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.src_dir = self.project_root / "src" / "poe_search"
        self.tests_dir = self.project_root / "tests"
        self.docs_dir = self.project_root / "docs"

    def run_command(
        self, command: List[str], check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(
            command, cwd=self.project_root, capture_output=True, text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        if check and result.returncode != 0:
            print(f"Command failed with return code {result.returncode}")
            sys.exit(result.returncode)
            
        return result

    def install_dependencies(self, extras: Optional[str] = None) -> None:
        """Install project dependencies."""
        print("Installing dependencies...")
        
        if extras:
            self.run_command([sys.executable, "-m", "pip", "install", "-e", f".[{extras}]"])
        else:
            self.run_command([sys.executable, "-m", "pip", "install", "-e", "."])

    def run_tests(self, coverage: bool = True, verbose: bool = False) -> None:
        """Run the test suite."""
        print("Running tests...")
        
        cmd = [sys.executable, "-m", "pytest"]
        
        if coverage:
            cmd.extend([
                "--cov=poe_search", 
                "--cov-report=term-missing", 
                "--cov-report=html"
            ])
        
        if verbose:
            cmd.append("-v")
            
        cmd.append(str(self.tests_dir))
        
        self.run_command(cmd)

    def run_linting(self) -> None:
        """Run code linting and formatting checks."""
        print("Running linting checks...")
        
        # Run ruff
        self.run_command([sys.executable, "-m", "ruff", "check", "src/", "tests/"])
        
        # Run black check
        self.run_command([sys.executable, "-m", "black", "--check", "src/", "tests/"])
        
        # Run mypy
        self.run_command([sys.executable, "-m", "mypy", "src/poe_search/"])

    def format_code(self) -> None:
        """Format code using black and ruff."""
        print("Formatting code...")
        
        # Run black
        self.run_command([sys.executable, "-m", "black", "src/", "tests/"])
        
        # Run ruff fix
        self.run_command([sys.executable, "-m", "ruff", "check", "--fix", "src/", "tests/"])

    def build_docs(self) -> None:
        """Build documentation."""
        print("Building documentation...")
        
        if not self.docs_dir.exists():
            print("Documentation directory not found. Skipping docs build.")
            return
            
        self.run_command([sys.executable, "-m", "mkdocs", "build"])

    def serve_docs(self) -> None:
        """Serve documentation locally."""
        print("Serving documentation...")
        
        if not self.docs_dir.exists():
            print("Documentation directory not found.")
            return
            
        print("Documentation will be available at http://localhost:8000")
        self.run_command([sys.executable, "-m", "mkdocs", "serve"])

    def clean_project(self) -> None:
        """Clean build artifacts and temporary files."""
        print("Cleaning project...")
        
        # Remove Python cache files
        for pattern in ["__pycache__", "*.pyc", "*.pyo", "*.pyd"]:
            for path in self.project_root.rglob(pattern):
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
        
        # Remove test artifacts
        test_artifacts = [
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            "dist",
            "build",
            "*.egg-info"
        ]
        
        for pattern in test_artifacts:
            for path in self.project_root.glob(pattern):
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
        
        print("Project cleaned successfully.")

    def check_security(self) -> None:
        """Run security checks."""
        print("Running security checks...")
        
        try:
            # Run bandit
            self.run_command([sys.executable, "-m", "bandit", "-r", "src/poe_search/"])
        except subprocess.CalledProcessError:
            print("Bandit found security issues. Please review the output above.")
        
        try:
            # Run safety
            self.run_command([sys.executable, "-m", "safety", "check"])
        except subprocess.CalledProcessError:
            print("Safety found vulnerable dependencies. Please update them.")

    def build_package(self) -> None:
        """Build the package for distribution."""
        print("Building package...")
        
        # Clean previous builds
        self.clean_project()
        
        # Build package
        self.run_command([sys.executable, "-m", "build"])

    def run_gui(self) -> None:
        """Run the GUI application."""
        print("Starting GUI application...")
        
        try:
            self.run_command([sys.executable, "-m", "poe_search.gui"])
        except KeyboardInterrupt:
            print("\nGUI application stopped.")

    def run_cli(self, args: List[str]) -> None:
        """Run the CLI application with given arguments."""
        print(f"Running CLI with arguments: {' '.join(args)}")
        
        cmd = [sys.executable, "-m", "poe_search.cli"] + args
        self.run_command(cmd)

    def setup_dev_environment(self) -> None:
        """Set up the development environment."""
        print("Setting up development environment...")
        
        # Install development dependencies
        self.install_dependencies("dev,gui")
        
        # Install pre-commit hooks
        self.run_command([sys.executable, "-m", "pre_commit", "install"])
        
        # Run initial checks
        self.run_linting()
        self.run_tests(coverage=False)
        
        print("Development environment setup complete!")

    def create_release(self, version: str) -> None:
        """Create a new release."""
        print(f"Creating release {version}...")
        
        # Update version in __about__.py
        about_file = self.src_dir / "__about__.py"
        if about_file.exists():
            content = about_file.read_text()
            content = content.replace(
                '__version__ = "0.1.0"',
                f'__version__ = "{version}"'
            )
            about_file.write_text(content)
        
        # Build package
        self.build_package()
        
        # Run full test suite
        self.run_tests()
        
        # Run security checks
        self.check_security()
        
        print(f"Release {version} prepared successfully!")
        print("Next steps:")
        print("1. Review the changes")
        print("2. Commit and tag the release")
        print("3. Push to GitHub")
        print("4. Create GitHub release")

    def check_dependencies(self) -> None:
        """Check for outdated dependencies."""
        print("Checking for outdated dependencies...")
        
        self.run_command([sys.executable, "-m", "pip", "list", "--outdated"])

    def update_dependencies(self) -> None:
        """Update dependencies to latest versions."""
        print("Updating dependencies...")
        
        # Update pip
        self.run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Update all dependencies
        self.run_command([
            sys.executable, "-m", "pip", "install", "--upgrade", "-e", ".[dev,gui]"
        ])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Poe Search Development Automation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install dependencies")
    install_parser.add_argument("--extras", help="Extra dependencies to install")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--no-coverage", action="store_true", help="Skip coverage report")
    test_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Lint command
    subparsers.add_parser("lint", help="Run linting checks")
    
    # Format command
    subparsers.add_parser("format", help="Format code")
    
    # Docs commands
    docs_parser = subparsers.add_parser("docs", help="Documentation commands")
    docs_parser.add_argument("action", choices=["build", "serve"], help="Documentation action")
    
    # Clean command
    subparsers.add_parser("clean", help="Clean project artifacts")
    
    # Security command
    subparsers.add_parser("security", help="Run security checks")
    
    # Build command
    subparsers.add_parser("build", help="Build package")
    
    # GUI command
    subparsers.add_parser("gui", help="Run GUI application")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run CLI application")
    cli_parser.add_argument("args", nargs=argparse.REMAINDER, help="CLI arguments")
    
    # Setup command
    subparsers.add_parser("setup", help="Set up development environment")
    
    # Release command
    release_parser = subparsers.add_parser("release", help="Create a new release")
    release_parser.add_argument("version", help="Release version")
    
    # Dependencies commands
    deps_parser = subparsers.add_parser("deps", help="Dependency management")
    deps_parser.add_argument("action", choices=["check", "update"], help="Dependency action")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    automation = PoeSearchAutomation()
    
    try:
        if args.command == "install":
            automation.install_dependencies(args.extras)
        elif args.command == "test":
            automation.run_tests(coverage=not args.no_coverage, verbose=args.verbose)
        elif args.command == "lint":
            automation.run_linting()
        elif args.command == "format":
            automation.format_code()
        elif args.command == "docs":
            if args.action == "build":
                automation.build_docs()
            elif args.action == "serve":
                automation.serve_docs()
        elif args.command == "clean":
            automation.clean_project()
        elif args.command == "security":
            automation.check_security()
        elif args.command == "build":
            automation.build_package()
        elif args.command == "gui":
            automation.run_gui()
        elif args.command == "cli":
            automation.run_cli(args.args)
        elif args.command == "setup":
            automation.setup_dev_environment()
        elif args.command == "release":
            automation.create_release(args.version)
        elif args.command == "deps":
            if args.action == "check":
                automation.check_dependencies()
            elif args.action == "update":
                automation.update_dependencies()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 