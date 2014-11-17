'''
Positive training images must exist in `data/imagenet/<wnid>/train/positive`

To generate these training images, run:
  python imagenet_image_fetcher.py --wnid=<wnid>
If you want:
  Either:
    a.) manually filter these images using `filter_positive_images.py`
    or
    b.) run `draw_bounding_boxes.py` followed with `bounded_box_cropper.py`,
  in case b, the images will be stored in
  `cropped` rather than `all`
Else:
  rename the `all` dir to `train/positive`

Then run this script.

As in the "Network In Network" paper, splitting of training and vaidation
datasets follows:
Ian J Goodfellow, David Warde-Farley, Mehdi Mirza, Aaron Courville,
and Yoshua Bengio. Maxout networks. arXiv preprint arXiv:1302.4389, 2013.

The negative examples are randomly drawn from other imagenet categories.
There are currently 21841 imagenet categories.
TODO: Use hard (difficult) negative mining by running the detector on
these images and recording which windows the detector misclassifies as
correct.
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
                     'The wordnet id of the noun in the positive images')
gflags.DEFINE_boolean('skip_pos', False, 'Set to True to generate only the'
                      ' negative images and category files, and skip moving'
                      ' the positive images. Useful if this'
                      ' script was interrupted during negative image '
                      ' generation.')
# I have 2281 cropped images for n07840804 (eggs) (I didn't draw bounding
# boxes for all of the images).
# This ratio default is used in
# http://people.csail.mit.edu/torralba/publications/datasets_cvpr11.pdf
# "For detection the number of negatives is naturally much larger and
# more diverse".
gflags.DEFINE_integer('negative_to_positive_train_ratio', 10, '')
# 2000 ideally, but I'm going for speed right now:
gflags.DEFINE_integer('negative_to_positive_test_ratio', 100, '')
# The above ratio default is similar to the number of bounding boxes detected
# via selective search for each image.

# This ratio default is high because I don't use this test
# (validation, really) set to train hyperparamaters, just to judge accuracy.
# Otherwise I'd use 6, as in the
# Maxout Networks paper: arxiv.org/pdf/1302.4389v4.pdf
gflags.DEFINE_integer('train_to_test_ratio', 40, '')

import sys
from glob import glob
from os.path import dirname, abspath, join, exists
from os import listdir, system

from imagenet_image_fetcher import (download_images, download_bounding_boxes,
                                    download_negative_images)

ROOT = dirname(abspath(__file__))


def create_train_and_test_splits():
  '''
  Directories created in data/imagenet/<wnid>/images:
    train-positive
    train-negative
    test-positive
    test-negative
    train # contains links to all images in train-positive and train-negative
    test # contains links to all images in test-positive and test-negative

  This function does not preprocess the images. I let caffe resize the
  images to 256x256.

  caffe needs to know the image categories. It does so by reading a
  text file for each the train set and the test set, of this format:

  /home/my_test_dir/picture-foo.jpg 0
  /home/my_test_dir/picture-foo1.jpg 1

  where picture-foo belongs to category 0 and picture-foo1 belongs
  to category 1 (I call category 1 the positive category).

  These two files are created in data/imagenet/<wnid>:
    train.txt
    test.txt
  '''
  wnid_dir = join(ROOT, 'data/imagenet', FLAGS.wnid)
  images_dir = join(wnid_dir, 'images')
  positive_images_train_dir = join(images_dir, 'train-positive')
  negative_images_train_dir = join(images_dir, 'train-negative')
  positive_images_test_dir = join(images_dir, 'test-positive')
  negative_images_test_dir = join(images_dir, 'test-negative')
  train_dir = join(images_dir, 'train')
  test_dir = join(images_dir, 'test')
  system('mkdir -p ' + positive_images_train_dir)
  system('mkdir -p ' + negative_images_train_dir)
  system('mkdir -p ' + positive_images_test_dir)
  system('mkdir -p ' + negative_images_test_dir)
  system('mkdir -p ' + train_dir)
  system('mkdir -p ' + test_dir)

  cropped_dir = join(images_dir, 'cropped')
  if exists(cropped_dir):
    all_positive_images_dir = cropped_dir
  else:
    all_positive_images_dir = join(images_dir, 'all')

  if not exists(all_positive_images_dir):
    print 'The positive_images_train_dir must be populated with images'
    sys.exit(1)

  num_positive_images = \
    len(glob(join(all_positive_images_dir, '*.[Jj][Pp][Gg]')))

  num_positive_test_images = \
    int(num_positive_images / (1 + FLAGS.train_to_test_ratio))

  num_positive_train_images = num_positive_images - num_positive_test_images

  num_negative_train_images = \
    FLAGS.negative_to_positive_train_ratio * num_positive_train_images

  num_negative_test_images = \
    num_positive_test_images * FLAGS.negative_to_positive_test_ratio

  if not FLAGS.skip_pos:
    num_moved = 0
    for name in listdir(all_positive_images_dir):
      if num_moved < num_positive_train_images:
        system('cp ' + join(all_positive_images_dir, name) + ' ' + \
               positive_images_train_dir)
      else:
        system('cp ' + join(all_positive_images_dir, name) + ' ' + \
               positive_images_test_dir)
      num_moved += 1

  download_negative_images(FLAGS.wnid, num_negative_train_images,
                      negative_images_train_dir)
  download_negative_images(FLAGS.wnid, num_negative_test_images,
                      negative_images_test_dir)

  print 'All done!'
  import pdb; pdb.set_trace()
  # ImageNet expects all train images to be in one directory,
  # and likewise the test images.
  # I wait until now to do it for debugging and visualization purposes
  link_positive_and_negative_images_to_one_dir('train')
  import pdb; pdb.set_trace()
  link_positive_and_negative_images_to_one_dir('test')
  import pdb; pdb.set_trace()

  create_category_files('train')
  create_category_files('test')

def create_category_files(stage):
  '''
  `stage` is either 'train' or 'test'
  '''
  wnid_dir = join(ROOT, 'data/imagenet', FLAGS.wnid)
  positive_dir = join(wnid_dir, stage, 'positive')
  negative_dir = join(wnid_dir, stage, 'negative')
  with open(join(wnid_dir, stage + '.txt'), 'w') as f:
    for name in listdir(positive_dir):
      f.write(join(positive_dir, name) + ' 1\n')
    for name in listdir(negative_dir):
      f.write(join(negative_dir, name) + ' 0\n')

def link_positive_and_negative_images_to_one_dir(stage):
  images_dir = join(ROOT, 'data/imagenet', FLAGS.wnid, 'images')
  positive_dir = join(images_dir, stage + '-positive')
  negative_dir = join(images_dir, stage + '-negative')
  dst_dir = join(images_dir, stage)
  for name in listdir(positive_dir):
    system('ln -s ' + join(positive_dir, name) + dst_dir)
  for name in listdir(negative_dir):
    system('ln -s ' + join(negative_dir, name) + dst_dir)


if __name__ == '__main__':
  set_gflags()
  create_train_and_test_splits()


