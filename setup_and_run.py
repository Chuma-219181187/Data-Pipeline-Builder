"""
Simple Dashboard Launcher with Setup Check
Checks dependencies and provides setup instructions
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python():
    """Check if Python is available"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Python found: {result.stdout.strip()}")
        return True
    except:
        print("❌ Python not found!")
        return False

def check_package(package):
    """Check if a package is installed"""
    try:
        __import__(package)
        print(f"✅ {package} is installed")
        return True
    except ImportError:
        print(f"❌ {package} is not installed")
        return False

def install_packages():
    """Install required packages"""
    packages = ["streamlit", "plotly", "pandas", "numpy"]
    
    print("🔧 Installing required packages...")
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def run_dashboard():
    """Run the Streamlit dashboard"""
    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard not found at: {dashboard_path}")
        return False
    
    print("🚀 Starting dashboard...")
    print("📱 Dashboard will open in your browser")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--browser.gatherUsageStats", "false"
        ])
        return True
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped")
        return True
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")
        return False

def main():
    """Main setup and launch function"""
    print("🎯 E-Commerce Dashboard Setup & Launch")
    print("=" * 50)
    
    # Check Python
    if not check_python():
        print("\n📥 Python Installation Required:")
        print("1. Install from Microsoft Store: Search 'Python 3.11'")
        print("2. OR download from: https://python.org/downloads")
        print("3. Make sure to check 'Add Python to PATH'")
        print("4. Restart command prompt and run this script again")
        input("\nPress Enter to exit...")
        return
    
    # Check packages
    required_packages = ["streamlit", "plotly", "pandas", "numpy"]
    missing_packages = []
    
    print("\n🔍 Checking required packages...")
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    # Install missing packages
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        
        install_choice = input("Install missing packages? (y/n): ").lower()
        if install_choice == 'y':
            if not install_packages():
                print("❌ Package installation failed!")
                input("Press Enter to exit...")
                return
        else:
            print("❌ Cannot run dashboard without required packages")
            input("Press Enter to exit...")
            return
    
    print("\n✅ All requirements satisfied!")
    
    # Run dashboard
    print("\n🚀 Launching Dashboard...")
    run_dashboard()

if __name__ == "__main__":
    main()