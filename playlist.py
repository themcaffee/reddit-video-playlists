import praw
import os
from datetime import date

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
# Secret file for youtube credentials
YT_SECRETS_FILE = "youtube_secrets.json"


def main():
  # Disable OAuthlib's HTTPS verification when running locally.
  # *DO NOT* leave this option enabled in production.
  os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
  youtube_client = create_yt_client()

def create_reddit_playlist("subreddit", date, youtube_client):
  top_videos = get_reddit_top()
  formatted_date = subreddit_day.strftime("%B %d, %Y")
  playlist_id = create_yt_playlist(youtube_client)
  insert_yt_playlist(youtube_client, playlist_id, top_videos)
  print("All done! Here's your playlist:")
  print("https://www.youtube.com/playlist?list=" + playlist_id)


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
    print(yt_id)
    if not yt_id or len(yt_id) != 11:
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
    if "id" in response and response["id"] != "":
      print("Inserted video: " + yt_id)


def create_yt_client():
  # Get credentials and create an API client
  flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
      YT_SECRETS_FILE, scopes)
  credentials = flow.run_console()
  youtube = googleapiclient.discovery.build(
      "youtube", "v3", credentials=credentials)
  return youtube


if __name__ == '__main__':
  main()
