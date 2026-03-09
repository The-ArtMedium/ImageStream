import numpy as np
import cv2
from PySide6.QtGui import QImage, QPixmap


def numpy_to_qimage(image_array):
    height, width, channel = image_array.shape
    bytes_per_line = channel * width
    return QImage(
        image_array.data,
        width, height,
        bytes_per_line,
        QImage.Format_RGB888
    )

def numpy_to_pixmap(image_array):
    return QPixmap.fromImage(numpy_to_qimage(image_array))

def resize_for_preview(image_array, max_size=800):
    height, width, _ = image_array.shape
    scale = min(max_size / width, max_size / height, 1.0)
    new_width = int(width * scale)
    new_height = int(height * scale)
    return cv2.resize(image_array, (new_width, new_height), interpolation=cv2.INTER_AREA)
