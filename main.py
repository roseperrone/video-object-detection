
from os import system, listdir
from os.path import dirname, abspath

from video_utils import get_video, get_prepared_images

import pdb

ROOT = dirname(abspath(__file__))

def where_is_noun_in_video(url, noun):
  '''
  Returns:
    a list of tuples of video segments in which that noun appears,
    in seconds. e.g. [(14.4, 20.2), (34.2, 89.2)]
  '''
  # TODO change 10,000 to 1,000 after the full pipeline works
  image_dir = get_prepared_images(url, 10000)
  noun_detected_times = detect(image_dir)
  return approximate_video_segments(noun_detected_times)

def detect(image_dir):
  '''
  Uses the 19-layer neural net from:
    Very Deep Convolutional Networks for Large-Scale Image Recognition
    K. Simonyan, A. Zisserman
    arXiv:1409.1556
  You can find information about this neural net here:
    https://gist.github.com/ksimonyan/3785162f95cd2d5fee77#file-readme-md

  Returns:

  '''
  image_filenames_txt = '/tmp/image_filenames.txt'
  with open(image_filenames_txt, 'w') as f:
    # skip the mac .DS_Store file
    image_filenames = [x for x in listdir(image_dir) if not x == '.DS_Store']
    f.write('\n'.join(image_filenames))
  cmd = ROOT + '/caffe/python/detect.py'
  pdb.set_trace()
  cmd += ' --input_file=' + image_filenames_txt

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
