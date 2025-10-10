#!/usr/bin/env python3
"""
NGO Collaboration Hub - Single Command Launcher
Starts backend server and opens frontend in browser
"""

import os
import sys
import subprocess
import time
import webbrowser
import threading
import platform

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend Server...")
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Determine Python executable
    if platform.system() == "Windows":
        python_cmd = os.path.join("venv", "Scripts", "python.exe")
    else:
        python_cmd = os.path.join("venv", "bin", "python")
    
    # Start the Flask application
    try:
        subprocess.run([python_cmd, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def open_frontend():
    """Open frontend in browser"""
    print("🌐 Opening Frontend...")
    time.sleep(3)  # Wait for backend to start
    
    # Get the absolute path to frontend
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    frontend_url = f"file:///{frontend_path.replace(os.sep, '/')}"
    
    print(f"📱 Opening: {frontend_url}")
    webbrowser.open(frontend_url)

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🎯 NGO Collaboration Hub - Single Command Launcher")
    print("=" * 60)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Open frontend
    open_frontend()
    
    print("\n✅ Project Started Successfully!")
    print("📋 Available URLs:")
    print("   • Frontend: file:///path/to/frontend/index.html")
    print("   • Backend API: http://localhost:5000/api")
    print("   • Health Check: http://localhost:5000/api/health")
    print("\n📝 Press Ctrl+C to stop all services")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()

