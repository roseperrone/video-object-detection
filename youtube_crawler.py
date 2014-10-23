'''
This code is adapted from ozansener's WebCrawler, found here:
https://raw.githubusercontent.com/ozansener/RecipeWatch/master/WebCrawler/Crawler/Crawler.py
'''

class Crawler:
    def __init__(self):
        self.query=''
    def __init__(self,q):
        self.query=q
    def searchYoutube(self,maxr):
        from apiclient.discovery import build
        from apiclient.errors import HttpError
        from oauth2client.tools import argparser

        DEVELOPER_KEY = "AIzaSyBDgwtalxdPqZnNOHpoaV6wV50AW75-mUk"
        YOUTUBE_API_SERVICE_NAME = "youtube"
        YOUTUBE_API_VERSION = "v3"

        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)

        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = youtube.search().list(
          q=self.query,
          part="id,snippet",
          maxResults=maxr,
          type='video'
        ).execute()

        vid_ids = []
        videos = []
        channels = []
        playlists = []

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                           search_result["id"]["videoId"]))
                vid_ids.append(search_result["id"]["videoId"])
            elif search_result["id"]["kind"] == "youtube#channel":
                channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                             search_result["id"]["channelId"]))
            elif search_result["id"]["kind"] == "youtube#playlist":
                playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                              search_result["id"]["playlistId"]))

        #print "Videos:\n", "\n".join(videos), "\n"
        #print "Channels:\n", "\n".join(channels), "\n"
        #print "Playlists:\n", "\n".join(playlists), "\n"

        return vid_ids


    def searchWikiHow(self):
        return []
