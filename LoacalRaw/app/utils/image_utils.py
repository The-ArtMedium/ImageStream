import numpy as np
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt


def numpy_to_qimage(image_array):
    """
    Convert a numpy RGB image (uint8) to QImage.
    """

    height, width, channel = image_array.shape

    bytes_per_line = channel * width

    return QImage(
        image_array.data,
        width,
        height,
        bytes_per_line,
        QImage.Format_RGB888
    )


def numpy_to_pixmap(image_array):
    """
    Convert numpy RGB image to QPixmap.
    """

    qimage = numpy_to_qimage(image_array)
    return QPixmap.fromImage(qimage)


def resize_for_preview(image_array, max_size=800):
    """
    Resize image proportionally for preview display.
    """

    height, width, _ = image_array.shape

    scale = min(max_size / width, max_size / height, 1.0)

    new_width = int(width * scale)
    new_height = int(height * scale)

    import cv2
    resized = cv2.resize(image_array, (new_width, new_height), interpolation=cv2.INTER_AREA)

    return resized