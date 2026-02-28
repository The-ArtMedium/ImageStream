import rawpy
import numpy as np
import os


class RawLoader:
    def __init__(self):
        pass

    def load_image(self, file_path):
        """
        Loads an image.
        Supports:
        - JPG
        - PNG
        - RAW formats (CR2, NEF, ARW, DNG)
        Returns:
        - numpy RGB array
        """

        extension = os.path.splitext(file_path)[1].lower()

        # RAW files
        if extension in [".cr2", ".nef", ".arw", ".dng"]:
            with rawpy.imread(file_path) as raw:
                rgb = raw.postprocess()
            return rgb

        # Standard images
        else:
            # We will expand this later if needed
            from PIL import Image
            image = Image.open(file_path)
            return np.array(image)--