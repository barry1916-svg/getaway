from http.server import BaseHTTPRequestHandler
import sys
import os
import json
import asyncio

# Add parent directory to path so we can import getaway
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import getaway


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            asyncio.run(getaway.main())
            body = json.dumps({"status": "ok"})
            status = 200
        except Exception as e:
            body = json.dumps({"status": "error", "message": str(e)})
            status = 500

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body.encode())
