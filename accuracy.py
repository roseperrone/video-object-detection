'''
Run this script after judging detection predictions
(see judge_predictions.py) to determine precision and recall.
'''

import json

import gflags
from gflags import FLAGS
from flags import set_gflags

gflags.DEFINE_string('log', None, 'Predicton logs filename');
gflags.MarkFlagAsRequired('log')

def determine_accuracy(predictions_log_filename):
  '''
  Detection accuracy is the fraction of images where the object is
  correctly detected.

  An object is considered correctly detected if the intersection over union
  of the predicted bounding box and the ground truth bounding box of > 0.5
  '''
  num_true_positives = 0
  num_false_positives = 0
  num_false_negatives = 0

  with open(predictions_log_filename) as f:
    for line in f.readlines():
      for letter in json.loads(line)['code']:
        if letter == 'c':
          num_true_positives += 1
        elif letter == 'p':
          num_false_positives += 1
        elif letter == 'n':
          num_false_negatives += 1

  precision = float(num_true_positives) / \
                (num_true_positives + num_false_positives)
  recall = float(num_true_positives) / \
                (num_true_positives + num_false_negatives)

  print 'precision:', precision
  print 'recall:', recall

if __name__ == '__main__':
  set_gflags()
  determine_accuracy(FLAGS.log)
