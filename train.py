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

from os.path import join, dirname, abspath
from os import system

ROOT = dirname(abspath(__file__))
# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
 'The wordnet id of the noun in the positive images')
gflags.DEFINE_string('aux_dir',
  join(ROOT, 'data/imagenet', FLAGS.wnid, 'aux/2014-11-12-n07840804'),
  'The directory in which to place all generated auxiliary files, '
  'like create_imagenet.sh')



# Whether caffe should resize images to 256x256. Should be True when
# the images aren't that size already
SHOULD_RESIZE_IMAGES = True

def create_leveldbs():
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
  with open(join(FLAGS.aux_dir, 'create_imagenet.sh'), 'w') as f:
    f.writelines(lines)

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
  set_gflags()
  global WNID_DIR
  WNID_DIR = join(ROOT, 'data/imagenet', FLAGS.wnid)
  system('mkdir -p ' + FLAGS.aux_dir)
  create_leveldbs()
  import pdb; pdb.set_trace()
  compute_image_mean()
  generate_prototxt_files()
  generate_train_script()
  train()
  test()

