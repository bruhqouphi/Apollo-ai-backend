#!/usr/bin/env python3
"""
Apollo AI Backend Server Startup Script
Simple script to start the FastAPI server with proper configuration.
"""

import uvicorn
import sys
from pathlib import Path

def main():
    """Start the Apollo AI backend server"""
    print("🚀 Starting Apollo AI Backend Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Configuration
    host = "0.0.0.0"
    port = 8000
    reload = True
    
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"📖 ReDoc Documentation: http://{host}:{port}/redoc")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 