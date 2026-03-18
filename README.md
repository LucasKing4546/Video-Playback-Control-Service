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
- `POST /play`: Start video playback. Body should include `filename` of the video to play.
- `POST /stop`: Stop the currently playing video.
- `GET /status`: Get the current playback status (playing/stopped).
- `POST /videos`: List available videos in the `videos/` directory.


## Dependencies
 
- Python 3.11+
- `mpv` or `vlc` installed on the machine
 

## Progress
 
**Phase 1 — Core Service: Complete**
 
The playback control service is implemented and running. It exposes a simple HTTP API that can be called programmatically to trigger, monitor, and stop video playback.
 
**Phase 2 — Testing: In Progress**
 
Unit and integration tests are being written to verify each endpoint and edge case behaviour.


