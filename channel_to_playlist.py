#!/usr/bin/env python3
"""
Add videos from a YouTube channel to a playlist.

Usage:

  channel_to_playlist.py source-channel-id target-playlist-id

"""
import os
import sys
import warnings
from argparse import ArgumentParser
from http import HTTPStatus

import dateutil.parser
import httplib2
from apiclient.discovery import build
from apiclient.errors import HttpError
from dateutil import tz
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow


def _parse_date(string):
    dt = dateutil.parser.parse(string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.UTC)
    return dt


def get_authenticated_service(args):
    flow = flow_from_clientsecrets(
        filename=args.secrets,
        message=(
            "Missing client_secrets.json file.\nDownload from "
            "https://console.developers.google.com"
            "/project/YOUR_PROJECT_ID/apiui/credential."
        ),
        scope="https://www.googleapis.com/auth/youtube",
    )
    storage = Storage(".channel_to_playlist-oauth2-credentials.json")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)
    return build("youtube", "v3", http=credentials.authorize(httplib2.Http()))


def get_channel_upload_playlist_id(youtube, channel_id):
    channel_response = youtube.channels().list(id=channel_id, part="contentDetails").execute()
    return channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_playlist_video_ids(
    youtube, playlist_id, *, published_after=None, published_before=None, http=None
):
    request = youtube.playlistItems().list(playlistId=playlist_id, part="snippet", maxResults=50)
    items = []
    while request:
        response = request.execute(http=http)
        items += response["items"]
        request = youtube.playlistItems().list_next(request, response)
    if published_after is not None:
        items = [
            item
            for item in items
            if _parse_date(item["snippet"]["publishedAt"]) >= published_after
        ]
    if published_before is not None:
        items = [
            item
            for item in items
            if _parse_date(item["snippet"]["publishedAt"]) < published_before
        ]
    items.sort(key=lambda item: _parse_date(item["snippet"]["publishedAt"]))
    return [item["snippet"]["resourceId"]["videoId"] for item in items]


def add_video_to_playlist(youtube, playlist_id, video_id):
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"videoId": video_id, "kind": "youtube#video"},
                }
            },
        ).execute()
    except HttpError as exc:
        if exc.resp.status == HTTPStatus.CONFLICT:
            # watch-later playlist don't allow duplicates
            raise VideoAlreadyInPlaylistError()
        raise


def add_to_playlist(youtube, playlist_id, video_ids, added_videos_file, add_duplicates):
    existing_videos = get_playlist_video_ids(youtube, playlist_id)
    count = len(video_ids)
    for video_num, video_id in enumerate(video_ids, start=1):
        if video_id in existing_videos and not add_duplicates:
            continue
        sys.stdout.write("\rAdding video {} of {}".format(video_num, count))
        sys.stdout.flush()
        try:
            add_video_to_playlist(youtube, playlist_id, video_id)
        except VideoAlreadyInPlaylistError:
            if add_duplicates:
                warnings.warn(f"video {video_id} cannot be added as it is already in the playlist")
        if added_videos_file:
            added_videos_file.write(video_id + "\n")
        existing_videos.append(video_id)
    if count:
        sys.stdout.write("\n")


def _parse_args(args):
    argparser = ArgumentParser(description="Add videos from a YouTube channel to a playlist")
    argparser.add_argument(
        "--secrets", default="client_secrets.json", help="Google API OAuth secrets file"
    )
    argparser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Add videos even if they are already in the playlist",
    )
    argparser.add_argument(
        "--after",
        type=_parse_date,
        dest="published_after",
        help="Only add videos published after this date",
    )
    argparser.add_argument(
        "--before",
        type=_parse_date,
        dest="published_before",
        help="Only add videos published before this date",
    )
    argparser.add_argument("channel_id", help="id of channel to copy videos from")
    argparser.add_argument("playlist_id", help="id of playlist to add videos to")
    parsed = argparser.parse_args(args)
    return parsed


def main():
    args = _parse_args(sys.argv[1:])

    youtube = get_authenticated_service(args)
    channel_playlist_id = get_channel_upload_playlist_id(youtube, args.channel_id)
    video_ids = get_playlist_video_ids(
        youtube,
        channel_playlist_id,
        published_after=args.published_after,
        published_before=args.published_before,
    )
    added_videos_filename = "playlist-{}-added-videos".format(args.playlist_id)

    if os.path.exists(added_videos_filename):
        with open(added_videos_filename) as f:
            added_video_ids = set(map(str.strip, f.readlines()))
        video_ids = [vid_id for vid_id in video_ids if vid_id not in added_video_ids]

    with open(added_videos_filename, "a") as f:
        add_to_playlist(youtube, args.playlist_id, video_ids, f, args.allow_duplicates)


class VideoAlreadyInPlaylistError(Exception):
    """ video already in playlist """


if __name__ == "__main__":
    main()
