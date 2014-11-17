'''
Run this script after running create_data_splits.py and before
manually generating the prototxt files.

This script generates create_imagenet.sh and imagenet_mean.binaryproto
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

# Whether caffe should resize images to 256x256. Should be True when
# the images are net that size already
SHOULD_RESIZE_IMAGES = True

# Whether caffe should resize images to 256x256. Should be True when
# the images are net that size already
SHOULD_RESIZE_IMAGES = True

def create_lmdbs():
  '''
  See:
    http://caffe.berkeleyvision.org/gathered/examples/imagenet.html
  for documentation

  These files should not exist prior to running this function:
    WNID_DIR/ilsvrc12_train_lmbd
    WNID_DIR/ilsvrc12_test_lmbd
  '''
  DEBUG_LOG = True # Set this to true to make `create_imagenet.sh`
                   # generate more information to inspect
  with open(join(ROOT, 'caffe/examples/imagenet/create_imagenet.sh')) as f:
    lines = list(f)
    for i in range(len(lines)):
      if 'EXAMPLE=examples/imagenet' in lines[i]:
        # the destination dir of the train and test lmdb databases
        lines[i] = 'EXAMPLE=' + WNID_DIR + '\n'
      if 'DATA=data/ilsvrc12' in lines[i]:
        # the location of the category files
        lines[i] = 'DATA=' + WNID_DIR + '\n'
      if 'TOOLS=build/tools' in lines[i]:
        lines[i] = '\n'
      if 'TRAIN_DATA_ROOT=/path/to/imagenet/train/' in lines[i]:
        lines[i] = 'TRAIN_DATA_ROOT=' + join(WNID_DIR, 'images/train') + '\n'
      if 'VAL_DATA_ROOT=/path/to/imagenet/val/' in lines[i]:
        lines[i] = 'VAL_DATA_ROOT=' + join(WNID_DIR, 'images/test') + '\n'
      if SHOULD_RESIZE_IMAGES and 'RESIZE=false' in lines[i]:
        lines[i] = 'RESIZE=true\n'
      if 'GLOG_logtostderr=1 $TOOLS/convert_imageset' in lines[i]:
        if DEBUG_LOG:
          lines[i] = 'GLOG_logtostderr=1 '
        else:
          lines[i] = 'GLOG_logtostderr=0 '
        lines[i] += join(ROOT, 'caffe/build/tools/convert_imageset') + '\\\n'
      if '$DATA/val.txt \\' in lines[i]:
        lines[i] = '    $DATA/test.txt \\\n'
      if '$EXAMPLE/ilsvrc12_val_lmdb' in lines[i]:
        lines[i] = '    $EXAMPLE/ilsvrc12_test_lmdb\n'
  with open(join(WNID_DIR, 'aux/create_imagenet.sh'), 'w') as f:
    f.writelines(lines)

def compute_image_mean():
  # compute_image_mean Usage:
  # compute_image_mean input_db output_file db_backend[leveldb or lmdb]
  system('/Users/rose/home/video-object-detection/caffe/.build_release/tools/'
         'compute_image_mean.bin '
         join(WNID_DIR, 'ilsvrc12_train_lmdb '),
         'image_mean.binaryproto '
         'lmdb')

if __name__ == '__main__':
  set_gflags()
  global WNID_DIR
  WNID_DIR = join(ROOT, 'data/imagenet', FLAGS.wnid)
  system('mkdir -p ' + join(WNID_DIR, 'aux'))
  create_lmdbs()
  compute_image_mean()
  system('mkdir -p ' + join(WNID_DIR, 'snapshots'))

