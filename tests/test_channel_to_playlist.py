from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from apiclient.discovery import build
from apiclient.http import HttpMock
from dateutil import tz

import channel_to_playlist


FIXTURES = Path(__file__).parent / "fixtures"
VIDEO_IDS = ["M1-eVW6Tboc", "ZBpSxpvZoW0", "wuzCwOO7QDs"]
PLAYLIST_ID = "PLlgnub_DBR_CJFqRj-Gcx4_nmybHAntki"


@pytest.fixture
def service():
    http = HttpMock(FIXTURES / "discovery.json")
    yield build("youtube", "v3", http=http, developerKey="")


def test_parse_args():
    args = channel_to_playlist._parse_args(
        [
            "--secrets",
            "secrets-1",
            "--allow-duplicates",
            "--after",
            "2018-01-02",
            "--before",
            "2019-01-02",
            "channel-id-1",
            "playlist-id-1",
        ]
    )
    assert args.secrets == "secrets-1"
    assert args.allow_duplicates is True
    assert args.published_after == datetime(2018, 1, 2, tzinfo=tz.UTC)
    assert args.published_before == datetime(2019, 1, 2, tzinfo=tz.UTC)
    assert args.channel_id == "channel-id-1"
    assert args.playlist_id == "playlist-id-1"


def test_parse_args_defaults():
    args = channel_to_playlist._parse_args(["channel-id-1", "playlist-id-1"])
    assert args.secrets == "client_secrets.json"
    assert args.allow_duplicates is False
    assert args.published_after is None
    assert args.published_before is None


def test_parse_args_handles_timezones():
    args = channel_to_playlist._parse_args(
        [
            "--after",
            "2018-01-02T03:04:05+10:00",
            "--before",
            "2019-01-02T03:04:05+10:00",
            "channel-id-1",
            "playlist-id-1",
        ]
    )
    tzinfo = timezone(timedelta(hours=10))
    assert args.published_after == datetime(2018, 1, 2, 3, 4, 5, tzinfo=tzinfo)
    assert args.published_before == datetime(2019, 1, 2, 3, 4, 5, tzinfo=tzinfo)


def test_get_playlist_video_ids(service):
    http = HttpMock(FIXTURES / "playlist.json")
    video_ids = channel_to_playlist.get_playlist_video_ids(service, PLAYLIST_ID, http=http)
    assert video_ids == VIDEO_IDS


def test_get_playlist_video_ids_with_published_after(service):
    http = HttpMock(FIXTURES / "playlist.json")
    dt = datetime(2018, 11, 4, 4, 25, 44, tzinfo=tz.UTC)
    video_ids = channel_to_playlist.get_playlist_video_ids(
        service, PLAYLIST_ID, published_after=dt, http=http
    )
    assert video_ids == VIDEO_IDS[1:]


def test_get_playlist_video_ids_with_published_before(service):
    http = HttpMock(FIXTURES / "playlist.json")
    dt = datetime(2018, 11, 4, 4, 27, 10, tzinfo=tz.UTC)
    video_ids = channel_to_playlist.get_playlist_video_ids(
        service, PLAYLIST_ID, published_before=dt, http=http
    )
    assert video_ids == VIDEO_IDS[:-1]
