from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
import json
import os

from ffmpeg_service import start_stream, stop_stream, stream_status, STREAM_DIR
from streams import STREAMS
from analytics import record_visit, record_listen_click, get_stats


class Handler(BaseHTTPRequestHandler):

    def get_host_name(self):
        host = self.headers.get("Host", "localhost:3000")
        return host.split(":")[0]

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

    def send_html(self, html):
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_listen_page(self):
        record_visit(
            self.client_address[0],
            self.headers.get("User-Agent", "")
        )

        hostname = self.get_host_name()
        buttons = ""

        for stream_id, stream in STREAMS.items():
            if stream["enabled"]:
                href = f"/listen/{stream_id}"
                status = "Available"
                disabled = ""
            else:
                href = "#"
                status = "Coming soon"
                disabled = "opacity: 0.45; pointer-events: none;"

            buttons += f"""
              <a style="{disabled}" href="{href}">
                {stream["label"]}
                <span>{status}</span>
              </a>
            """

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
      margin-top: 16px;
    }}
    a span {{
      display: block;
      font-size: 13px;
      font-weight: normal;
      margin-top: 6px;
      color: #dbe6ff;
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
    <p>Choose the TV audio you want to hear.</p>
    {buttons}
    <p class="small">Use your phone volume controls after joining.</p>
    <p class="small">Host: {hostname}</p>
  </div>
</body>
</html>
"""
        self.send_html(html)

    def send_stream_page(self, stream_id):
        stream = STREAMS.get(stream_id)

        if not stream:
            self.send_json({"error": "stream not found"}, 404)
            return

        if not stream["enabled"]:
            self.send_json({"error": "stream not enabled"}, 404)
            return

        record_listen_click(
            stream_id,
            self.client_address[0],
            self.headers.get("User-Agent", "")
        )

        hostname = self.get_host_name()
        webrtc_url = f"http://{hostname}:8889/{stream['path']}"

        html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>{stream["label"]}</title>
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
    .back {{
      background: #30394d;
      font-size: 16px;
    }}
    p {{
      color: #c8d0df;
      font-size: 17px;
      line-height: 1.5;
    }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{stream["label"]}</h1>
    <p>{stream["description"]}</p>
    <a href="{webrtc_url}">Tap to Listen</a>
    <a class="back" href="/listen">Choose another TV</a>
  </div>
</body>
</html>
"""
        self.send_html(html)

    def send_admin_page(self):
        stats = get_stats()

        html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>Venue Audio Admin</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="10">
  <style>
    body {{
      font-family: Arial, sans-serif;
      background: #10131a;
      color: white;
      margin: 0;
      padding: 24px;
    }}
    h1 {{
      font-size: 42px;
      margin: 0 0 24px 0;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 18px;
    }}
    .card {{
      background: #1b2230;
      border: 1px solid #30394d;
      border-radius: 20px;
      padding: 24px;
    }}
    .label {{
      color: #9aa8c0;
      font-size: 18px;
    }}
    .value {{
      font-size: 48px;
      font-weight: bold;
      margin-top: 10px;
    }}
    .ok {{
      color: #63e6be;
    }}
    .small {{
      color: #9aa8c0;
      font-size: 15px;
      margin-top: 24px;
    }}
  </style>
</head>
<body>
  <h1>Venue Audio Dashboard</h1>

  <div class="grid">
    <div class="card">
      <div class="label">System</div>
      <div class="value ok">LIVE</div>
    </div>

    <div class="card">
      <div class="label">Stream Mode</div>
      <div class="value">WebRTC</div>
    </div>

    <div class="card">
      <div class="label">Visits Today</div>
      <div class="value">{stats["today_visits"]}</div>
    </div>

    <div class="card">
      <div class="label">Listen Clicks Today</div>
      <div class="value">{stats["today_listen_clicks"]}</div>
    </div>

    <div class="card">
      <div class="label">Total Visits</div>
      <div class="value">{stats["total_visits"]}</div>
    </div>

    <div class="card">
      <div class="label">Total Listen Clicks</div>
      <div class="value">{stats["total_listen_clicks"]}</div>
    </div>
  </div>

  <p class="small">This page refreshes every 10 seconds.</p>
</body>
</html>
"""
        self.send_html(html)

    def do_GET(self):

        if self.path == "/":
            self.send_listen_page()
            return

        if self.path == "/listen":
            self.send_listen_page()
            return

        if self.path.startswith("/listen/"):
            stream_id = self.path.replace("/listen/", "")
            self.send_stream_page(stream_id)
            return

        if self.path == "/admin":
            self.send_admin_page()
            return

        if self.path == "/health":
            self.send_json({
                "status": "ok",
                "service": "venue-audio-edge-agent",
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