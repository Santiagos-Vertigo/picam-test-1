import io
from datetime import datetime
from pathlib import Path
from threading import Condition, Lock
from time import sleep

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput


PROJECT_DIR = Path(__file__).resolve().parent
STORAGE_DIR = PROJECT_DIR / "storage" / "images"
PREVIEW_SIZE = (1280, 720)
PREVIEW_FPS = 12

SETTINGS_CONTROLS = {
    "brightness": "Brightness",
    "contrast": "Contrast",
    "saturation": "Saturation",
    "sharpness": "Sharpness",
    "exposure_compensation": "ExposureValue",
}


class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buffer):
        with self.condition:
            self.frame = buffer
            self.condition.notify_all()


_stream_output = StreamingOutput()
_server_camera = None
_settings_lock = Lock()
_current_values = {}


def _capture_file(camera, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / datetime.now().strftime("%Y%m%d-%H%M%S-%f.jpg")
    camera.capture_file(str(output_path), name="main")
    return output_path


def camera_available():
    if _server_camera is not None:
        return True
    try:
        return bool(Picamera2.global_camera_info())
    except RuntimeError:
        return False


def start_preview():
    global _server_camera
    if _server_camera is not None:
        return

    camera = Picamera2()
    try:
        config = camera.create_still_configuration(
            main={"size": camera.sensor_resolution},
            lores={"size": PREVIEW_SIZE, "format": "YUV420"},
            controls={"FrameRate": PREVIEW_FPS},
            buffer_count=3,
        )
        camera.configure(config)
        camera.start_recording(
            MJPEGEncoder(),
            FileOutput(_stream_output),
            name="lores",
        )
    except Exception:
        camera.close()
        raise

    _server_camera = camera

    controls = camera.camera_controls
    for api_name, hw_name in SETTINGS_CONTROLS.items():
        _mn, _mx, default = controls[hw_name]
        _current_values[api_name] = float(default)


def stop_preview():
    global _server_camera

    camera = _server_camera
    _server_camera = None
    if camera is not None:
        _current_values.clear()
        try:
            camera.stop_recording()
        finally:
            camera.close()


def preview_frames():
    while True:
        with _stream_output.condition:
            _stream_output.condition.wait()
            frame = _stream_output.frame
        yield frame


def capture_still():
    if _server_camera is None:
        raise RuntimeError("camera preview is not running")
    return _capture_file(_server_camera, STORAGE_DIR)


def get_settings():
    if _server_camera is None:
        raise RuntimeError("camera preview is not running")

    with _settings_lock:
        controls = _server_camera.camera_controls
        settings = {}
        for api_name, hw_name in SETTINGS_CONTROLS.items():
            mn, mx, default = controls[hw_name]
            settings[api_name] = {
                "value": round(_current_values[api_name], 4),
                "min": round(float(mn), 4),
                "max": round(float(mx), 4),
                "default": round(float(default), 4),
            }
    return settings


def apply_settings(updates):
    if _server_camera is None:
        raise RuntimeError("camera preview is not running")

    with _settings_lock:
        controls = _server_camera.camera_controls
        hw_controls = {}

        for api_name, value in updates.items():
            hw_name = SETTINGS_CONTROLS[api_name]
            mn, mx, _default = controls[hw_name]
            if not isinstance(value, (int, float)):
                raise ValueError(f"{api_name}: expected a number")
            if value < mn or value > mx:
                raise ValueError(f"{api_name}: {value} is outside range [{mn}, {mx}]")
            hw_controls[hw_name] = float(value)

        _server_camera.set_controls(hw_controls)

        for api_name, value in updates.items():
            _current_values[api_name] = float(value)

    return get_settings()


def capture_images(count=1, delay=2, output_dir=STORAGE_DIR):
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_DIR / output_dir

    captured = []
    camera = Picamera2()
    try:
        camera.configure(camera.create_still_configuration())
        camera.start()
        sleep(2)

        for index in range(count):
            captured.append(_capture_file(camera, output_dir))
            if index < count - 1:
                sleep(delay)
    finally:
        camera.close()

    return captured
