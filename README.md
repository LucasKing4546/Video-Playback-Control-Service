# Video-Playback-Control-Service
A lightweight HTTP service for controlling video playback on a local machine, built as a prototype for automating Winnow Vision camera testing.

## Setup

```bash
pip install -r requirements.txt
```

Place your test videos in a `videos/` folder next to `app.py`.

## Run

```bash
python app.py
```

Service runs on `http://localhost:5000`.

## API Endpoints

- `POST /play` - Start video playback. Body should include `filename` of the video to play.
- `POST /stop` - Stop the currently playing video.
- `GET /status` - Get the current playback status (idle/playing/error).
- `GET /videos` - List available videos in the `videos/` directory.

## Dependencies

- Python 3.12+
- `mpv` or `vlc` installed on the machine

## Progress

**Phase 1 - Core Service: Complete**

The playback control service is implemented and running. It exposes a simple HTTP API that can be called programmatically to trigger, monitor, and stop video playback.

**Phase 2 - Testing: In Progress**

Unit and integration tests are being written to verify each endpoint and edge case behaviour.

## Design Description

### Main Components

- **`app.py`** - Flask application with route handlers
- **`PlayerState`** - thread-safe class that owns the subprocess and tracks state
- **`_launch_player()`** - detects and launches the best available video player (mpv → vlc → OS fallback)
- **`tests.py`** - **NOT WORKING** test suite using `pytest` to validate API functionality and error handling

### Design Decisions

**Repeated requests:** If `/play` is called while a video is already playing, the current video is stopped and the new one starts immediately. This is the most useful behaviour for automated tests that want to move to the next scenario without manually calling `/stop` first.

**State tracking:** A background thread watches the player process. When the process exits naturally (video ends), state is automatically reset to `idle`. This lets tests poll `/status` to know when a scenario has finished.

**Video selection:** Videos are identified by filename and looked up in a configured `VIDEOS_DIR`.

**Error handling:** If the video file is not found, `/play` returns 404. If the player fails to launch, it returns 500 and the state is set to `error`. `/status` will include the error message so tests can inspect it.

**Test repeatability:** Each `/play` call starts a fresh player process from the beginning of the file. There is no state that persists between test runs, making tests fully repeatable.

### Assumptions and Limitations

- The service controls a player on the same machine it runs on.
- The service does not verify that the camera actually observed the video.
- `mpv` or `vlc` must be installed on the machine.
- No authentication - the service is intended for use on a trusted local test network only.

### What would I add 

## Testing

**Fix the integration tests** so /play, /stop while playing, and /status while playing all work

## Features

**Video duration** in /status - show how far through the video playback is
**Queue support** - line up multiple videos to play back to back