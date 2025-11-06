"""
Dashboard Launcher
Easy way to start the Streamlit dashboard
"""

import subprocess
import sys
from pathlib import Path
import os

def main():
    """Launch the Streamlit dashboard"""
    
    # Get the dashboard directory
    dashboard_dir = Path(__file__).parent
    app_path = dashboard_dir / "app.py"
    
    if not app_path.exists():
        print("❌ Dashboard app.py not found!")
        return
    
    print("🚀 Starting E-Commerce Analytics Dashboard...")
    print(f"📁 Dashboard location: {dashboard_dir}")
    print(f"🌐 Opening in your default browser...")
    print(f"⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Run Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--browser.gatherUsageStats", "false"
        ], cwd=dashboard_dir)
        
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped successfully!")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()