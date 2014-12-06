'''
This script trains the neural net on the train and test set created
by create_data_splits.py using the auxiliary files created in
prepare_data.py and the prototxt files created manually
(see prototxt_generation_instructions.md).
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

from os.path import join, dirname, abspath, exists
from os import system

gflags.DEFINE_string('dataset_dir', None, 'This is the directory that '
  'contains `aux`, `snapshots`, and all the data relevant to training')
gflags.MarkFlagAsRequired('dataset_dir')
gflags.DEFINE_boolean('time', False, 'Set to true if you are interested in '
  'dissecting the runtime')
gflags.DEFINE_string('snapshot', None, 'If training got interrupted, '
  'resume from this snapshot. This snapshot is a .solverstate file.')
gflags.DEFINE_string('pretrained_caffemodel', None, 'The path to a .caffemodel '
  'you want to finetune')

ROOT = dirname(abspath(__file__))

if __name__ == '__main__':
  set_gflags()
  aux_dir = join(FLAGS.dataset_dir, 'aux')
  cmd = join(ROOT, 'caffe/.build_release/tools/caffe.bin')
  if FLAGS.time:
    cmd += ' time --model=' + join(aux_dir, 'train_val.prototxt')
  else:
    cmd += ' train --solver=' + join(aux_dir, 'solver.prototxt')
    if FLAGS.snapshot is not None:
      cmd += ' --snapshot=' + FLAGS.snapshot
    if FLAGS.pretrained_caffemodel is not None:
      cmd += ' --weights=' + FLAGS.pretrained_caffemodel
  print cmd
  system(cmd)
