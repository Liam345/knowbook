#!/usr/bin/env python3
"""
KnowBook Startup Script
Starts both backend and frontend services
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread

def run_backend():
    """Start the Flask backend server."""
    os.chdir('backend')
    try:
        subprocess.run([sys.executable, 'run.py'], check=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Backend error: {e}")

def run_frontend():
    """Start the React frontend server."""
    os.chdir('frontend')
    try:
        subprocess.run(['npm', 'run', 'dev'], check=True)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Frontend error: {e}")

def main():
    print("🚀 Starting KnowBook...")
    print("📚 Backend: http://localhost:5000")
    print("🌐 Frontend: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers\n")

    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()

    # Give backend time to start
    time.sleep(2)

    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down KnowBook...")
        # Cleanup happens automatically with daemon threads

if __name__ == '__main__':
    main()