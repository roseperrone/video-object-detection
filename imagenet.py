'''
This file contains utility methods for mapping prediction scores
to class labels, and in the case of the detector, also detected
bounding boxes.
'''

import heapq
import pandas as pd
from os.path import join
from collections import defaultdict


def _top_scores(predictions, n_top_scores=100):
  '''
  Arguments:
    predictions: a numpy 1x1000 array that contains one float per class
  Returns:
    a list of `n_top_predictions` tuples that each contain the
    score and a string that is a comma-separated list of
    class names corresponding to that score.
  '''
  scores = []
  noun_ids = []

  for index, score in heapq.nlargest(
    n_top_scores, enumerate(predictions), lambda x: x[1]):
    scores.append(score)
    noun_ids.append(_get_noun_id(index))

  return noun_ids, scores

def top_boxed_scores(detection_output_file, n_top_scores=100):
  '''
  Returns:
    a list of tuples that each take the following format:
    (xmin, xmin, xmax, ymax, noun_ids, scores)
      where the first four values indicate the bounding box, and
      `scores` and `noun_ids` are parallel arrays.
      `scores` is an ordered list of `n_top_scores`. `noun_ids`
      is a list of ImageNet noun ids that correspond to the scores.
  '''
  df = pd.read_pickle('/tmp/detection_results.bin')
  boxed_scores = defaultdict(list)
  for i in range(df.index.shape[0]):
    noun_ids, scores = _top_scores(df.prediction[i].as_matrix(),
                                   n_top_scores)
    # df.index[i] is the image filename
    boxed_scores[df.index[i]].append(
      (df.xmin[i], df.xmax[i], df.ymin[i], df.ymax[i], noun_ids, scores))
  return boxed_scores

NOUN_IDS = None

def _get_noun_id(index):
  '''
  Gets noun id from the list of 1000 ILSVRC12.

  You can find the list of 1000 ImageNet nouns here:
  http://www.image-net.org/challenges/LSVRC/2013/browse-synsets
  (as used in ILSVRC2012)
  '''
  global NOUN_IDS
  if NOUN_IDS is None:
    NOUN_IDS = []
    with open('caffe/data/ilsvrc12/caffe_ilsvrc12/synset_words.txt') as f:
      for line in f.read().split('\n'):
        NOUN_IDS.append(line.split(' ')[0])
  return NOUN_IDS[index]

NOUN_DESCRIPTIONS = None

def _populate_noun_descriptions():
  global NOUN_DESCRIPTIONS
  NOUN_DESCRIPTIONS = defaultdict()
  with open('caffe/data/ilsvrc12/caffe_ilsvrc12/synset_words.txt') as f:
    for line in f.read().split('\n'):
      tokens = line.split(' ')
      NOUN_DESCRIPTIONS[tokens[0]] = ' '.join(tokens[1:]).split(', ')

def get_description(noun_id):
  '''
  Returns the noun description that corresponds to the noun_id.

  For example, the noun description for the id n09835506 is
  "ballplayer, baseball player"
  '''
  if NOUN_DESCRIPTIONS is None:
    _populate_noun_descriptions()
  return ', '.join(NOUN_DESCRIPTIONS[noun_id])

def get_noun_id(noun):
  '''
  The noun must fully match one of the comma-separated tokens
  e.g. "Nile crocodile" would return "n01697457", because this entry
  is present in caffe/data/ilsvrc12/caffe_ilsvrc12/synset_words.txt:
  "n01697457 African crocodile, Nile crocodile, Crocodylus niloticus"
  '''
  if NOUN_DESCRIPTIONS is None:
    _populate_noun_descriptions()
  for noun_id, tokens in NOUN_DESCRIPTIONS.iteritems():
    if noun in tokens:
      return noun_id
  raise Exception(noun + ' is not present in the ImageNet ILSVRC12 dataset')

