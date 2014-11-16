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

import csv
from PIL import Image
from os.path import dirname, abspath, join, exists, splitext, basename
from os import system

ROOT = dirname(abspath(__file__))

def absolute_dimensions(box, image):
  'Converts dimension percentages to absolute int values'

  return (int(SIZE * box[0]),
          int(SIZE * box[1]),
          int(SIZE * box[2]),
          int(SIZE * box[3]))

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
        # in the csv, each bounding box dimensions is a percentage of the
        # image size
        crop_box = (int(float(row[i]) * width),    # left
                    int(float(row[i+1]) * height), # top
                    int(float(row[i+2]) * width),  # right
                    int(float(row[i+3]) * height)) # bottom
        # Depending on the order in which the dots were drawn (upper left
        # first or bottom left), the dimensions might be swapped. The
        # following code rectifies this.
        left = min(crop_box[0], crop_box[2])
        top = min(crop_box[1], crop_box[3])
        right = max(crop_box[0], crop_box[2])
        bottom = max(crop_box[1], crop_box[3])

        crop_box = left, top, right, bottom

        name, _ = splitext(basename(filename))
        try:
          image.crop(crop_box).save(join(cropped_dir, name) \
                 + '_' + str(int(i/4)) + '.jpg')
        except SystemError as e:
          print count
          print e
          print 'image.size:', image.size
          print 'crop_box:', crop_box
