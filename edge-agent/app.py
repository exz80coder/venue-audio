from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
import json
import os

from audio_monitor import get_audio_level
from ffmpeg_service import start_stream, stop_stream, stream_status, STREAM_DIR


class Handler(BaseHTTPRequestHandler):

    def send_json(self, body, status=200):
        data = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path, content_type):
        if not os.path.exists(path):
            self.send_json({"error": "file not found"}, 404)
            return

        with open(path, "rb") as file:
            data = file.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
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
            self.send_json({
                "status": "ok",
                "audio": get_audio_level()
            })
            return

        if self.path == "/stream/status":
            self.send_json(stream_status())
            return

        if self.path == "/stream/live.m3u8":
            self.send_file(
                f"{STREAM_DIR}/live.m3u8",
                "application/vnd.apple.mpegurl"
            )
            return

        if self.path.startswith("/stream/") and self.path.endswith(".ts"):
            filename = self.path.replace("/stream/", "")
            self.send_file(
                f"{STREAM_DIR}/{filename}",
                "video/MP2T"
            )
            return

        self.send_json({"error": "not found"}, 404)

    def do_POST(self):

        if self.path == "/stream/start":
            self.send_json(start_stream())
            return

        if self.path == "/stream/stop":
            self.send_json(stop_stream())
            return

        self.send_json({"error": "not found"}, 404)


server = HTTPServer(("0.0.0.0", 3000), Handler)

print("Venue Audio Edge Agent running on port 3000")

server.serve_forever()
