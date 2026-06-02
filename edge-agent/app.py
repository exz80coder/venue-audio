from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
import json

from audio_monitor import get_audio_level

class Handler(BaseHTTPRequestHandler):
    def send_json(self, body, status=200):
        data = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.send_json({
                "status": "ok",
                "service": "venue-audio-edge-agent",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return

        if self.path == "/audio-status":
            level = get_audio_level()
            self.send_json({
                "status": "ok",
                "service": "venue-audio-edge-agent",
                "audio": level,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return

        self.send_json({"error": "not found"}, 404)

server = HTTPServer(("0.0.0.0", 3000), Handler)
print("Venue Audio Edge Agent running on port 3000")
server.serve_forever()
