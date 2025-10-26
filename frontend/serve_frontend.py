#!/usr/bin/env python3
"""
Simple HTTP server for the frontend
This allows the HTML to properly make requests to the API
"""
import http.server
import socketserver
import os

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 70)
        print(f"🌐 Frontend Server Started!")
        print("=" * 70)
        print(f"📍 URL: http://localhost:{PORT}")
        print(f"📂 Serving: {DIRECTORY}")
        print()
        print("💡 Instructions:")
        print("   1. Make sure API is running: python api_endpoint_v2.py")
        print("   2. Open browser: http://localhost:8000")
        print()
        print("Press Ctrl+C to stop the server")
        print("=" * 70)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")
