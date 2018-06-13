#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Add videos from a YouTube channel to a playlist.

Usage:

  channel_to_playlist.py source-channel-id target-playlist-id

"""

import os
import sys

from apiclient.errors import HttpError
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import httplib2


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
    channel_response = (
        youtube.channels().list(id=channel_id, part="contentDetails").execute()
    )
    return channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_playlist_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        playlistId=playlist_id, part="snippet", maxResults=50
    )
    items = []
    while request:
        response = request.execute()
        items += response["items"]
        request = youtube.playlistItems().list_next(request, response)
    items.sort(key=lambda item: item["snippet"]["publishedAt"])
    return [item["snippet"]["resourceId"]["videoId"] for item in items]


def add_video_to_playlist(youtube, playlist_id, video_id, skip_if_already_exists):
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
        return True
    except HttpError as ex:
        if ex.resp.status == 409 and skip_if_already_exists:
            return False
        raise
        


def add_to_playlist(youtube, playlist_id, video_ids, added_videos_file, skip_if_already_exists):
    count = len(video_ids)
    for video_num, video_id in enumerate(video_ids, start=1):
        sys.stdout.write("\rAdding video {} of {}".format(video_num, count))
        sys.stdout.flush()
        success = add_video_to_playlist(youtube, playlist_id, video_id, skip_if_already_exists)
        if added_videos_file and success:
            added_videos_file.write(video_id + "\n")
    if count:
        sys.stdout.write("\n")


def main():
    argparser.add_argument(
        "--secrets", default="client_secrets.json", help="Google API OAuth secrets file"
    )
    argparser.add_argument(
        "--skip_existing", required=False, default=False, type=bool, help="Skip videos, which already exist in playlist"
    )
    argparser.add_argument("channel_id", help="id of channel to copy videos from")
    argparser.add_argument("playlist_id", help="id of playlist to add videos to")
    args = argparser.parse_args()

    youtube = get_authenticated_service(args)
    channel_playlist_id = get_channel_upload_playlist_id(youtube, args.channel_id)
    video_ids = get_playlist_video_ids(youtube, channel_playlist_id)
    added_videos_filename = "playlist-{}-added-videos".format(args.playlist_id)

    if os.path.exists(added_videos_filename):
        with open(added_videos_filename) as f:
            added_video_ids = set(map(str.strip, f.readlines()))
        video_ids = [vid_id for vid_id in video_ids if vid_id not in added_video_ids]

    with open(added_videos_filename, "a") as f:
        add_to_playlist(youtube, args.playlist_id, video_ids, f, args.skip_existing)


if __name__ == "__main__":
    main()
