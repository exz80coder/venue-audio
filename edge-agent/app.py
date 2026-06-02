from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
import json
import os

from audio_monitor import get_audio_level
from ffmpeg_service import start_stream, stop_stream, stream_status, STREAM_DIR


WEBRTC_URL = "http://192.168.0.2:8889/venueaudio"


class Handler(BaseHTTPRequestHandler):

    def send_json(self, body, status=200):
        data = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
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

    def send_listen_page(self):
        html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Venue Audio</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: Arial, sans-serif;
      background: #10131a;
      color: white;
      text-align: center;
      padding: 40px 20px;
      margin: 0;
    }}
    .card {{
      max-width: 420px;
      margin: auto;
      background: #1b2230;
      border: 1px solid #30394d;
      border-radius: 20px;
      padding: 30px;
    }}
    h1 {{
      margin-top: 0;
      font-size: 32px;
    }}
    p {{
      color: #c8d0df;
      font-size: 17px;
      line-height: 1.5;
    }}
    a {{
      display: block;
      background: #2f80ed;
      color: white;
      padding: 18px;
      border-radius: 14px;
      text-decoration: none;
      font-size: 20px;
      font-weight: bold;
      margin-top: 24px;
    }}
    .small {{
      margin-top: 20px;
      font-size: 13px;
      color: #8f9bb0;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Venue Audio</h1>
    <p>Listen to the live TV audio on your phone.</p>
    <a href="{WEBRTC_URL}">Tap to Listen</a>
    <p class="small">Use your phone volume controls after joining.</p>
  </div>
</body>
</html>
"""
        data = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):

        if self.path == "/":
            self.send_listen_page()
            return

        if self.path == "/listen":
            self.send_listen_page()
            return

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
                "audio": get_audio_level(),
                "timestamp": datetime.now(timezone.utc).isoformat()
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
