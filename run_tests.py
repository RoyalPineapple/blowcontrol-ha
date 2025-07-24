#!/usr/bin/env python3
"""Test runner for BlowControl Home Assistant integration."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed!")
        print(f"Return code: {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def main():
    """Run all tests and generate coverage reports."""
    print("🧪 BlowControl Home Assistant Integration Test Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("custom_components/blowcontrol").exists():
        print("❌ Error: Must run from the project root directory")
        sys.exit(1)
    
    # Install test dependencies if needed
    print("\n📦 Installing test dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"], 
                      "Installing test dependencies"):
        print("❌ Failed to install test dependencies")
        sys.exit(1)
    
    # Run linting
    print("\n🔍 Running code quality checks...")
    if not run_command([sys.executable, "-m", "flake8", "custom_components/blowcontrol"], 
                      "Flake8 linting"):
        print("⚠️  Linting issues found")
    
    # Run type checking
    print("\n🔍 Running type checking...")
    if not run_command([sys.executable, "-m", "mypy", "custom_components/blowcontrol"], 
                      "MyPy type checking"):
        print("⚠️  Type checking issues found")
    
    # Run unit tests
    print("\n🧪 Running unit tests...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"], 
                      "Unit tests"):
        print("❌ Unit tests failed")
        sys.exit(1)
    
    # Run tests with coverage
    print("\n📊 Running tests with coverage...")
    if not run_command([sys.executable, "-m", "pytest", "tests/", "--cov=custom_components/blowcontrol", 
                       "--cov-report=term-missing", "--cov-report=html", "--cov-report=xml"], 
                      "Tests with coverage"):
        print("❌ Coverage tests failed")
        sys.exit(1)
    
    # Run specific test categories
    print("\n🎯 Running specific test categories...")
    
    test_categories = [
        ("coordinator", "Coordinator tests"),
        ("fan", "Fan entity tests"),
        ("binary_sensor", "Binary sensor tests"),
        ("sensor", "Sensor tests"),
        ("config_flow", "Config flow tests"),
        ("init", "Initialization tests"),
        ("integration", "Integration tests"),
    ]
    
    for marker, description in test_categories:
        if not run_command([sys.executable, "-m", "pytest", "tests/", "-m", marker, "-v"], 
                          description):
            print(f"⚠️  {description} had issues")
    
    # Generate coverage summary
    print("\n📈 Coverage Summary:")
    print("=" * 60)
    
    coverage_files = [
        "htmlcov/index.html",
        "coverage.xml",
    ]
    
    for file_path in coverage_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} generated")
        else:
            print(f"❌ {file_path} not found")
    
    print("\n🎉 Test suite completed!")
    print("\n📋 Next steps:")
    print("1. View coverage report: open htmlcov/index.html")
    print("2. Fix any failing tests")
    print("3. Address linting/type issues")
    print("4. Run tests again to verify fixes")


if __name__ == "__main__":
    main() 