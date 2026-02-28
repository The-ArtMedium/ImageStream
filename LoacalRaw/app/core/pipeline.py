import numpy as np
import cv2


class Pipeline:
    def __init__(self):
        # Default adjustment values
        self.exposure = 0.0
        self.contrast = 1.0
        self.sharpen_amount = 0.0

    def apply(self, image):
        """
        Apply processing pipeline to numpy RGB image.
        Returns processed image.
        """

        result = image.astype(np.float32)

        # Exposure adjustment
        if self.exposure != 0.0:
            result = result * (2.0 ** self.exposure)

        # Contrast adjustment
        if self.contrast != 1.0:
            result = (result - 128) * self.contrast + 128

        # Sharpen (basic unsharp mask)
        if self.sharpen_amount > 0:
            blurred = cv2.GaussianBlur(result, (0, 0), 3)
            result = cv2.addWeighted(
                result,
                1.0 + self.sharpen_amount,
                blurred,
                -self.sharpen_amount,
                0
            )

        # Clip values
        result = np.clip(result, 0, 255)

        return result.astype(np.uint8)--