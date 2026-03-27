from kivy.uix.videoplayer import VideoPlayer

class EditorScreen(Screen):
    video_path = ""
    
    def on_enter(self):
        # This triggers when you switch to this screen
        self.layout.clear_widgets() # Clean the node
        
        # 1. The Video Player (The Eyes of the Utility)
        self.player = VideoPlayer(source=self.video_path, state='play', options={'allow_stretch': True})
        self.player.size_hint = (1, 0.5)
        self.player.pos_hint = {'center_x': 0.5, 'top': 1}
        self.layout.add_widget(self.player)

        # 2. Re-add the Buttons (The Hands of the Utility)
        # [Use the button code from the previous block here...]
        self.add_widget(self.layout)

    def set_start(self, instance):
        self.start_time = self.player.position # Grabs real-time data
        self.btn_start.text = f"START: {round(self.start_time, 2)}s"

    def set_end(self, instance):
        self.end_time = self.player.position # Grabs real-time data
        self.btn_end.text = f"END: {round(self.end_time, 2)}s"
