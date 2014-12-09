'''
Uses a pretrained model on the ImageNet dataset to predict the liklihood
the entire image displays any of 1000 categories.
'''

from os import system
from os.path import join, splitext, basename, dirname, abspath
import numpy as np

ROOT = dirname(abspath(__file__))

# TODO this is out of date
def classify(image_filename):
  '''
  Returns:
    a numpy array containing a score for each of 1000 ImageNet classes
  '''
  image_name = splitext(basename(image_filename))[0]
  predictions_filename = '/tmp/classification_predictions_' + image_name + '.npy'
  cmd = join(ROOT, 'caffe/python/classify.py')
  cmd += ' --pretrained_model=data/models/' + \
         'bvlc_reference_caffenet.caffemodel'
  cmd += ' --channel_swap=\'\'' # the image is already BGR.
  #cmd += ' --pretrained_model=data/models/VGG_ILSVRC_19_layers.caffemodel' TODO use this one
  cmd += ' ' + image_filename
  cmd += ' ' + predictions_filename
  print cmd
  system(cmd)
  return np.load(predictions_filename).tolist()[0]
