#!/usr/bin/env python3
"""
Global Collaboration Hub - Single Command Launcher
Sets up venv (if needed), installs deps, starts backend, and opens frontend.
"""

import os
import sys
import subprocess
import time
import webbrowser
import platform


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
FRONTEND_INDEX = os.path.join(FRONTEND_DIR, 'index.html')


def venv_python_path():
    if platform.system() == 'Windows':
        return os.path.join(BACKEND_DIR, 'venv', 'Scripts', 'python.exe')
    return os.path.join(BACKEND_DIR, 'venv', 'bin', 'python')


def venv_pip_path():
    if platform.system() == 'Windows':
        return os.path.join(BACKEND_DIR, 'venv', 'Scripts', 'pip.exe')
    return os.path.join(BACKEND_DIR, 'venv', 'bin', 'pip')


def ensure_venv_and_dependencies():
    print('🔧 Preparing environment...')
    py = sys.executable
    venv_dir = os.path.join(BACKEND_DIR, 'venv')
    if not os.path.exists(venv_dir):
        print('📦 Creating virtual environment...')
        subprocess.check_call([py, '-m', 'venv', venv_dir])
    pip = venv_pip_path()
    print('⬆️  Upgrading pip...')
    subprocess.check_call([pip, 'install', '--upgrade', 'pip'])
    print('📚 Installing requirements...')
    subprocess.check_call([pip, 'install', '-r', os.path.join(BACKEND_DIR, 'requirements.txt')])


def start_backend():
    print('🚀 Starting Global Collaboration Hub backend on http://localhost:5000')
    env = os.environ.copy()
    # Ensure we run from backend directory
    cwd = BACKEND_DIR
    return subprocess.Popen([venv_python_path(), 'app.py'], cwd=cwd)

def start_frontend_server():
    print('🌐 Starting frontend server on http://localhost:8000')
    # Serve the frontend using Python's http.server
    # Use system python for static server (no venv dependency needed)
    return subprocess.Popen([sys.executable, '-m', 'http.server', '8000'], cwd=FRONTEND_DIR)


def main():
    try:
        ensure_venv_and_dependencies()
        be_proc = start_backend()
        fe_proc = start_frontend_server()
        time.sleep(2)
        # Open browser URL (not a file) to avoid opening in editors
        target_url = 'http://localhost:8000/login.html' if os.path.exists(os.path.join(FRONTEND_DIR, 'login.html')) else 'http://localhost:8000/index.html'
        print('🌐 Opening browser...')
        webbrowser.open_new_tab(target_url)
        print('📝 Press Ctrl+C to stop.')
        # Wait on backend; frontend server will stop when this script exits
        be_proc.wait()
    except KeyboardInterrupt:
        print('\n🛑 Stopping...')
    finally:
        # Best-effort cleanup of child servers
        try:
            for p in ['be_proc', 'fe_proc']:
                proc = locals().get(p)
                if proc and proc.poll() is None:
                    proc.terminate()
        except Exception:
            pass


if __name__ == '__main__':
    main()


