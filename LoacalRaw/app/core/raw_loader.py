import rawpy
import numpy as np
import os


class RawLoader:
    def __init__(self):
        pass

    def load_image(self, file_path):
        extension = os.path.splitext(file_path)[1].lower()

        if extension in [".cr2", ".nef", ".arw", ".dng"]:
            with rawpy.imread(file_path) as raw:
                rgb = raw.postprocess()
            return rgb
        else:
            from PIL import Image
            image = Image.open(file_path).convert("RGB")
            return np.array(image)
