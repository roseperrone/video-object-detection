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
CLASSES = None

VIDEO_IDS = [
  # how to make banana icecream
  '9uddKYGPEkg',
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
  classify(image_dir, noun)

def classify(image_dir, noun):
  '''
  `network` can be ccv_2012 or 19_layers
  '''
  for image_file in listdir(image_dir):
    image_name = splitext(basename(image_file))[0]
    image_path = join(image_dir, image_file)
    output = '/tmp/classification_results_' + image_name + '.npy'
    cmd = join(ROOT, 'caffe/python/classify.py')
    cmd += ' --pretrained_model=data/models/bvlc_reference_caffenet.caffemodel'
    cmd += ' --channel_swap=\'\'' # the image is alreadiy BGR. No need to convert it.
    #cmd += ' --pretrained_model=data/models/VGG_ILSVRC_19_layers.caffemodel' TODO use this one
    cmd += ' ' + image_path
    cmd += ' ' + output
    print cmd
    system(cmd)
    top_100_labels, top_100_score_mean = top_labels(output, 100)
    matching_label = [label for label in top_100_labels if noun in label]
    label = '' if len(matching_label) == 0 else matching_label[0]
    labels = [label, 'Top 10% mean: ' + "{0:.4f}".format(top_100_score_mean)]
    print '\n'.join(labels)
    draw_image_labels(image_path, labels)
  write_video(image_dir)

#TODO: selective_search is not supported on mac os > 10.7. maybe try to link clang
def detect(image_dir):
  image_filenames_txt = '/tmp/image_filenames.txt'
  with open(image_filenames_txt, 'w') as f:
    # skip the mac .DS_Store file
    image_filenames = [[join(image_dir, x) for x in listdir(image_dir) if not x == '.DS_Store'][0]] # TODO remove the [0]
    if len(image_filenames) > 1:
      f.write('\n'.join(image_filenames))
    else:
      f.write(image_filenames[0])
  cmd = join(ROOT, 'caffe/python/detect.py')
  #cmd += ' --pretrained_model=../data/models/VGG_ILSVRC_19_layers.caffemodel'
  cmd += ' --pretrained_model=data/models/bvlc_reference_caffenet.caffemodel'
  cmd += ' --model_def=data/models/bvlc_reference_caffenet/deploy.prototxt'
  cmd += ' ' + image_filenames_txt
  cmd += ' /tmp/detection_results.csv'
  system(cmd)
  print cmd

def top_labels(classification_output_file, n_top_scores=5):
  '''
  Returns:
    A list of strings of the format <score> <claass names> for the
    `n_top_scores` top scores, and the mean of the top `n_top_scores`
  '''
  scores = np.load(classification_output_file).tolist()[0]
  top_scores = heapq.nlargest(n_top_scores, enumerate(scores), lambda x: x[1])
  total = 0
  for score in top_scores:
    total += score[1]
  mean = total / float(n_largest)
  return (["{0:.4f}".format(score[1]) + ' ' + get_classes()[score[0]] \
           for score in top_scores],
          mean)

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
    where_is_noun_in_video(video_id, 'banana')
    pdb.set_trace()
