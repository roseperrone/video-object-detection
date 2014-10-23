'''
This file contains utility methods for mapping prediction scores
to class labels, and in the case of the detector, also detected
bounding boxes.
'''

import heapq
import pandas as pd
from os.path import join
from collections import defaultdict


def top_labels(predictions, n_top_predictions=5):
  '''
  Arguments:
    predictions: a numpy 1x1000 array that contains one float per class
  Returns:
    a list of strings of the format <score> <claass names> for the
    `n_top_predictions` top predictions, and the mean of the
    top `n_top_predictions`
  '''
  top_predictions = heapq.nlargest(
    n_top_predictions, enumerate(predictions), lambda x: x[1])
  total = 0
  for prediction in top_predictions:
    total += prediction[1]
  mean = total / float(n_top_predictions)
  return (["{0:.4f}".format(prediction[1]) + ' ' + \
           _get_classes()[prediction[0]] \
           for prediction in top_predictions],
          mean)

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

CLASSES = None

def _get_classes():
  '''
  Gets the list of 1000 ILSVRC12 classes.

  You can find the list of 1000 ImageNet classes here:
  http://www.image-net.org/challenges/LSVRC/2013/browse-synsets
  (as used in ILSVRC2012)
  '''
  global CLASSES
  if CLASSES is None:
    CLASSES = []
    with open('caffe/data/ilsvrc12/caffe_ilsvrc12/synset_words.txt') as f:
      for line in f.read().split('\n'):
        tokens = line.split(' ')[1:]
        CLASSES.append(' '.join(tokens))
  return CLASSES

