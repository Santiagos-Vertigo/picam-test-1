# picam-test-1

A minimal Raspberry Pi camera tool with command-line capture and a browser remote with live focus preview.

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

The dark monitor page shows camera and storage status, a responsive 1280x720 live preview at approximately 12 FPS, and one Capture button. Captured full-resolution JPEGs are saved under `storage/images` but are not displayed on the home page. The interface has no authentication and is intended only for a trusted local network.

### Adjust focus

1. Start the server and open the browser URL.
2. Keep the full preview frame visible while resizing or positioning the browser.
3. Turn the physical lens focus ring slowly until the subject is sharp.
4. Press Capture to save a full-resolution JPEG under `storage/images`.
5. Stop the server with Ctrl+C when finished.

Routes:

- `GET /` - browser remote
- `POST /capture` - capture one full-resolution image
- `GET /latest` - newest full-resolution JPEG
- `GET /status` - JSON status
- `GET /stream` - 1280x720 MJPEG focus preview

Example endpoint requests:

```bash
curl http://192.168.1.97:5000/status
curl -X POST http://192.168.1.97:5000/capture
curl http://192.168.1.97:5000/latest --output latest.jpg
```

## Scope

Version 0.4 provides still-image capture and live MJPEG focus preview. It does not include video recording, timelapse, cloud upload, AI, authentication, or a database.
