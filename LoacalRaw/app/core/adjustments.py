--class Adjustments:
    """
    Stores all editable parameters for LocalRAW.
    This keeps UI separated from processing logic.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.exposure = 0.0
        self.contrast = 1.0
        self.sharpen = 0.0
        self.dehaze = 0.0
        self.temperature = 0
        self.tint = 0