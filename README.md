# Reddit Video Playlists

Create a youtube playlist of a reddit subreddit. Used to create daily playlists
of the top videos of the day in various subreddits. The subreddits are currently
hard-coded so you will need to edit it if you want different ones. This script
is intended to run headless so after the first login, the access token is
stored in `token.pickle`.

### Usage

Create reddit developer service, move praw.ini.bak to praw.ini, and fill out the
client_id and client_secret.

Create youtube developer account and download OAuth credentials in to youtube_secrets.json.

Create virtualenv
```
python3 -m venv venv
source venv/bin/activate
```

Install requirements
```
pip3 install -r requirements.txt
```

Run playlists
```
python3 playlist.py
```
