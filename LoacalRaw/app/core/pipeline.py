import numpy as np
import cv2


class Pipeline:
    """
    LocalRAW v1.2 processing pipeline.
    Professional-grade, fully local, no cloud.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.temperature = 0.0
        self.tint = 0.0
        self.exposure = 0.0
        self.contrast = 0.0
        self.sharpen_amount = 0.0
        self.dehaze = 0.0
        self.nr_luminance = 0.0     # 0 to 1
        self.nr_color = 0.0         # 0 to 1

    def apply(self, image: np.ndarray) -> np.ndarray:
        """
        Full pipeline on RGB uint8 image.
        Order: Noise Reduction → White Balance → Exposure → Contrast → Dehaze → Sharpen
        """
        result = image.astype(np.float32) / 255.0

        # ═══════════════════════════════════════
        # 1. NOISE REDUCTION (first — before other ops amplify noise)
        # ═══════════════════════════════════════
        if self.nr_luminance > 0 or self.nr_color > 0:
            lab = cv2.cvtColor(result, cv2.COLOR_RGB2Lab)

            if self.nr_luminance > 0:
                L = lab[..., 0]
                L_uint8 = np.clip(L / 100.0 * 255, 0, 255).astype(np.uint8)
                h = max(1, int(self.nr_luminance * 8))
                L_denoised = cv2.fastNlMeansDenoising(L_uint8, h=h)
                lab[..., 0] = L_denoised.astype(np.float32) / 255.0 * 100.0

            if self.nr_color > 0:
                sigma = self.nr_color * 3.0
                lab[..., 1] = cv2.GaussianBlur(lab[..., 1], (0, 0), sigma)
                lab[..., 2] = cv2.GaussianBlur(lab[..., 2], (0, 0), sigma)

            result = cv2.cvtColor(lab, cv2.COLOR_Lab2RGB)
            result = np.clip(result, 0, 1)

        # ═══════════════════════════════════════
        # 2. WHITE BALANCE — LAB colorspace shift
        # ═══════════════════════════════════════
        if self.temperature != 0 or self.tint != 0:
            lab = cv2.cvtColor(result.astype(np.float32), cv2.COLOR_RGB2Lab)

            temp_shift = self.temperature / 50.0
            lab[..., 2] += temp_shift * 15.0
            lab[..., 1] += temp_shift * 3.0

            tint_shift = self.tint / 50.0
            lab[..., 1] += tint_shift * 10.0

            result = cv2.cvtColor(lab, cv2.COLOR_Lab2RGB)
            result = np.clip(result, 0, 1)

        # ═══════════════════════════════════════
        # 3. EXPOSURE
        # ═══════════════════════════════════════
        if self.exposure != 0.0:
            result = result * (2.0 ** self.exposure)
            result = np.clip(result, 0, 1)

        # ═══════════════════════════════════════
        # 4. CONTRAST — S-curve on luminance
        # ═══════════════════════════════════════
        if self.contrast != 0.0:
            lab = cv2.cvtColor(result.astype(np.float32), cv2.COLOR_RGB2Lab)
            L = lab[..., 0] / 100.0
            strength = self.contrast / 50.0
            L_curved = L + strength * (L * (1 - L) * (L - 0.5) * 4.0)
            lab[..., 0] = np.clip(L_curved, 0, 1) * 100.0
            result = cv2.cvtColor(lab, cv2.COLOR_Lab2RGB)
            result = np.clip(result, 0, 1)

        # ═══════════════════════════════════════
        # 5. DEHAZE
        # ═══════════════════════════════════════
        if self.dehaze > 0:
            atm = np.percentile(result, 99, axis=(0, 1))
            dark = np.min(result, axis=2)
            dark_blurred = cv2.GaussianBlur(dark, (15, 15), 0)
            t = 1.0 - self.dehaze * (dark_blurred[..., np.newaxis] / (atm + 1e-6))
            t = np.clip(t, 0.2, 1.0)
            result = (result - atm) / t + atm
            result = np.clip(result, 0, 1)

        # ═══════════════════════════════════════
        # 6. SHARPEN — luminance only
        # ═══════════════════════════════════════
        if self.sharpen_amount > 0:
            lab = cv2.cvtColor(result.astype(np.float32), cv2.COLOR_RGB2Lab)
            L = lab[..., 0]
            blurred = cv2.GaussianBlur(L, (0, 0), 2)
            L_sharp = cv2.addWeighted(L, 1.0 + self.sharpen_amount, blurred, -self.sharpen_amount, 0)
            lab[..., 0] = np.clip(L_sharp, 0, 100)
            result = cv2.cvtColor(lab, cv2.COLOR_Lab2RGB)
            result = np.clip(result, 0, 1)

        return (result * 255).astype(np.uint8)
