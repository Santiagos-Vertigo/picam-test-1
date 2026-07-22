from datetime import datetime
from pathlib import Path
from time import sleep

from picamera2 import Picamera2


PROJECT_DIR = Path(__file__).resolve().parent
STORAGE_DIR = PROJECT_DIR / "storage" / "images"


def camera_available():
    try:
        return bool(Picamera2.global_camera_info())
    except RuntimeError:
        return False


def capture_images(count=1, delay=2, output_dir=STORAGE_DIR):
    output_dir = Path(output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_DIR / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    captured = []
    camera = Picamera2()
    try:
        camera.configure(camera.create_still_configuration())
        camera.start()
        sleep(2)

        for index in range(count):
            output_path = output_dir / datetime.now().strftime("%Y%m%d-%H%M%S-%f.jpg")
            camera.capture_file(str(output_path))
            captured.append(output_path)

            if index < count - 1:
                sleep(delay)
    finally:
        camera.close()

    return captured
