import os

from flask import Flask, abort, jsonify, redirect, render_template, send_file, url_for

from camera import STORAGE_DIR, camera_available, capture_images


VERSION = "0.3"
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
    capture_images()
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=False)
