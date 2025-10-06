"""
Bookstore Multi-Agent Simulation Dashboard Launcher

This script:
1. Checks and installs required dependencies
2. Starts the Flask web server
3. Automatically opens the dashboard in your default web browser

Usage:
    python launch_dashboard.py
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("   BOOKSTORE MULTI-AGENT SIMULATION DASHBOARD")
    print("   Real-time Monitoring & Analytics Platform")
    print("="*70 + "\n")

def check_python_version():
    """Ensure Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def install_dependencies():
    """Install required packages from requirements.txt"""
    print("\n📦 Checking dependencies...")
    
    frontend_req = Path(__file__).parent / "frontend" / "requirements.txt"
    main_req = Path(__file__).parent / "requirements.txt"
    
    if not frontend_req.exists() and not main_req.exists():
        print("⚠️  Warning: No requirements.txt found. Proceeding anyway...")
        return
    
    try:
        # Check if Flask is installed
        import flask
        print("✓ Flask is already installed")
    except ImportError:
        print("📥 Installing Flask and dependencies...")
        try:
            if frontend_req.exists():
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(frontend_req), "-q"
                ])
            print("✓ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Some dependencies failed to install: {e}")
            print("   Continuing anyway...")
    
    # Install main requirements if not already done
    try:
        import mesa
        import owlready2
        print("✓ Mesa and Owlready2 are installed")
    except ImportError:
        if main_req.exists():
            print("📥 Installing simulation dependencies...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", str(main_req), "-q"
                ])
                print("✓ Simulation dependencies installed")
            except subprocess.CalledProcessError:
                print("⚠️  Warning: Some simulation dependencies failed to install")

def start_server():
    """Start the Flask server in a subprocess"""
    print("\n🚀 Starting Flask server...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    app_path = frontend_dir / "app.py"
    
    if not app_path.exists():
        print(f"❌ Error: app.py not found at {app_path}")
        sys.exit(1)
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Start Flask server
    print("   Server starting at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server\n")
    
    # Start server process
    try:
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open browser
        print("🌐 Opening dashboard in your default browser...")
        webbrowser.open("http://localhost:5000")
        
        print("\n" + "="*70)
        print("✓ Dashboard is now running!")
        print("="*70)
        print("\n📍 Dashboard URL: http://localhost:5000")
        print("\n📄 Available Pages:")
        print("   • Main Dashboard:        http://localhost:5000/")
        print("   • Graphs & Analytics:    http://localhost:5000/graphs")
        print("   • Agent Details:         http://localhost:5000/agents")
        print("   • Rules Execution:       http://localhost:5000/rules")
        print("   • Messages Log:          http://localhost:5000/messages")
        print("   • Summary & Export:      http://localhost:5000/summary")
        print("\n💡 Tips:")
        print("   • Use the control panel to configure and start simulations")
        print("   • Watch real-time updates in the terminal console")
        print("   • Toggle dark/light theme with the moon/sun button")
        print("   • Export reports in PDF, JSON, or Excel format")
        print("\n⚠️  Press Ctrl+C in this terminal to stop the server")
        print("="*70 + "\n")
        
        # Stream output
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        process.terminate()
        process.wait()
        print("✓ Server stopped successfully")
        print("\n👋 Thank you for using Bookstore MAS Dashboard!\n")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main launcher function"""
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Start server and open browser
    start_server()

if __name__ == "__main__":
    main()
