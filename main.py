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
import pandas as pd
import pdb
from collections import defaultdict

from performance_stats import timeit
from video_metadata import NOUNS_AND_VIDEO_IDS
from video_utils import get_prepared_images, draw_image_labels, \
                        write_video, video_url, draw_boxes

import gflags
from gflags import FLAGS

USE_CACHE = True
HUSH_CAFFE = False

ROOT = dirname(abspath(__file__))
CLASSES = None
N_FRAMES = 2 # just for testing the pipeline

def where_is_noun_in_video(video_id, noun):
  '''
  Returns:
    a list of tuples of video segments in which that noun appears,
    in seconds. e.g. [(14.4, 20.2), (34.2, 89.2)]
  '''
  # TODO change 10,000 to 1,000 after the full pipeline works
  image_dir = get_prepared_images(video_url(video_id), 10000, USE_CACHE)
  #classify(image_dir, noun)
  detect(image_dir, noun)

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
    if HUSH_CAFFE:
      cmd += ' > /dev/null'
    print cmd
    system(cmd)
    predictions = np.load(classification_output_file).tolist()[0]
    top_100_labels, top_100_score_mean = top_labels(predictions, 100)
    matching_label = [label for label in top_100_labels if noun in label]
    label = '' if len(matching_label) == 0 else matching_label[0]
    labels = [label, 'Top 10% mean: ' + "{0:.4f}".format(top_100_score_mean)]
    print '\n'.join(labels)
    draw_image_labels(image_path, labels)
  write_video(image_dir)

#TODO: selective_search is not supported on mac os > 10.7. maybe try to link clang

@timeit
def detect(image_dir, noun):
  '''
  On mac 10.9 running MATLAB R2013a, to make the selective_search work
  (the generator of the windows over which the classifier is run),
  I needed to change 10.7 to 10.9 in
  /Applications/MATLAB_R2013a_Student.app/bin/mexopts.sh, and
  (see http://www.mathworks.com/matlabcentral/answers/87709-just-upgraded-to-x-code-5-0-on-my-mac)
  add -std=c++11 to CXXFLAGS in said script.
  Then in /Users/rose/video-object-detection/caffe/python/caffe/selective_search_ijcv_with_python/selective_search_rcnn
  I needed to add -Dchar16_t=uint16_t to
  mex Dependencies/anigaussm/anigauss_mex.c Dependencies/anigaussm/anigauss.c -output anigauss
  (see http://stackoverflow.com/questions/22367516/mex-compile-error-unknown-type-name-char16-t)
  '''
  image_filenames_txt = '/tmp/image_filenames.txt'
  output_filename = '/tmp/detection_results.bin'
  with open(image_filenames_txt, 'w') as f:
    # skip the mac .DS_Store file
    image_filenames = [join(image_dir, x) for x in listdir(image_dir) if not x == '.DS_Store']#[:N_FRAMES]
    if len(image_filenames) > 1:
      f.write('\n'.join(image_filenames))
    else:
      f.write(image_filenames[0])
  cmd = join(ROOT, 'caffe/python/detect.py')
  #cmd += ' --pretrained_model=../data/models/VGG_ILSVRC_19_layers.caffemodel'
  cmd += ' --pretrained_model=data/models/bvlc_reference_caffenet.caffemodel'
  cmd += ' --model_def=data/models/bvlc_reference_caffenet/deploy.prototxt'
  cmd += ' ' + image_filenames_txt
  # In detect.py, the .csv output
  # code is buggy, and the hdf5 gave weird uint8 prediction values, so I
  # pickled the pandas DataFrame instead.
  cmd += ' ' + output_filename
  if HUSH_CAFFE:
    cmd += ' > /dev/null'
  print cmd
  system(cmd)
  draw_results(output_filename, basename(image_dir), noun)

@timeit
def draw_results(output_filename, image_dir_name, noun):
  labelled_boxes = boxes_and_top_labels(output_filename, 100)
  boxes_containing_noun = find_boxes_containing_noun(labelled_boxes, noun)
  draw_boxes(boxes_containing_noun, image_dir_name)

def find_boxes_containing_noun(labelled_boxes, noun):
  found = defaultdict(list)
  for image_filename, boxes in labelled_boxes.iteritems():
    for i, tup in enumerate(boxes):
      xmin, xmax, ymin, ymax, labels = tup
      for label in labels:
        if noun in label: # FIXME: egg is not eggnog.
          found[image_filename].append((image_filename, (xmin, xmax, ymin, ymax, [label])))
          #pdb.set_trace()
    if len(found[image_filename]) == 0:
      found[image_filename].append((0, 0, 0, 0, ['Not found']))
  return found

def boxes_and_top_labels(detection_output_file, n_top_scores=5):
  '''
  Returns:
    a list of tuples that take the following format:
    (xmin, xmin, xmax, ymax, predictions)
      where the first four values indicate the bounding box
      of the image with the detected predictions, and
      predictions is a list of `n_top_scores` that each
      take the format: (score, class)
  '''
  df = pd.read_pickle('/tmp/detection_results.bin')
  labelled_boxes = defaultdict(list)
  for i in range(df.index.shape[0]):
    labelled_boxes[df.index[i]].append((df.xmin[i],
      df.xmax[i],
      df.ymin[i],
      df.ymax[i],
      top_labels(df.prediction[i].as_matrix())[0]))
  return labelled_boxes

def top_labels(predictions, n_top_predictions=5):
  '''
  Arguments:
    predictions: a numpy 1x1000 array that contains one float per class
  Returns:
    a list of strings of the format <score> <claass names> for the
    `n_top_predictions` top predictions, and the mean of the top `n_top_predictions`
  '''
  top_predictions = heapq.nlargest(n_top_predictions, enumerate(predictions), lambda x: x[1])
  total = 0
  for prediction in top_predictions:
    total += prediction[1]
  mean = total / float(n_top_predictions)
  return (["{0:.4f}".format(prediction[1]) + ' ' + get_classes()[prediction[0]] \
           for prediction in top_predictions],
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
  for noun, video_id_list in NOUNS_AND_VIDEO_IDS.iteritems():
    for video_id in video_id_list:
      where_is_noun_in_video(video_id, noun)
      pdb.set_trace()
