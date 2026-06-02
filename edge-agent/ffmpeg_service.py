import subprocess
import os
import signal

AUDIO_DEVICE = "plughw:0,0"
STREAM_DIR = "/home/gfurse/venue-audio/edge-agent/stream"
PLAYLIST = f"{STREAM_DIR}/live.m3u8"

ffmpeg_process = None

def start_stream():
    global ffmpeg_process

    if ffmpeg_process and ffmpeg_process.poll() is None:
        return {
            "running": True,
            "message": "stream already running",
            "playlist": "/stream/live.m3u8"
        }

    os.makedirs(STREAM_DIR, exist_ok=True)

    for file in os.listdir(STREAM_DIR):
        os.remove(os.path.join(STREAM_DIR, file))

    cmd = [
        "ffmpeg",
        "-f", "alsa",
        "-ar", "48000",
        "-ac", "2",
        "-i", AUDIO_DEVICE,
        "-vn",
        "-c:a", "aac",
        "-b:a", "128k",
        "-f", "hls",
        "-hls_time", "1",
        "-hls_list_size", "6",
        "-hls_flags", "delete_segments",
        PLAYLIST
    ]

    ffmpeg_process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return {
        "running": True,
        "message": "stream started",
        "playlist": "/stream/live.m3u8"
    }

def stop_stream():
    global ffmpeg_process

    if ffmpeg_process and ffmpeg_process.poll() is None:
        ffmpeg_process.send_signal(signal.SIGTERM)
        ffmpeg_process.wait(timeout=5)
        return {
            "running": False,
            "message": "stream stopped"
        }

    return {
        "running": False,
        "message": "stream was not running"
    }

def stream_status():
    running = ffmpeg_process is not None and ffmpeg_process.poll() is None

    return {
        "running": running,
        "playlist": "/stream/live.m3u8" if running else None
    }
