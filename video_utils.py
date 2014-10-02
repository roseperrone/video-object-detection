'''
Utility methods for downloading and preparing video frames.
'''
from os.path import dirname, abspath, exists, splitext, basename
from os import system
from PIL import Image
import numpy as np
import cv2
import re
import pafy
import shelve
import pylab

import pdb

ROOT = dirname(abspath(__file__))

def get_video(url):
  '''
  Returns the filename of the downloaded mp4
  '''
  video = pafy.new(url)
  stream = _get_stream(video)
  filename = _downloaded_filename(url, video.title, stream.extension)
  # First check if we cached it
  mp4_filename = _converted_mp4_filename(filename)
  if exists(mp4_filename):
    return mp4_filename
  stream.download(filename)
  return _convert_video_to_mp4(filename)

def get_prepared_images(video_filename):
  '''
  Returns:
    A list of tuples of the format:
      (image, time)
    where `time` is the time at which the image appears in the video,
    in seconds.
  '''
  cap = cv2.VideoCapture(video_filename)
  frame_count = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
  frames_per_s = int(cap.get(cv2.cv.CV_CAP_PROP_FPS))

  images = []
  # TODO take out the 10x after the full pipeline works
  for i in range(frame_count)[::10*frames_per_s]:
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, i)
    retval, image = cap.read()
    images.append(_prepare_image(Image.fromarray(image)))
    print len(images), '/', frame_count/(10*frames_per_s)
  return images

def _prepare_image(image):
  'Resizes the images to 256x256 and demeans the images.'
  image = _resize_and_paste(image, (256, 256))
  image = np.asarray(image)
  retval = image - [103.939, 116.779, 123.68]
  return retval

def _resize_and_paste(image, new_shape):
  '''
  The original image proportions are left unchanged; any left over area
  is filled with black.
  '''
  new_width, new_height = new_shape[:2]
  cw, ch = image.size
  result = Image.new('RGB', (new_width, new_height), color=(0,0,0))

  dw = float(new_width) / cw
  dh = float(new_height) / ch

  if dw < dh:
    ratio = float(new_width) / cw
    image = image.resize((int(cw * ratio), int(ch * ratio)))
    cw, ch = image.size
    result.paste(image, (0, (new_height - ch) / 2))
  else:
    ratio = float(new_height) / ch
    image = image.resize((int(cw * ratio), int(ch * ratio)))
    cw, ch = image.size
    result.paste(image, ((new_width - cw) / 2, 0))
  return result

def _show_image(image):
  pylab.imshow(image)
  pylab.show()

def _get_stream(video):
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

def _convert_video_to_mp4(filename):
  'OpenCV seems to only like mp4'
  target = _converted_mp4_filename(filename)
  print target
  system('ffmpeg -i ' + filename + ' -vcodec copy ' + target)
  return target

def _converted_mp4_filename(filename):
  return ROOT + '/data/videos/' + splitext(basename(filename))[0] + '.mp4'

def _downloaded_filename(url, title, extension):
  return dirname(abspath(__file__)) + '/data/videos/' + \
         re.match('.*v=(.*$)', url).groups()[0] + \
         ''.join(x for x in title if x.isalnum()) + '.' + extension

