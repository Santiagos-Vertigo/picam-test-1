import os
import signal

from flask import Flask, Response, abort, jsonify, redirect, render_template, request, send_file, url_for

from camera import (
    SETTINGS_CONTROLS,
    STORAGE_DIR,
    apply_settings,
    camera_available,
    capture_still,
    get_settings,
    preview_frames,
    start_preview,
    stop_preview,
)


VERSION = "0.5"
app = Flask(__name__, static_folder=None)


def latest_image():
    return max(
        STORAGE_DIR.glob("*.jpg"),
        key=lambda path: path.stat().st_mtime_ns,
        default=None,
    )


def project_status():
    latest = latest_image()
    return {
        "camera": "available" if camera_available() else "unavailable",
        "storage": "writable"
        if STORAGE_DIR.is_dir() and os.access(STORAGE_DIR, os.W_OK)
        else "unavailable",
        "latest_image": latest.name if latest else "none",
        "version": VERSION,
    }


def mjpeg_stream():
    for frame in preview_frames():
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame
            + b"\r\n"
        )


def stop_server(_signum, _frame):
    raise KeyboardInterrupt


@app.get("/")
def index():
    status = project_status()
    return render_template(
        "index.html",
        status=status,
        has_latest=status["latest_image"] != "none",
    )


@app.post("/capture")
def capture():
    try:
        capture_still()
    except Exception:
        abort(503)
    return redirect(url_for("index"))


@app.get("/latest")
def latest():
    image = latest_image()
    if image is None:
        abort(404)
    return send_file(image, mimetype="image/jpeg", conditional=True)


@app.get("/status")
def status():
    return jsonify(project_status())


@app.get("/stream")
def stream():
    return Response(
        mjpeg_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/settings")
def settings_get():
    try:
        return jsonify(get_settings())
    except RuntimeError:
        abort(503)


@app.post("/settings")
def settings_post():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    try:
        body = request.get_json(silent=True)
    except Exception:
        return jsonify({"error": "malformed JSON"}), 400

    if body is None:
        return jsonify({"error": "malformed JSON"}), 400

    if not isinstance(body, dict):
        return jsonify({"error": "JSON body must be an object"}), 400

    if not body:
        return jsonify({"error": "no settings provided"}), 400

    unknown = set(body.keys()) - set(SETTINGS_CONTROLS.keys())
    if unknown:
        return jsonify({"error": f"unknown fields: {', '.join(sorted(unknown))}"}), 400

    for key, value in body.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return jsonify({"error": f"{key}: expected a number"}), 400

    try:
        result = apply_settings(body)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError:
        abort(503)

    return jsonify(result)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, stop_server)
    try:
        start_preview()
    except Exception as e:
        print(f"Camera unavailable: {e}")
        raise SystemExit(1)
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    finally:
        stop_preview()
