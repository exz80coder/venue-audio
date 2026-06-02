from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = {
                "status": "ok",
                "service": "venue-audio-edge-agent",
                "audio_input": "StarTech Line In",
                "timestamp": datetime.utcnow().isoformat()
            }

            data = json.dumps(body).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()

server = HTTPServer(("0.0.0.0", 3000), Handler)
print("Venue Audio Edge Agent running on port 3000")
server.serve_forever()
