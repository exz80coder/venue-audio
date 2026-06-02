import subprocess
import re

AUDIO_DEVICE = "plughw:0,0"

def get_audio_level():
    cmd = [
        "ffmpeg",
        "-f", "alsa",
        "-ar", "48000",
        "-ac", "2",
        "-i", AUDIO_DEVICE,
        "-t", "3",
        "-af", "volumedetect",
        "-f", "null",
        "-"
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    output = result.stderr

    mean_match = re.search(r"mean_volume:\s*(-?\d+\.?\d*) dB", output)
    max_match = re.search(r"max_volume:\s*(-?\d+\.?\d*) dB", output)

    mean_volume = float(mean_match.group(1)) if mean_match else None
    max_volume = float(max_match.group(1)) if max_match else None

    audio_detected = max_volume is not None and max_volume > -50

    return {
        "device": AUDIO_DEVICE,
        "mean_volume_db": mean_volume,
        "max_volume_db": max_volume,
        "audio_detected": audio_detected
    }
