import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ScreenshotCapture:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture(self) -> Path | None:
        try:
            import mss

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            path = self.output_dir / f"screenshot_{timestamp}.png"

            with mss.mss() as sct:
                monitor = sct.monitors[1]
                sct.shot(mon=monitor, output=str(path))

            logger.debug("Screenshot saved: %s", path)
            return path
        except Exception as e:
            logger.error("Screenshot capture failed: %s", e)
            return None
