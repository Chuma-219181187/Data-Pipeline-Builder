#!/usr/bin/env python3
"""
Simple Dashboard Launcher
Ensures the dashboard runs with the correct Python installation
"""

import sys
import subprocess
import os

def check_and_install_packages():
    """Install required packages if not already installed"""
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy']
    
    print("🔍 Checking required packages...")
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
                print(f"✅ {package} - installed successfully")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("\n🚀 Launching E-Commerce Analytics Dashboard...")
    print("📍 Dashboard URL: http://localhost:8501")
    print("⚠️  Press Ctrl+C to stop the dashboard")
    print("🌐 Opening in your default browser...\n")
    
    # Change to dashboard directory
    dashboard_dir = os.path.join(os.path.dirname(__file__), 'dashboard')
    app_file = os.path.join(dashboard_dir, 'app.py')
    
    if not os.path.exists(app_file):
        print(f"❌ Dashboard file not found: {app_file}")
        print("💡 Make sure you're running this from the project root directory")
        return False
    
    try:
        # Use subprocess to run streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', app_file, '--browser.gatherUsageStats', 'false']
        subprocess.run(cmd, cwd=dashboard_dir)
        return True
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {str(e)}")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🚀 E-Commerce Analytics Dashboard Launcher")
    print("=" * 50)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Install packages if needed
    if not check_and_install_packages():
        print("\n❌ Package installation failed!")
        print("💡 Try running: pip install streamlit plotly pandas numpy")
        input("\nPress Enter to exit...")
        return
    
    # Launch dashboard
    if not launch_dashboard():
        print("\n💡 Alternative: Open 'static_dashboard.html' for instant demo")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()