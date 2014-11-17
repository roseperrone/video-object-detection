'''
This script trains the neural net on the train and test set created
by create_data_splits.py using the auxiliary files created in
prepare_data.py and the prototxt files created manually
(see prototxt_generation_instructions.md).

This github issue is wildly helpful:
  https://github.com/BVLC/caffe/issues/550
This documentation is good too:
  http://caffe.berkeleyvision.org/gathered/examples/imagenet.html

Usage:
  Run python `
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

from os.path import join, dirname, abspath
from os import system

ROOT = dirname(abspath(__file__))
# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
 'The wordnet id of the noun in the positive images')

def generate_train_script():
  pass

def train():
  pass

def test():
  pass

if __name__ == '__main__':
  set_gflags()
  global WNID_DIR
  WNID_DIR = join(ROOT, 'data/imagenet', FLAGS.wnid)
  if FLAGS.create_lmdbs_and_compute_image_mean:
    system('mkdir -p ' + FLAGS.aux_dir)
    create_lmdbs()
    compute_image_mean()

  generate_prototxt_files()
  generate_train_script()
  train()
  test()

