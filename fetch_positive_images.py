'''
After running this script, you'll be able to find the fetched images
in data/imagenet-images/<wnid>/
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

from imagenet_image_fetcher import download_images

# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
                     'The wordnet id of the noun in the positive images')

if __name__ == '__main__':
  set_gflags()
  download_images(FLAGS.wnid)
