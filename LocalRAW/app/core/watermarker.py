import numpy as np
import cv2


class Watermarker:
    """
    Adds text or image watermark to a numpy RGB image.

    Position options: 
        'bottom_right', 'bottom_left', 
        'top_right',    'top_left', 
        'center'
    """

    POSITIONS = [
        "bottom_right", "bottom_left",
        "top_right",    "top_left",
        "center"
    ]

    def apply_text(
        self,
        image: np.ndarray,
        text: str,
        position: str = "bottom_right",
        opacity: float = 0.6,
        font_scale: float = 1.0,
        color: tuple = (255, 255, 255),
        margin: int = 30
    ) -> np.ndarray:
        """
        Burns a text watermark onto the image.
        Returns a new RGB uint8 array.
        """
        result = image.copy()
        h, w = result.shape[:2]

        font = cv2.FONT_HERSHEY_DUPLEX
        thickness = max(1, int(font_scale * 1.5))

        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        # Calculate position
        x, y = self._get_xy(position, w, h, text_w, text_h, margin)

        # Draw shadow for readability on any background
        shadow_color = (0, 0, 0)
        cv2.putText(result, text, (x + 2, y + 2), font, font_scale, shadow_color, thickness + 1, cv2.LINE_AA)

        # Blend text onto image using opacity
        overlay = result.copy()
        cv2.putText(overlay, text, (x, y), font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.addWeighted(overlay, opacity, result, 1 - opacity, 0, result)

        return result

    def apply_image(
        self,
        image: np.ndarray,
        watermark_path: str,
        position: str = "bottom_right",
        opacity: float = 0.5,
        scale: float = 0.15,
        margin: int = 30
    ) -> np.ndarray:
        """
        Burns a PNG image watermark (logo) onto the image.
        Supports transparency (PNG with alpha channel).
        """
        result = image.copy()
        h, w = result.shape[:2]

        wm = cv2.imread(watermark_path, cv2.IMREAD_UNCHANGED)
        if wm is None:
            raise FileNotFoundError(f"Watermark image not found: {watermark_path}")

        # Resize watermark proportionally
        wm_h = int(h * scale)
        wm_w = int(wm.shape[1] * (wm_h / wm.shape[0]))
        wm = cv2.resize(wm, (wm_w, wm_h), interpolation=cv2.INTER_AREA)

        x, y = self._get_xy(position, w, h, wm_w, wm_h, margin)

        # Clamp to image bounds
        x = max(0, min(x, w - wm_w))
        y = max(0, min(y, h - wm_h))

        roi = result[y:y + wm_h, x:x + wm_w]

        if wm.shape[2] == 4:
            # Has alpha channel
            alpha = (wm[..., 3] / 255.0 * opacity)[..., np.newaxis]
            wm_rgb = cv2.cvtColor(wm, cv2.COLOR_BGRA2RGB)
            blended = (wm_rgb * alpha + roi * (1 - alpha)).astype(np.uint8)
        else:
            wm_rgb = cv2.cvtColor(wm, cv2.COLOR_BGR2RGB)
            blended = cv2.addWeighted(wm_rgb, opacity, roi, 1 - opacity, 0)

        result[y:y + wm_h, x:x + wm_w] = blended
        return result

    def _get_xy(self, position, w, h, obj_w, obj_h, margin):
        if position == "bottom_right":
            return w - obj_w - margin, h - margin
        elif position == "bottom_left":
            return margin, h - margin
        elif position == "top_right":
            return w - obj_w - margin, obj_h + margin
        elif position == "top_left":
            return margin, obj_h + margin
        elif position == "center":
            return (w - obj_w) // 2, (h + obj_h) // 2
        return w - obj_w - margin, h - margin
