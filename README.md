# YouTube Channel to Playlist

Keeping track of which YouTube videos you have watched can be tricky,
especially because the "WATCHED" indicator seems to be ephemeral. This script
allows you to add all videos from a YouTube channel to a playlist that you
control so you can order them as you please and remove them once they've been
watched.

# Installation

1. Install the Google API client library:

  ```bash
  pip install google-api-python-client
  ```

2. Create a project through the [Google Developers Console](https://console.developers.google.com/project).
3. Create an OAuth Client ID for a native application through the APIs & Auth /
   Credentials section of your project.
4. Download the OAuth client secrets JSON file from the Credentials page and
   rename it to `client_secrets.json`. Place this file in the same folder as
   `channel_to_playlist.py`.

# Usage

```bash
./channel_to_playlist.py source-channel-id target-playlist-id
```

where `source-channel-id` and `target-playlist-id` can be found from the URLs of
the YouTube channel and playlist.

For example, to copy videos from the [PyCon 2015 Channel](https://www.youtube.com/channel/UCgxzjK6GuOHVKR_08TT4hJQ)
to [this playlist](https://www.youtube.com/playlist?list=PLlgnub_DBR_CszAWpJypwst0OFDxW6jOJ)
you would run:

```bash
./channel_to_playlist.py UCgxzjK6GuOHVKR_08TT4hJQ PLlgnub_DBR_CszAWpJypwst0OFDxW6jOJ
```

The script will store the video IDs that are added to the playlist in a file
and skip these videos if it is run again. This allows you to re-run the script
when new videos are uploaded to the channel.
