import os
import subprocess
import threading
from enum import Enum
from pathlib import Path

from flask import Flask, jsonify, request

app = Flask("VideoPlaybackApp")

# Directory where test videos are stored
VIDEOS_DIR = Path(os.environ.get("VIDEOS_DIR", "./videos"))

class PlaybackState(str, Enum):
    IDLE = "idle"
    PLAYING = "playing"
    ERROR = "error"

class PlayerState:
    def __init__(self, state: PlaybackState = PlaybackState.IDLE):
        self.state = state
        self.current_video = None
        self.error_message = None
        self.process = None
        self.lock = threading.Lock()

    def _playback_finished(self):
        """
        Called in the background when the playback is finished.
        """
        with self.lock:
           if self.state == PlaybackState.PLAYING:
                self.state = PlaybackState.IDLE
                self.current_video = None
                self.error_message = None
                self.process = None

    def play(self, video_path: Path):
        """
        Play the given video path.
        """
        with self.lock:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait()

            try:
                self.process = _launch_video(video_path)
            except Exception as e:
                self.state = PlaybackState.ERROR
                self.error_message = str(e)
                self.current_video = None
                return False, str(e)

            self.state = PlaybackState.PLAYING
            self.current_video = video_path.name
            self.error_message = None

        # Watch the process in a background thread so we can auto-reset state
        threading.Thread(target=self._watch, daemon=True).start()
        return True, f"Playing {video_path.name}"

    def _watch(self):
        """
        Wait for the process to finish before updating state.
        """
        if self.process:
            self.process.wait()
        self._playback_finished()

    def stop(self):
        with self.lock:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait()
                self.process = None
                self.state = PlaybackState.IDLE
                self.current_video = None
                return True, "Playback stopped"
            return False, "No video is currently playing"

    def get_status(self):
        with self.lock:
            return {
                "state": self.state,
                "current_video": self.current_video,
                "error": self.error_message
            }

player = PlayerState()

def _launch_video(video_path: Path):
    """
    Launch a video process.
    Tries mvp, then vlc
    Raises RuntimeError if no player is found
    """
    candidates = [
        ["mpv", "--no-terminal", str(video_path)],
        ["vlc", "--play-and-exit", str(video_path)]
    ]
    for candidate in candidates:
        command = candidate[0]
        if _command_exists(command):
            return subprocess.Popen(
                candidate,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
    raise RuntimeError("No supported video player found (try installing mpv or vlc)")


def _command_exists(command : str):
    import shutil
    return shutil.which(command) is not None
