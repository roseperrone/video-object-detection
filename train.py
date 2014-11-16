'''
This script trains the neural net on the train and test set created
by create_data_splits.py

This github issue is wildly helpful:
  https://github.com/BVLC/caffe/issues/550
This documentation is good too:
  http://caffe.berkeleyvision.org/gathered/examples/imagenet.html


'''

import gflags
from gflags import FLAGS
from flags import set_gflags

# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
                     'The wordnet id of the noun in the positive images')

from os.path import join

ROOT = dirname(abspath(__file__))

##################### TODO
# The directory in which to place all generated auxiliary files
AUXILIARY_DIR = (join(ROOT, 'aux/2014-11-12-n07841037'))

# Whether caffe should resize images to 256x256. Should be True when
# the images aren't that size already
SHOULD_RESIZE_IMAGES = True

def create_leveldbs():
  DEBUG_LOG = False # Set this to true to make `create_imagenet.sh`
                    # generate more information to inspect
  pass

def compute_image_mean():
  pass

def generate_prototxt_files():
  pass

def generate_train_script():
  pass

def train():
  pass

def test():
  pass

if __name__ == '__main__':
  create_leveldbs()
  compute_image_mean()
  generate_prototxt_files()
  generate_train_script()
  train()
  test()

