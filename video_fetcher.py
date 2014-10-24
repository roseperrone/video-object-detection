from os.path import dirname, abspath, exists, splitext, basename, join
from os import system
import pafy
import re

from performance import timeit

ROOT = dirname(abspath(__file__))

@timeit
def fetch_video(url):
  '''
  Returns the filename of the downloaded mp4
  '''
  video = pafy.new(url)
  stream = get_stream(video)
  filename = downloaded_filename(url, video.title, stream.extension)
  # First check if we cached it
  mp4_filename = converted_mp4_filename(filename)
  if exists(mp4_filename):
    return mp4_filename
  stream.download(filename)
  return convert_video_to_mp4(filename)

def get_stream(video):
  'Gets the lowest resolution stream that has the smallest dimension >= 256'
  # my ffmpeg build doesn't convert webm's, so I'm just using m4v for now
  dimensions = [stream.dimensions for stream in video.videostreams \
    if stream.dimensions[0] >= 256 and stream.dimensions[1] >= 256 \
      and str(stream.extension) == 'm4v']
  if len(dimensions) == 0:
    raise Exception('Video does not have a suffciently high resolution')
  res = min(dimensions, key=lambda x:x[0]*x[1])

  for stream in video.videostreams:
    if stream.resolution == str(res[0]) + 'x' + str(res[1]):
      return stream

def convert_video_to_mp4(filename):
  'OpenCV seems to only like mp4'
  target = converted_mp4_filename(filename)
  system('ffmpeg -i ' + filename + ' -vcodec copy ' + target)
  return target

def converted_mp4_filename(filename):
  return ROOT + '/data/videos/' + splitext(basename(filename))[0] + '.mp4'

def downloaded_filename(url, title, extension):
  return dirname(abspath(__file__)) + '/data/videos/' + get_video_id(url) + \
         sanitized_video_title(title) + '.' + extension

def sanitized_video_title(title):
  return ''.join(x for x in title if x.isalnum())

def get_video_id(url):
  return re.match('.*v=(.*$)', url).groups()[0]

def video_url(video_id):
  return 'https://www.youtube.com/watch?v=' + video_id
