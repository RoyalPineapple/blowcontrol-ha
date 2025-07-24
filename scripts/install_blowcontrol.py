#!/usr/bin/env python3
"""
BlowControl CLI Installation Helper

This script helps install the BlowControl CLI tool that's required for the Home Assistant integration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def check_pip():
    """Check if pip is available."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip is not available")
        return False


def install_dependencies():
    """Install required Python dependencies."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "paho-mqtt", "python-dotenv"
        ], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def install_blowcontrol():
    """Install BlowControl CLI from GitHub."""
    print("\n🚀 Installing BlowControl CLI...")
    
    # Check if blowcontrol is already installed
    if shutil.which("blowcontrol"):
        print("✅ BlowControl CLI is already installed")
        return True
    
    try:
        # Clone BlowControl repository
        print("📥 Cloning BlowControl repository...")
        subprocess.run([
            "git", "clone", "https://github.com/RoyalPineapple/blowcontrol.git"
        ], check=True)
        
        # Install BlowControl
        print("🔧 Installing BlowControl...")
        os.chdir("blowcontrol")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], check=True)
        
        # Clean up
        os.chdir("..")
        shutil.rmtree("blowcontrol")
        
        print("✅ BlowControl CLI installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install BlowControl: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False


def verify_installation():
    """Verify that BlowControl CLI is working."""
    print("\n🔍 Verifying installation...")
    
    try:
        result = subprocess.run(
            ["blowcontrol", "--help"], 
            capture_output=True, text=True, check=True
        )
        print("✅ BlowControl CLI is working correctly")
        print("📋 Available commands:")
        for line in result.stdout.split('\n'):
            if line.strip() and not line.startswith('usage:'):
                print(f"   {line.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ BlowControl CLI is not working correctly")
        return False


def create_env_template():
    """Create a template .env file."""
    print("\n📝 Creating .env template...")
    
    env_content = """# BlowControl Configuration Template
# Copy this file to your Home Assistant config directory and fill in your values

DEVICE_IP=192.168.1.100
MQTT_PORT=1883
MQTT_PASSWORD=your-mqtt-password
ROOT_TOPIC=438M
SERIAL_NUMBER=your-device-serial
"""
    
    try:
        with open("blowcontrol.env.template", "w") as f:
            f.write(env_content)
        print("✅ Created blowcontrol.env.template")
        print("📋 Edit this file with your device credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create template: {e}")
        return False


def main():
    """Main installation function."""
    print("🔧 BlowControl CLI Installation Helper")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        print("\n💡 To install pip, visit: https://pip.pypa.io/en/stable/installation/")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Install BlowControl
    if not install_blowcontrol():
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        sys.exit(1)
    
    # Create template
    create_env_template()
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit blowcontrol.env.template with your device credentials")
    print("2. Copy the .env file to your Home Assistant config directory")
    print("3. Restart Home Assistant")
    print("4. Configure the BlowControl integration")
    
    print("\n📚 For more information:")
    print("   - BlowControl: https://github.com/RoyalPineapple/blowcontrol")
    print("   - Home Assistant Integration: https://github.com/RoyalPineapple/blowcontrol-ha")


if __name__ == "__main__":
    main() 