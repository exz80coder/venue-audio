from datetime import datetime, date
from datetime import timedelta
import json
import os

DATA_FILE = "/home/gfurse/venue-audio/edge-agent/analytics.json"


def _load():
    if not os.path.exists(DATA_FILE):
        return {
            "visits": [],
            "listen_clicks": []
        }

    with open(DATA_FILE, "r") as file:
        return json.load(file)

def get_peak_listeners():
    return get_current_listeners()
    
def _save(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=2)


def record_visit(ip, user_agent):
    data = _load()
    data["visits"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip,
        "user_agent": user_agent
    })
    _save(data)


def record_listen_click(stream_id, ip, user_agent):
    data = _load()
    data["listen_clicks"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "stream_id": stream_id,
        "ip": ip,
        "user_agent": user_agent
    })
    _save(data)


def get_stats():
    data = _load()
    today = date.today().isoformat()

    today_visits = [
        item for item in data["visits"]
        if item["timestamp"].startswith(today)
    ]

    today_clicks = [
        item for item in data["listen_clicks"]
        if item["timestamp"].startswith(today)
    ]

    return {
        "total_visits": len(data["visits"]),
        "today_visits": len(today_visits),
        "total_listen_clicks": len(data["listen_clicks"]),
        "today_listen_clicks": len(today_clicks),
        "recent_listen_clicks": data["listen_clicks"][-10:]
    }
def heartbeat(session_id, stream_id):
    data = _load()

    if "heartbeats" not in data:
        data["heartbeats"] = {}

    data["heartbeats"][session_id] = {
        "stream_id": stream_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    _save(data)


def get_current_listeners():
    data = _load()

    if "heartbeats" not in data:
        return 0

    active = 0
    cutoff = datetime.utcnow() - timedelta(seconds=30)

    for session in data["heartbeats"].values():
        try:
            ts = datetime.fromisoformat(session["timestamp"])

            if ts > cutoff:
                active += 1

        except Exception:
            pass

    return active
