'''
  Detection and classification use the 19-layer neural net from:
    Very Deep Convolutional Networks for Large-Scale Image Recognition
    K. Simonyan, A. Zisserman
    arXiv:1409.1556
  You can find information about this neural net here:
    https://gist.github.com/ksimonyan/3785162f95cd2d5fee77#file-readme-md
'''
import cv2
from os import system, listdir
from os.path import dirname, abspath, join, splitext, basename
import heapq
import numpy as np
import pdb

from video_utils import get_video, get_prepared_images, draw_image_labels, \
                        write_video, video_url


ROOT = dirname(abspath(__file__))
CLASSES = None # TODO use a memoize decorator instead

VIDEO_IDS = [
  # how to hard boil an egg
  '1QK-DGlRcTo',
  '7-9OEohpivA',
  'lbzhyvH74w8',
  'qX7A0LPIuKs',
  's1oUDsonIzg',
  'sSni2HTfvM',
  'wdasrVE5NOc',
  'zuMslqJKQo',
  # how to poach an egg
  'jk36el4_Rbc',
  'JrRqG9Apt6g',
  'KtZ14xEbgzg',
  'pAWduxoCgVk',
  'UMiCy8EH1go',
  'xpN1dlH3tWo',
  'yppgDL0Mn3g',
  # how to scramble an egg
  '65ifzkFi614',
  'FbLU87PYsZE',
  'Nbh64ntT3EM',
  'R4vDqlKMbrk',
  's9r-CxnCXkg',
  'TGyb7uBXe9E',
  'Be0koDmxrtQ',
  'M8SHMUBnm4A',
  'PUP7U5vTMM0',
  's9r-CxnCXkg',
  # how to make an omelet
  '1dGBRGtyzX0',
  '57afEWn-QDg',
  'AgHgbn_sVUw',
  'AJ2uBYCVHik',
  'OQyRuOEKfVk',
  'PLDUqyS2AGA',
  'PzWsyPHoSyQ',
  'r09Hgeb9-6s',
  'zglsDdaBf4g',
  ]

def where_is_noun_in_video(video_id, noun):
  '''
  Returns:
    a list of tuples of video segments in which that noun appears,
    in seconds. e.g. [(14.4, 20.2), (34.2, 89.2)]
  '''
  # TODO change 10,000 to 1,000 after the full pipeline works
  image_dir = get_prepared_images(video_url(video_id), 10000)
  noun_detected_times = classify(image_dir, '19_layers')
  #noun_detected_times = detect(image_dir)
  #return approximate_video_segments(noun_detected_times)

def detect(image_dir):
  '''
  '''
  image_filenames_txt = '/tmp/image_filenames.txt'
  with open(image_filenames_txt, 'w') as f:
    # skip the mac .DS_Store file
    image_filenames = [join(image_dir, x) for x in listdir(image_dir) if not x == '.DS_Store']
    f.write('\n'.join(image_filenames))
  cmd = join(ROOT, 'caffe/python/detect.py')
  cmd += ' --input_file=' + image_filenames_txt
  cmd += ' --output_file=' + '/tmp/detection_results.csv'
  cmd += ' --pretrained_model=../data/models/VGG_ILSVRC_19_layers.caffemodel'
  system(cmd)
  print cmd

def classify(image_dir, network):
  '''
  `network` can be ccv_2012 or 19_layers
  '''
  image_name = splitext(basename(image_file))[0]
  image_path = join(image_dir, image_file)
  if network == '19_layers':
    for image_file in listdir(image_dir):
      output = '/tmp/classification_results_' + image_name + '.npy'
      cmd = join(ROOT, 'caffe/python/classify.py')
      cmd += ' --pretrained_model=data/models/bvlc_reference_caffenet.caffemodel'
      #cmd += ' --pretrained_model=data/models/VGG_ILSVRC_19_layers.caffemodel' TODO use this one
      cmd += ' ' + image_path
      cmd += ' ' + output
      print cmd
      system(cmd)
      labels = top_labels(output) # TODO why all the same score?
      draw_image_labels(image_path, labels)
    write_video(image_dir)
  elif network == 'ccv_2012':
    for image_file in listdir(image_dir):
      layer_offset = -2;
      # TODO unfinished
      lines = os.popen(
        ' '.join([join(ROOT, 'DeepBelief/deepbelief'),
                  file,
                  join(ROOT, 'DeepBelief/ccv2012.ntwk '),
                  str(layer_offset)])).read().split('\n')[:-1]
  else:
    raise Exception('That network is unsupported')

def top_labels(classification_output_file):
  scores = np.load(classification_output_file).tolist()[0]
  top_scores = heapq.nlargest(5, enumerate(scores), lambda x: x[1])
  for score in top_scores:
    print scores[1], get_classes()[score[0]]
  return [get_classes()[score[0]] for score in top_scores]

def get_classes():
  '''
  Gets the list of 1000 ILSVRC12 classes.
  '''
  global CLASSES
  if CLASSES is None:
    CLASSES = []
    with open('caffe/data/ilsvrc12/caffe_ilsvrc12/synset_words.txt') as f:
      for line in f.read().split('\n'):
        tokens = line.split(' ')[1:]
        CLASSES.append(' '.join(tokens))
  return CLASSES

if __name__ == '__main__':
  for video_id in VIDEO_IDS:
    print where_is_noun_in_video(video_id, 'cup')
    pdb.set_trace()
