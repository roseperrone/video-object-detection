import os
import sys
import lmdb
import pylab
import numpy as np
from os.path import dirname, abspath, join

ROOT = dirname(abspath(__file__))
sys.path.append(join(ROOT, 'caffe/python'))

from caffe.proto import caffe_pb2
import caffe.io

import gflags
from gflags import FLAGS
from flags import set_gflags
gflags.DEFINE_string('db_path', None, 'Path to LMDB database')
gflags.MarkFlagAsRequired('db_path')

def main():
  if not os.path.exists(FLAGS.db_path):
      raise Exception('db not found')

  lmdb_env = lmdb.open(FLAGS.db_path)  # equivalent to mdb_env_open()
  lmdb_txn = lmdb_env.begin()  # equivalent to mdb_txn_begin()
  lmdb_cursor = lmdb_txn.cursor()  # equivalent to mdb_cursor_open()
  index = 3000
  count = 0
  for key, value in lmdb_cursor:
    count += 1
    print count
    if count > index:
      show_image(value)

def show_image(lmdb_value):
  datum = caffe_pb2.Datum()
  datum.ParseFromString(value)
  image = np.zeros((datum.channels, datum.height, datum.width))
  image = caffe.io.datum_to_array(datum)
  image = np.transpose(image, (1, 2, 0))
  pylab.imshow(image)
  pylab.show()

if __name__ == '__main__':
  set_gflags()
  main()
