import cv2
import os


class Exporter:
    def __init__(self):
        pass

    def save(self, image, output_path):
        """
        Saves a numpy image (RGB) to disk.
        Supports:
        - .jpg / .jpeg
        - .png
        """

        extension = os.path.splitext(output_path)[1].lower()

        if extension in [".jpg", ".jpeg"]:
            # Convert RGB → BGR for OpenCV
            bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_path, bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        elif extension == ".png":
            bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(output_path, bgr)

        else:
            raise ValueError("Unsupported export format")