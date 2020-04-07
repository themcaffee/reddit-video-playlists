import praw
import os
import os.path
from datetime import date

import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
# Secret file for youtube credentials
YT_SECRETS_FILE = "youtube_secrets.json"
SUBREDDITS = ["videos", "dankvideos", "mealtimevideos", "documentaries"]
TOKEN_FILE = 'token.pickle'


def main():
  # Disable OAuthlib's HTTPS verification when running locally.
  # *DO NOT* leave this option enabled in production.
  os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
  youtube_client = get_service()
  for subreddit in SUBREDDITS:
    create_reddit_playlist(subreddit, youtube_client)
    print("All done! Here's your playlist for /r/" + subreddit + ":")
    print("https://www.youtube.com/playlist?list=" + playlist_id)

def create_reddit_playlist(subreddit, youtube_client):
  top_videos = get_reddit_top(subreddit)
  today = date.today()
  formatted_date = today.strftime("%B %d, %Y")
  playlist_id = create_yt_playlist(youtube_client, formatted_date, subreddit)
  insert_yt_playlist(youtube_client, playlist_id, top_videos)
  return playlist_id


def get_reddit_top(subreddit):
  reddit = praw.Reddit('bot1', user_agent='Reddit Youtube Playlist Bot')
  top_videos = reddit.subreddit(subreddit).top(time_filter='day', limit=100)
  return top_videos


def create_yt_playlist(youtube, formatted_date, subreddit):
  playlist_title = "Reddit Top /r/" + subreddit + " " + formatted_date
  request = youtube.playlists().insert(
    part="snippet,status",
    body={
      "snippet": {
        "title": playlist_title,
        "description": "The top videos on /r/" + subreddit + " on " + formatted_date,
        "tags": [
          "API call"
        ],
        "defaultLanguage": "en"
      },
      "status": {
        "privacyStatus": "public"
      }
    }
  )
  response = request.execute()
  print("Created Youtube Playlist: " + playlist_title)
  return response["id"]


def get_yt_id(video):
  try:
    if "youtube.com" in video.url:
      return video.url.split("?v=")[1]
    elif "youtu.be" in video.url:
      return video.url.split(".be/")[1]
    else:
      return False
  except:
    print("There was an error parsing youtube urls for:")
    print(video.url)
    return False

def insert_yt_playlist(youtube, playlist_id, videos):
  for index, video in enumerate(videos):
    yt_id = get_yt_id(video)
    if not yt_id or len(yt_id) != 11:
      print(yt_id)
      continue
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
          "snippet": {
            "playlistId": playlist_id,
            "position": index,
            "resourceId": {
              "kind": "youtube#video",
              "videoId": yt_id
            }
          }
        }
    )
    response = request.execute()
    if "id" not in response or response["id"] == "":
      print("There was an error inserting: " + yt_id)


def create_yt_client():
  # Get credentials and create an API client
  flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
      YT_SECRETS_FILE, scopes)
  # Generate URL for request to Google's OAuth 2.0 server.
  # Use kwargs to set optional request parameters.
  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')
  print(authorization_url)
  credentials = input("Enter the auth token: ")
  youtube = googleapiclient.discovery.build(
      "youtube", "v3", credentials=credentials)
  return youtube


def get_service():
  creds = None
  if os.path.exists(TOKEN_FILE):
      with open(TOKEN_FILE, 'rb') as token:
          creds = pickle.load(token)
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              YT_SECRETS_FILE, SCOPES)
          creds = flow.run_local_server()
      with open(TOKEN_FILE, 'wb') as token:
          pickle.dump(creds, token)
  return build("youtube", "v3", credentials=creds)


if __name__ == '__main__':
  main()
