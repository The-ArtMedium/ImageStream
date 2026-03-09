import cv2
import numpy as np


class Adjustments:
    """
    Stores all editable parameters for LocalRAW.
    This keeps UI separated from processing logic.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.exposure = 0.0       # in stops (-3 to +3)
        self.contrast = 1.0       # 1.0 = neutral
        self.sharpen = 0.0        # 0 to 2
        self.dehaze = 0.0         # placeholder
        self.temperature = 0      # placeholder
        self.tint = 0             # placeholder

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        Apply all adjustments to image.
        Image expected in BGR uint8 format.
        """

        result = image.astype(np.float32) / 255.0

        # ---- Exposure (stops) ----
        if self.exposure != 0:
            result = result * (2 ** self.exposure)

        # ---- Contrast ----
        if self.contrast != 1.0:
            result = (result - 0.5) * self.contrast + 0.5

        # ---- Sharpen (Unsharp Mask) ----
        if self.sharpen > 0:
            blurred = cv2.GaussianBlur(result, (0, 0), 3)
            result = cv2.addWeighted(result, 1 + self.sharpen, blurred, -self.sharpen, 0)

        # Clamp values
        result = np.clip(result, 0, 1)

        return (result * 255).astype(np.uint8)