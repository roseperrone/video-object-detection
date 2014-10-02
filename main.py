
from os import system

from video_utils import get_video, get_prepared_images

import pdb

def where_is_noun_in_video(url, noun):
  '''
  Returns:
    a list of tuples of video segments in which that noun appears,
    in seconds. e.g. [(14.4, 20.2), (34.2, 89.2)]
  '''
  video_filename = get_video(url)
  images = get_prepared_images(video_filename)
  noun_detected_times = []
  for image, time in images:
    detected_nouns = detect(image)
    if noun in detected_nouns:
      noun_detected_times.append(time)
  return approximate_video_segments(noun_detected_times)

def detect(image):
  '''
  Uses the 19-layer neural net from:
    Very Deep Convolutional Networks for Large-Scale Image Recognition
    K. Simonyan, A. Zisserman
    arXiv:1409.1556
  You can find information about this neural net here:
    https://gist.github.com/ksimonyan/3785162f95cd2d5fee77#file-readme-md

  Returns:

  '''
  root = dirname(abspath(__file__))
  cmd = root + '/caffe/python/detect.py '
  cmd += ''

def approximate_video_segments(times):
  '''
  Arguments:
    times: The times at which the noun was detected in the video, in seconds
  Returns:
    approximate segments of time at which the noun was detected
  '''
  pass


if __name__ == '__main__':
  # Video is how to make coffee
  print where_is_noun_in_video('https://www.youtube.com/watch?v=2Ao5b6uqI40',
                               'cup')
