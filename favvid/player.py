import sys
from pathlib import Path
import vlc


class VLCPlayer:
    def __init__(self, video_widget):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        # attach native window handle
        if sys.platform.startswith('win'):
            self.player.set_hwnd(video_widget.winId())
        else:
            self.player.set_xwindow(video_widget.winId())

    def play(self, path: Path):
        media = self.instance.media_new(str(path))
        self.player.set_media(media)
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def is_playing(self):
        return bool(self.player.is_playing())

    def set_rate(self, rate: float):
        try:
            self.player.set_rate(rate)
        except Exception:
            pass

    def set_position(self, pos: float):
        self.player.set_position(pos)

    def get_position(self):
        return float(self.player.get_position() or 0.0)

    def set_volume(self, vol: int):
        self.player.audio_set_volume(vol)
