# picam-test-1

A minimal Raspberry Pi camera tool with a command-line capture utility and a four-route browser remote.

## Requirements

- Raspberry Pi with a camera supported by `rpicam`
- Python 3
- Raspberry Pi OS Picamera2 package

The virtual environment uses system site packages because Raspberry Pi OS provides Picamera2 and its native camera dependencies.

## Installation

```bash
cd /home/diego/picam-test-1
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Command-line capture

Capture one image:

```bash
.venv/bin/python capture.py
```

Capture three images with one second between captures:

```bash
.venv/bin/python capture.py --count 3 --delay 1
```

Use a different output directory:

```bash
.venv/bin/python capture.py --output storage/test-images
```

## Browser remote

Start the server:

```bash
cd /home/diego/picam-test-1
.venv/bin/python app.py
```

Open this URL from another device on the same network:

```text
http://192.168.1.97:5000
```

The page shows camera and storage status, a Capture button, and the latest image. It has no authentication and is intended only for a trusted local network.

Routes:

- `GET /` - browser remote
- `POST /capture` - capture one image and redirect to the home page
- `GET /latest` - newest JPEG
- `GET /status` - JSON status

Example endpoint requests:

```bash
curl http://192.168.1.97:5000/status
curl -X POST http://192.168.1.97:5000/capture
curl http://192.168.1.97:5000/latest --output latest.jpg
```

## Scope

Version 0.3 provides still-image capture through the CLI and browser remote. It does not include video, timelapse, streaming, cloud upload, or AI features.
