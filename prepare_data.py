'''
Run this script after running create_data_splits.py and before
manually generating the prototxt files.

This script generates create_imagenet.sh and imagenet_mean.binaryproto

Make sure you delete the lmdb directories if you rerun this script.

This github issue is wildly helpful:
  https://github.com/BVLC/caffe/issues/550
This documentation is good too:
  http://caffe.berkeleyvision.org/gathered/examples/imagenet.html
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
gflags.DEFINE_string('dataset', None, 'The name of the directory that contains '
                     'the test and train image directories, as well as the '
                     'train.txt and test.txt files')
gflags.MarkFlagAsRequired('dataset')

# Whether caffe should resize images to 256x256. Should be True when
# the images are net that size already
SHOULD_RESIZE_IMAGES = True

def create_lmdbs():
  '''
  See:
    http://caffe.berkeleyvision.org/gathered/examples/imagenet.html
  for documentation

  These files should not exist prior to running this function:
    DATASET_DIR/ilsvrc12_train_lmbd
    DATASET_DIR/ilsvrc12_test_lmbd
  '''
  DEBUG_LOG = True # Set this to true to make `create_imagenet.sh`
                   # generate more information to inspect
  with open(join(ROOT, 'caffe/examples/imagenet/create_imagenet.sh')) as f:
    lines = list(f)
    for i in range(len(lines)):
      if 'EXAMPLE=examples/imagenet' in lines[i]:
        # the destination dir of the train and test lmdb databases
        lines[i] = 'EXAMPLE=' + DATASET_DIR + '\n'
      elif 'DATA=data/ilsvrc12' in lines[i]:
        # the location of the category files
        lines[i] = 'DATA=' + join(WNID_DIR, 'images', FLAGS.dataset) + '\n'
      elif 'TOOLS=build/tools' in lines[i]:
        lines[i] = '\n'
      elif 'TRAIN_DATA_ROOT=/path/to/imagenet/train/' in lines[i]:
        lines[i] = 'TRAIN_DATA_ROOT=' + join(
          WNID_DIR, 'images', FLAGS.dataset, 'train/') + '\n'
      elif 'VAL_DATA_ROOT=/path/to/imagenet/val/' in lines[i]:
        lines[i] = 'VAL_DATA_ROOT=' + join(WNID_DIR, 'images',
          FLAGS.dataset, 'test/') + '\n'
      elif SHOULD_RESIZE_IMAGES and 'RESIZE=false' in lines[i]:
        lines[i] = 'RESIZE=true\n'
      elif 'GLOG_logtostderr=1 $TOOLS/convert_imageset' in lines[i]:
        if DEBUG_LOG:
          lines[i] = 'GLOG_logtostderr=1 '
        else:
          lines[i] = 'GLOG_logtostderr=0 '
        lines[i] += join(ROOT,
          'caffe/.build_release/tools/convert_imageset.bin') + '\\\n'
      elif '$DATA/val.txt \\' in lines[i]:
        lines[i] = '    $DATA/test.txt \\\n'
      elif '$EXAMPLE/ilsvrc12_val_lmdb' in lines[i]:
        lines[i] = '    $EXAMPLE/ilsvrc12_test_lmdb\n'
      elif '--shuffle' in lines[i]:
        lines[i] = '    --shuffle=True \\\n'
  create_imagenet_filename = join(DATASET_DIR, 'create_imagenet.sh')
  with open(create_imagenet_filename, 'w') as f:
    f.writelines(lines)
  system('chmod 777 ' + create_imagenet_filename)
  system(create_imagenet_filename)

def compute_image_mean():
  # compute_image_mean Usage:
  # compute_image_mean input_db output_file db_backend[leveldb or lmdb]
  cmd = ('/Users/rose/home/video-object-detection/caffe/.build_release/tools/'
         'compute_image_mean.bin ' + join(DATASET_DIR, 'ilsvrc12_train_lmdb ') + \
         join(DATASET_DIR, 'image_mean.binaryproto ') + \
         'lmdb')
  print cmd
  system(cmd)

if __name__ == '__main__':
  set_gflags()
  global WNID_DIR
  WNID_DIR = join(ROOT, 'data/imagenet', FLAGS.wnid)
  global DATASET_DIR
  DATASET_DIR = join(WNID_DIR, 'images', FLAGS.dataset)
  create_lmdbs()
  compute_image_mean()
  system('mkdir -p ' + join(DATASET_DIR, 'snapshots'))

