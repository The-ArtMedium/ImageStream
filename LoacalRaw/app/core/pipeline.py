import numpy as np
import cv2


class Pipeline:
    def __init__(self):
        # White balance
        self.temperature = 0.0   # -50 to +50
        self.tint = 0.0          # -50 to +50

        # Tone controls
        self.exposure = 0.0
        self.contrast = 1.0
        self.sharpen_amount = 0.0

    def apply(self, image):
        """
        Full v1 processing pipeline.
        Order:
        1. White Balance
        2. Exposure
        3. Contrast
        4. Sharpen
        """

        # Convert to float [0-1]
        result = image.astype(np.float32) / 255.0

        # =========================
        # 1. WHITE BALANCE
        # =========================

        # Temperature (approximation)
        temp = self.temperature / 50.0

        # Tint
        tint = self.tint / 50.0

        # Apply temperature shift
        if temp != 0:
            if temp > 0:
                result[..., 2] *= (1 + temp * 0.2)  # Red boost
                result[..., 0] *= (1 - temp * 0.1)  # Blue slight reduce
            else:
                result[..., 0] *= (1 - temp * 0.2)  # Blue boost
                result[..., 2] *= (1 + temp * 0.1)  # Red slight reduce

        # Apply tint shift (green-magenta axis)
        if tint != 0:
            result[..., 1] *= (1 - tint * 0.2)

        # =========================
        # 2. EXPOSURE
        # =========================

        if self.exposure != 0.0:
            result *= (2.0 ** self.exposure)

        # =========================
        # 3. CONTRAST
        # =========================

        if self.contrast != 1.0:
            result = (result - 0.5) * self.contrast + 0.5

        # =========================
        # 4. SHARPEN
        # =========================

        if self.sharpen_amount > 0:
            blurred = cv2.GaussianBlur(result, (0, 0), 3)
            result = cv2.addWeighted(
                result,
                1.0 + self.sharpen_amount,
                blurred,
                -self.sharpen_amount,
                0
            )

        # Clamp safely
        result = np.clip(result, 0, 1)

        return (result * 255).astype(np.uint8)