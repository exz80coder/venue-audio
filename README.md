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
