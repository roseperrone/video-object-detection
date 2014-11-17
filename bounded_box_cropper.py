'''
After the bounding boxes have been drawn using `draw_bounding_boxes.py`,
every bounded box must be cropped and copied into its own image in order
to train and test the net on them. No resizing to 256x256 is necessary
because I let caffe do that.
TODO make sure caffe warps rather than crops.

The source images should be in `data/imagenet/<wnid>/images/all`,
and the cropped images will be placed in
`data/imagenet/<wnid>/images/cropped`.
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
                     'The wordnet id of the noun in the positive images')

from cropping_utils import get_crop_box

import csv
from PIL import Image
from os.path import dirname, abspath, join, splitext, basename
from os import system
from random import randint

ROOT = dirname(abspath(__file__))

if __name__ == '__main__':
  set_gflags()
  wnid_dir = join(ROOT, 'data/imagenet', FLAGS.wnid)
  cropped_dir = join(wnid_dir, 'images/cropped')
  print cropped_dir
  system('mkdir -p ' + cropped_dir)
  count = 0
  with open(join(wnid_dir, 'bounding_boxes.csv')) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
      for i in range(1, len(row), 4):
        count += 1
        if count % 100 == 0:
          print count
        filename = row[0]
        image = Image.open(filename)
        width, height = image.size
        name, _ = splitext(basename(filename))
        image.crop(get_crop_box(row, i, width, height)
           ).save(join(cropped_dir, name) + '_' + str(int(i/4)) + '.jpg')

