# Venue Audio

Venue Audio is a low-latency audio streaming platform for hospitality venues.

## Current Status

### Hardware
- Raspberry Pi 5
- StarTech 7.1 USB Audio
- HDMI Audio Extractor

### Audio Path
Windows PC
-> HDMI
-> Audio Extractor
-> 3.5mm Line Out
-> StarTech Line In
-> Raspberry Pi

### Important Mixer Setting

PCM Capture Source = Line

### Edge Agent

Health endpoint:

http://<pi-ip>:3000/health

### Sprint 1 Complete

- Audio capture verified
- Audio playback verified
- GitHub configured
- Python edge agent created
# Venue Audio

## Current Status

### Hardware

* Raspberry Pi 5
* StarTech 7.1 USB Audio
* HDMI Audio Extractor

### Audio Path

Windows PC
→ HDMI
→ Audio Extractor
→ 3.5mm Line Out
→ StarTech Line In (Blue)
→ Raspberry Pi

### Critical Audio Setting

```bash
alsamixer
```

Select:

```text
PCM Capture Source = Line
```

### Working Audio Capture Test

```bash
./scripts/audio-test.sh
```

### MediaMTX

Installed in:

```text
/home/gfurse/mediamtx
```

Start:

```bash
cd ~/mediamtx
./mediamtx
```

### Publish Audio

```bash
ffmpeg \
-f alsa \
-ar 48000 \
-ac 2 \
-i plughw:0,0 \
-vn \
-c:a libopus \
-b:a 64k \
-f rtsp \
-rtsp_transport tcp \
rtsp://127.0.0.1:8554/venueaudio
```

### Browser Playback

```text
http://<pi-ip>:8889/venueaudio
```

### Current Result

* Phone playback working
* Raspberry Pi playback working
* WebRTC latency acceptable
* HLS latency unacceptable

```
```
