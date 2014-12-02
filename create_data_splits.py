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
  `all-positive-cropped` rather than `all-positive-uncropped`

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

This script works by computing all counts for pos/neg train/test sets based
on the size of the `all-positive-cropped` dir.
Then it downloads all the negative images needed to the `all-negative` dir.
Then it symlinks the proper numbers of images to these directories, which
are created in data/imagenet/<wnid>/images/<dataset>:
  train-positive
  train-negative
  test-positive
  test-negative
  train
  test
The purpose for the train-X and test-X files is just visualization. It's of course
possible to create `train` and `test` without them.
Then this script writes train.txt and test.txt in the dataset directory.
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
                     'The wordnet id of the noun in the positive images')
# Useful for training on datasets with different positive/negative ratios
gflags.DEFINE_string('dataset', None, 'The name of the directory that contains '
                     'the test and train image directories, as well as the '
                     'train.txt and test.txt files')
gflags.MarkFlagAsRequired('dataset')

# I have 2281 cropped images for n07840804 (eggs) (I didn't draw bounding
# boxes for all of the images).
# This ratio default is used in
# http://people.csail.mit.edu/torralba/publications/datasets_cvpr11.pdf
# "For detection the number of negatives is naturally much larger and
# more diverse".
# Note: For eggs, I didn't meet this ratio of 10, because I cut the
# negative image downlaoding short, so I actually use a ratio of 7.6
# (17280 negative train images)
#gflags.DEFINE_integer('negative_to_positive_train_ratio', 10, '')
gflags.DEFINE_integer('negative_to_positive_train_ratio', 1, '')
# 2000 ideally, but I'm going for speed right now:
#gflags.DEFINE_integer('negative_to_positive_test_ratio', 50, '')
gflags.DEFINE_integer('negative_to_positive_test_ratio', 10, '')
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
  Directories created in data/imagenet/<wnid>/images/<dataset>:
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

  These two files are created in data/imagenet/<wnid>/images/<dataset>:
    train.txt
    test.txt
  '''

  wnid_dir = join(ROOT, 'data/imagenet', FLAGS.wnid)
  images_dir = join(wnid_dir, 'images')
  all_negative_images_dir = join(images_dir, 'all-negative')
  dataset_dir = join(images_dir, FLAGS.dataset)
  positive_images_train_dir = join(dataset_dir, 'train-positive')
  negative_images_train_dir = join(dataset_dir, 'train-negative')
  positive_images_test_dir = join(dataset_dir, 'test-positive')
  negative_images_test_dir = join(dataset_dir, 'test-negative')
  train_dir = join(dataset_dir, 'train')
  test_dir = join(dataset_dir, 'test')
  system('mkdir -p ' + positive_images_train_dir)
  system('mkdir -p ' + negative_images_train_dir)
  system('mkdir -p ' + positive_images_test_dir)
  system('mkdir -p ' + negative_images_test_dir)
  system('mkdir -p ' + train_dir)
  system('mkdir -p ' + test_dir)

  cropped_dir = join(images_dir, 'all-positive-cropped')
  if exists(cropped_dir):
    all_positive_images_dir = cropped_dir
  else:
    all_positive_images_dir = join(images_dir, 'all-positive-uncropped')

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

  num_negative_images = num_negative_train_images + num_negative_test_images

  download_negative_images(FLAGS.wnid, num_negative_images,
                           all_negative_images_dir)

  symlink(all_positive_images_dir,
          positive_images_train_dir,
          positive_images_test_dir,
          num_positive_train_images,
          num_positive_test_images)
  symlink(all_negative_images_dir,
          negative_images_train_dir,
          negative_images_test_dir,
          num_negative_train_images,
          num_negative_test_images)

  create_category_files('train')
  create_category_files('test')

def symlink(all_dir, train_dir, test_dir, train_count, test_count):
  '''
  FIXME: do I need to sanitize the filenames? I got like 500 of these errors:

  ln: 1.jpg: No such file or directory
  ln: hemlock.jpg: No such file or directory
  ln: littoralis_thumb.jpg: No such file or directory
  ln: matricariifolium.JPG: No such file or directory
  ln: phalloides-1.jpg: No such file or directory
  ln: tomato.jpg: No such file or directory
  ln: Kuznik.jpg: No such file or directory
  sh: -c: line 0: syntax error near unexpected token `('
  sh: -c: line 0: `ln -s /Users/rose/home/video-object-detection/data/imagenet/n07840804/images/train-negative/n13003522_275px-Amanita_rubescens_(2).JPG /Users/rose/home/video-object-detection/data/imagenet/n07840804/images/train/n13003522_275px-Amanita_rubescens_(2).JPG'
  ln: DW.jpg: No such file or directory
  ln: 21968.jpg: No such file or directory
  ln: 3.JPG: No such file or directory
  ln: 0.jpg: No such file or directory
  ln: betulinus.jpg: No such file or directory
  ln: peckii7.jpg: No such file or directory
  ln: ovovillus.JPG: No such file or directory
  ln: luridus.jpg: No such file or directory
  ln: Parker.jpg: No such file or directory
  ln: Beug.jpg: No such file or directory
  '''
  num_linked = 0
  for name in listdir(all_dir):
    if num_linked < train_count:
      system('ln -s "' + join(all_dir, name) + '" ' + train_dir)
      system('ln -s "' + join(all_dir, name) + '" ' + \
        join(ROOT, 'data/imagenet', FLAGS.wnid, 'images', FLAGS.dataset, 'train'))
    elif num_linked < train_count + test_count:
      system('ln -s "' + join(all_dir, name) + '" ' + test_dir)
      system('ln -s "' + join(all_dir, name) + '" ' + \
        join(ROOT, 'data/imagenet', FLAGS.wnid, 'images', FLAGS.dataset, 'test'))
    else:
      return
    num_linked += 1

def create_category_files(stage):
  '''
  `stage` is either 'train' or 'test'

  The original positive images are in train-positive or test-positive.
  The original negative images are in train-negative or test-negative.

  train/ and test/ contain symlinks from both positive and negative images.

  Therefore I use train and test as the filenames in the category files, but
  I use the [train, test]-[positive-negative] directories to determine whether
  the filename should be followed with a 0 or 1.

  I also create image-data-train.txt and image-data-test.txt, because
  the IMAGE_DATA layer requires full pathnames rather than just basenames,
  which LMDB requires (for a DATA layer in the net).
  '''
  wnid_dir = join(ROOT, 'data/imagenet', FLAGS.wnid)
  positive_dir = join(wnid_dir, 'images', FLAGS.dataset, stage + '-positive')
  negative_dir = join(wnid_dir, 'images', FLAGS.dataset, stage + '-negative')
  with open(join(wnid_dir,'images', FLAGS.dataset, 'image-data-' + stage + '.txt'), 'w') as fi:
    with open(join(wnid_dir,'images', FLAGS.dataset, stage + '.txt'), 'w') as f:
      for name in listdir(positive_dir):
        f.write(name + ' 1\n')
        fi.write(join(positive_dir, name) + ' 1\n')
      for name in listdir(negative_dir):
        f.write(name + ' 0\n')
        fi.write(join(negative_dir, name) + ' 0\n')

if __name__ == '__main__':
  set_gflags()
  create_train_and_test_splits()

