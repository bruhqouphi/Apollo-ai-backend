#!/usr/bin/env python3
"""
Apollo AI - One-Click Demo Launcher
Starts server, opens browser, and provides testing workflow
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def print_banner():
    print("""
🚀 APOLLO AI - DEMO LAUNCHER
==================================================
🎯 Starting server and opening demo interface...
==================================================
""")

def activate_venv():
    """Activate virtual environment"""
    venv_path = Path("apollo_env")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("💡 Run: python -m venv apollo_env")
        return False
    
    # For Windows
    if os.name == 'nt':
        activate_script = venv_path / "Scripts" / "Activate.ps1"
        if activate_script.exists():
            print("✅ Virtual environment found")
            return True
        else:
            print("❌ Activation script not found")
            return False
    else:
        activate_script = venv_path / "bin" / "activate"
        if activate_script.exists():
            print("✅ Virtual environment found")
            return True
        else:
            print("❌ Activation script not found")
            return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Apollo AI Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📖 ReDoc Documentation: http://localhost:8000/redoc")
    print("=" * 50)
    
    # Start server in background
    try:
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def open_browser():
    """Open browser to API docs"""
    print("🌐 Opening browser to API documentation...")
    time.sleep(3)  # Wait for server to start
    
    try:
        webbrowser.open("http://localhost:8000/docs")
        print("✅ Browser opened successfully!")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print("💡 Manual URL: http://localhost:8000/docs")

def show_testing_workflow():
    """Show testing workflow instructions"""
    print("""
🎯 TESTING WORKFLOW
==================================================
1. 📁 UPLOAD FILE:
   - Click "Try it out" on POST /upload
   - Upload a CSV file (use sample data in /uploads folder)
   - Copy the file_id from response

2. 📊 ANALYZE DATA:
   - Click "Try it out" on POST /analyze
   - Paste the file_id
   - Get comprehensive analysis in 0.2s

3. 🤖 GENERATE AI INSIGHTS:
   - Click "Try it out" on POST /insight
   - Paste the file_id
   - Choose AI provider (groq, anthropic, etc.)
   - Get AI-powered insights

4. 📈 CREATE VISUALIZATIONS:
   - Click "Try it out" on GET /visualize/{file_id}
   - Get available chart types
   - Use POST /visualize/{file_id}/{chart_type} to generate charts

5. 📄 EXPORT REPORTS:
   - Use POST /export/{file_id} for PDF/HTML reports

==================================================
💡 PRO TIPS:
- Use the sample CSV files in /uploads folder
- Test with different file sizes
- Try different AI providers
- Check response times (should be <1s)
==================================================
""")

def main():
    print_banner()
    
    # Check virtual environment
    if not activate_venv():
        print("💡 Please activate virtual environment manually:")
        print("   apollo_env\\Scripts\\Activate.ps1")
        return
    
    # Start server
    if not start_server():
        print("💡 Please start server manually:")
        print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Open browser
    open_browser()
    
    # Show workflow
    show_testing_workflow()
    
    print("""
🎉 DEMO READY!
==================================================
✅ Server running: http://localhost:8000
✅ API Docs open: http://localhost:8000/docs
✅ Testing workflow provided above

Press Ctrl+C to stop the server when done
==================================================
""")

if __name__ == "__main__":
    main() 