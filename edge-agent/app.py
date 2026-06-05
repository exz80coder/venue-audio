from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
import json
import os

from ffmpeg_service import start_stream, stop_stream, stream_status, STREAM_DIR
from streams import STREAMS
from analytics import (
    record_visit,
    record_listen_click,
    get_stats,
    heartbeat,
    get_current_listeners
)
from pages import (
    render_listen_page,
    render_stream_page,
    render_admin_page
)


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
        html = render_listen_page(hostname, STREAMS)
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
        session_id = f"{self.client_address[0]}-{datetime.utcnow().timestamp()}"

        html = render_stream_page(
            stream=stream,
            stream_id=stream_id,
            webrtc_url=webrtc_url,
            session_id=session_id
        )

        self.send_html(html)

    def send_admin_page(self):
        stats = get_stats()
        current_listeners = get_current_listeners()

        html = render_admin_page(
            stats=stats,
            current_listeners=current_listeners
        )

        self.send_html(html)

    def handle_ping(self):
        try:
            query = self.path.split("?")[1]
            params = {}

            for item in query.split("&"):
                key, value = item.split("=")
                params[key] = value

            heartbeat(
                params["session"],
                params["stream"]
            )

            self.send_json({"status": "ok"})
            return

        except Exception as ex:
            self.send_json({"error": str(ex)}, 400)
            return

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

        if self.path.startswith("/ping"):
            self.handle_ping()
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