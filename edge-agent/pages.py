def render_listen_page(hostname, streams):
    buttons = ""

    for stream_id, stream in streams.items():
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

    return f"""
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


def render_stream_page(stream, stream_id, webrtc_url, session_id):
    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>{stream["label"]}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <script>
    function sendHeartbeat() {{
      fetch("/ping?session={session_id}&stream={stream_id}")
        .catch(() => {{}});
    }}

    setInterval(sendHeartbeat, 10000);
    window.onload = sendHeartbeat;
  </script>

  <style>
    body {{
      font-family: Arial, sans-serif;
      background: #10131a;
      color: white;
      text-align: center;
      padding: 20px;
      margin: 0;
    }}

    .card {{
      max-width: 520px;
      margin: auto;
      background: #1b2230;
      border: 1px solid #30394d;
      border-radius: 20px;
      padding: 24px;
    }}

    h1 {{
      margin-top: 0;
      font-size: 30px;
    }}

    p {{
      color: #c8d0df;
      font-size: 17px;
      line-height: 1.5;
    }}

    iframe {{
      width: 100%;
      height: 360px;
      border: 0;
      border-radius: 16px;
      background: #000;
      margin-top: 20px;
    }}

    .back {{
      display: block;
      background: #30394d;
      color: white;
      padding: 16px;
      border-radius: 14px;
      text-decoration: none;
      font-size: 16px;
      font-weight: bold;
      margin-top: 20px;
    }}

    .small {{
      margin-top: 16px;
      font-size: 13px;
      color: #8f9bb0;
    }}
  </style>
</head>

<body>
  <div class="card">
    <h1>{stream["label"]}</h1>
    <p>{stream["description"]}</p>

    <iframe src="{webrtc_url}" allow="autoplay; microphone; speaker"></iframe>

    <a class="back" href="/listen">Choose another TV</a>

    <p class="small">Keep this page open while listening.</p>
  </div>
</body>
</html>
"""


def render_admin_page(stats, current_listeners):
    return f"""
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
      <div class="label">Current Listeners</div>
      <div class="value">{current_listeners}</div>
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
      <div class="label">Total Listen Clicks</div>
      <div class="value">{stats["total_listen_clicks"]}</div>
    </div>
  </div>

  <p class="small">This page refreshes every 10 seconds.</p>
</body>
</html>
"""
