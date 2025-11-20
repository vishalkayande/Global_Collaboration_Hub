#!/usr/bin/env python3
"""
Backend Server Runner
This script starts the Flask backend server with proper configuration.
"""

import os
import sys
import subprocess
import platform

def main():
    """Start the backend server"""
    print("🚀 Starting Global Collaboration Hub Backend Server...")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    os.chdir(backend_dir)
    
    # Determine the correct Python executable
    if platform.system() == "Windows":
        python_cmd = os.path.join("venv", "Scripts", "python.exe")
    else:
        python_cmd = os.path.join("venv", "bin", "python")
    
    # Check if virtual environment exists
    if not os.path.exists(python_cmd):
        print("❌ Virtual environment not found. Please run setup.py first.")
        sys.exit(1)
    
    # .env optional; continue if missing
    
    print("✅ Starting server on http://127.0.0.1:5500/frontend/login.html")
    print("📝 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the Flask application
        subprocess.run([python_cmd, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
