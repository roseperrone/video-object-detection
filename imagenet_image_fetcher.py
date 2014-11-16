'''
First, search ImageNet for the noun. Click on Downloads,
and then click Download URLs of images in the synset. Copy this text to
data/image-urls/<wnid>.txt

Then run `python imagenet_image_fetcher.py <wnid>`. You'll be able to find
the fetched images in data/imagenet-images/<wnid>/

As in the "Network In Network" paper, splitting of training and vaidation
datasets follows:
Ian J Goodfellow, David Warde-Farley, Mehdi Mirza, Aaron Courville,
and Yoshua Bengio. Maxout networks. arXiv preprint arXiv:1302.4389, 2013.

The negative examples are randomly drawn from other imagenet categories.
There are currently 21841 imagenet categories.
TODO: Use hard (difficult) negative mining by running the detector on
these images and recording which windows the detector misclassifies as
correct.

Positive training examples are the image cropped to the bounding box.
No resizing to 256x256 is done. I let caffe do that. Note that these images (usually)
must be manually looked at to select a subtype of the noun if you
want a subtype. For example, I want to only collect pictures of whole eggs,
not open eggs, so I run `filter_positive_images.py`.

Perhaps a better method is to use windows from positive images that do not
contain the image. The negative-mining method will change when the time comes.
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
                     'The wordnet id of the noun in the positive images')

from os.path import dirname, abspath, join, exists
from os import system

ROOT = dirname(abspath(__file__))

def bounding_boxes_are_available_for_this_noun(wnid):
  '''
  It turns out the sets of bounding boxes are too incomplete for use,
  so I wrote a Pygame to manually draw the bounding boxes.

  Bounding boxes are only available for the 300 synsets (out of the current
  21841 total synsets on ImageNet)

  Here is the list of synsets with bounding boxes.
  http://www.image-net.org/api/text/imagenet.bbox.obtain_synset_list
  '''
  bbox_synset_list_filename = join(ROOT, 'data/imagenet_bbox_synset_list')
  system('wget http://www.image-net.org/api/text/'
         'imagenet.bbox.obtain_synset_list '
         '-O ' + bbox_synset_list_filename)
  with open(bbox_synset_list_filename) as f:
   return wnid + '\n' in list(f)

def get_one_random_image(wnid, target_dir):
  '''
  Downloads a random image identified by the synset id, and places it in
  `target_dir`

  Given the wnid of a synset, the URLs of its images can be obtained at
  http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=[wnid]
  '''
  pass

def download_images(wnid):
  '''
  Downloads all images identified by the synset id, and places them in
  `target_dir`

  Returns:
    the number of images placed in `target_dir`

  Given the wnid of a synset, the URLs of its images can be obtained at
  http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=[wnid]
  '''
  images_dir = join(ROOT, 'data/imagenet', FLAGS.wnid, 'images/all')
  system('mkdir -p ' + images_dir)
  tmp = '/tmp/image_urls.txt'
  system('wget http://www.image-net.org/api/text/'
         'imagenet.synset.geturls?wnid=' + FLAGS.wnid + ' -O ' + tmp)
  with open(tmp) as f:
    for line in f:
      image_url = line[:-2] # strip trailing '\r\n'
      system('wget ' + image_url + ' --directory-prefix=' + images_dir)

def download_bounding_boxes(wnid):
  '''
  You can use the following API to download the bounding boxes of a
  particular synset:
  http://www.image-net.org/api/download/imagenet.bbox.synset?wnid=[wnid]

  The number of bounding boxes per image is way too small to be useful...
  like 10% and the mapping between image and "annotation" seems unclear

  And that endpoint above doesn't actually work. I emailed
  the imagenet list about it. The endpoint that does work is:
  "You can download all the bounding boxes available packaged in one file:
  http://image-net.org/Annotation/Annotation.tar.gz"

  I await an email to see if I'll need to write a pygame for bounding
  the boxes. I've done it before, so it should be quick...

  Well hey, if I can draw bounding boxes in six seconds per image on
  average, it'll take two hours. I can handle that...
  haha unfortunately for eggs, there are often several (like 20) eggs
  per image. It takes much longer.
  '''
  pass

def download_negative_images(wnid, count, target_dir):
  '''
  Downloads `count` random images from imagenet that have any wnid other than
  `wnid', and place them in `target_dir`.
  '''
  pass

def all_wnids():
  '''
  Returns all wnids for which ImageNet has images

  The list of all wordnet ids (which identify the synsets) is at:
  http://www.image-net.org/api/text/imagenet.synset.obtain_synset_list
  '''
  pass

if __name__ == '__main__':
  set_gflags()
  download_images(FLAGS.wnid)
