import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

BASE_URL = "http://localhost:5001"
VIDEOS_DIR = Path("videos")
TEST_VIDEO = VIDEOS_DIR / "test_chips.mp4"


@pytest.fixture(scope="session", autouse=True)
def test_video():
    """Create a dummy video file before tests, delete it after."""
    VIDEOS_DIR.mkdir(exist_ok=True)
    TEST_VIDEO.write_bytes(b"fake video content")
    yield
    TEST_VIDEO.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def server():
    """Start the real Flask server, shut it down after all tests."""
    env = os.environ.copy()
    env["PORT"] = "5001"

    process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        #stdout=subprocess.DEVNULL,
        #stderr=subprocess.DEVNULL,
    )

    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/status", timeout=1)
            break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        process.terminate()
        TEST_VIDEO.unlink(missing_ok=True)
        raise RuntimeError("Server did not start in time")

    yield process

    process.terminate()
    process.wait()


@pytest.fixture(autouse=True)
def stop_after_each(server):
    """Stop any playing video after each test to reset state."""
    yield
    requests.post(f"{BASE_URL}/stop")


def test_status_idle(server):
    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    assert response.json()["state"] == "idle"


def test_play_missing_field(server):
    response = requests.post(f"{BASE_URL}/play", json={})
    assert response.status_code == 400


def test_play_video_not_found(server):
    response = requests.post(f"{BASE_URL}/play", json={"video": "ghost.mp4"})
    assert response.status_code == 404


def test_stop_when_idle(server):
    response = requests.post(f"{BASE_URL}/stop")
    assert response.status_code == 409


def test_list_videos(server):
    response = requests.get(f"{BASE_URL}/videos")
    assert response.status_code == 200
    assert TEST_VIDEO.name in response.json()["videos"]
