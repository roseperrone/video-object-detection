'''
This code is adapted from ozansener's WebCrawler, found here:
https://raw.githubusercontent.com/ozansener/RecipeWatch/ \
                    master/WebCrawler/Crawler/Crawler.py
'''
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

DEVELOPER_KEY = 'AIzaSyBDgwtalxdPqZnNOHpoaV6wV50AW75-mUk'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def search_youtube(query, max_num_video_ids=3):
  '''
  max_results:
    This number of results includes playlists and channels, not just video_ids
  '''
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                  developerKey=DEVELOPER_KEY)

  # Return five times as mayn results as we need, because we'll exclude
  # channels and playlists. This gives a large safety margin to return
  # enough video_ids
  search_response = youtube.search().list(
    q=query,
    part="id,snippet",
    maxResults=5*max_num_video_ids,
    type='video'
  ).execute()

  video_ids = []
  for search_result in search_response.get('items', []):
    # See Ozan's code to get search results that are channels or playlists
    if search_result['id']['kind'] == 'youtube#video' \
      and len(video_ids) < max_num_video_ids:
      video_ids.append(search_result['id']['videoId'])

  if len(video_ids) < max_num_video_ids:
    print 'WARNING: fewer than ' + str(max_num_video_ids) + \
      ' video ids were found. Increase maxResults in the youtube.search().'

  return video_ids
