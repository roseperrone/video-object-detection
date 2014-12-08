'''
This script lets you run object detection using your choice of trained
caffe model, on video frames of YouTube videos, fetched from YouTube
by search query. The bounding boxes of detection results are drawn.

Usage:
  Train a model according to the instructions in the README.md
  Add your model to MODELS.
  Run this script. in addition to the flags in this script, you can
  also change a few parameters in config.py.
'''
from os.path import dirname, abspath, basename, join, exists
from os import system
import sys
from PIL import Image
import numpy as np
from datetime import datetime

from video_id_fetcher import (get_noun_ids_and_video_ids,
                              get_egg_video_ids)
from video_fetcher import video_url, fetch_video
from image_utils import get_prepared_images
from classifier import classify
from detector import detect
from image_annotator import draw_detection_results
from image_utils import show_image

import gflags
from gflags import FLAGS
from flags import set_gflags

gflags.DEFINE_string('model', 'nin-high-neg', 'The name of the model in MODELS to'
  ' use to detect objects')
gflags.DEFINE_integer('ms_between_frames', 10000, 'The number of milliseconds'
  ' between frames in each video')

ROOT = dirname(abspath(__file__))

# The key is the trained model name, and the value is a tuple containing:
#   - a path to the caffemodel
#   - a path to the deploy.prototxt of the trained model
MODELS = {
  # Accuracy per test iteration:
  #  0:    0.904
  #  2000: 0.976
  #  4000: 0.970
  #  6000: 0.965
  # I stopped training this at iteration 7000
  # lr = 0.01
  'alexnet': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/alexnet/snapshots/snapshot_iter_6000.caffemodel',
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/alexnet/aux/deploy.prototxt'
  ),

  # Accuracy per test iteration:
  #  0:    0.738
  #  1500: 0.944
  #  3000: 0.953
  #  4500: 0.979
  #  6000: 0.981
  # lr = 0.001. When I trained with 0.01, the loss remained constant at 0.63
  'nin-equal': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/nin-equal/snapshots/snapshot_iter_6500.caffemodel',
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/nin-equal/aux/deploy.prototxt'
  ),
  # I stopped training this at iter 6500
  # I judged predictions on 10 videos and computed this accuracy:
  #   precision: 0.282051282051
  #   recall: 0.22


  # Note that I accidentally wrote the snapshots for this model to nin-equal,
  # I just have to keep an eye on it during training and move the snapshots.
  # Accuracy per test iteration:
  #  0:    0.910
  #  1000: 0.908
  #  2000: 0.919
  #  3000: 0.931
  #  4000: 0.934
  #  5000: 0.951
  #  6000: 0.9524
  #  7000: 0.9518
  #  8000: 0.954
  #  9000: 0.952
  # lr = 0.001. When I trained with 0.01, the loss remained constant at 0.63
  'nin-high-neg': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/nin-high-neg/snapshots/snapshot_iter_9000.caffemodel',
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/nin-high-neg/aux/deploy.prototxt'
  ),
  # The data skew caused the predictions for the negative class to be all 0s.
  # A similar skew happened before with this NIN model, when an LMDB bug caused
  # me to have way more positive training images than negative training images.
  # In that situation, the positive class had pred[0], pred[1] scores like this:
  # 0.0 10.1965
  # 0.0 89.606
  # 0.0 15.007
  # 0.0 8.72097
  # 0.0 27.801
  # 0.0 55.6223
  #
  # and in this situation of having a 10:1 negative:positive training images ratio,
  # pred[0], pred[1] scores look like this:
  # 11.9817 0.0
  # 8.1218 0.0
  # 13.3314 0.0
  # 6.01843 0.0
  # 10.6878 0.0
  # 15.3691 0.0
  # 18.2615 0.0
  # I'll keep equal numbers of negative and positive training images
  # in the future. It's curious, though, that the test accuracy was steadily
  # improving. I'm sure I'm training on the correct model, because this is
  # the first model I've trained up to iteration 9000.
  #

  # This model uses an equal neg:pos train ratio. I also removed all images from
  # the positive set except clean, white, mostly-unobscured chicken eggs.
  # I also changed the neg:pos test ratio to 8.
  # Accuracy per test iteration:
  #  0:
  #

  'bvlc-reference-finetuned': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/bvlc-reference-finetuned/snapshots/snapshot_iter_xxxx.caffemodel',
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/bvlc-reference-finetuned/aux/deploy.prototxt'
  ),

  # then maybe finetune nin

}

def draw_noun_detections_on_video_frames(video_id, wnid):
  '''
  Draws boxes of detections of <wnid> on the frames of the video.
  The boxes have been non-maximally suppressed.

  Because selective search provides about 2000 boxes per frame, and the noun
  usually isn't even present, I don't consider a detection positive if the score
  for the positive class is higher than the negative class. Instead, I
  consider a detection positive if the positive score is > 0.99 (out of 1.00)

  If you want to change the drawing code, but not have to rerun the detection,
  simply delete the directory of annotated images you want to redraw (found in
  the data/imagenet/<wnid>/annotated directory)

  The names of the annotated directories take this form:
    <model>_<video_id>_<ms_betwen_frames>
  '''
  url = video_url(video_id)
  video_filename = fetch_video(url)
  image_dir = get_prepared_images(url, FLAGS.ms_between_frames,
                                  video_filename, wnid)
  wnid_dir = join(ROOT, 'data/imagenet', wnid)
  annotated_dir = join(dirname(dirname(MODELS[FLAGS.model][0])),
                       'annotated', basename(image_dir))
  if exists(annotated_dir):
    print 'The annotated dir for ' + video_id + ' already exists'
    return
  system('mkdir -p ' + annotated_dir)

  detections_filename = join('/tmp',
    '_'.join(['detection', 'results', FLAGS.model, wnid, video_id]) + '.bin')
  if not exists(detections_filename):
    print detections_filename, 'does not already exist'
    detect(image_dir, detections_filename, MODELS[FLAGS.model][0], MODELS[FLAGS.model][1])
  else:
    print detections_filename, 'already exists'
  if not exists(detections_filename):
    print 'Something went wrong during detection'
    sys.exit(1)
  draw_detection_results(detections_filename, annotated_dir)

def test_detector_on_eggs():
  video_ids = get_egg_video_ids(10)
  for video_id in video_ids:
    draw_noun_detections_on_video_frames(video_id, 'n07840804')

if __name__ == '__main__':
  set_gflags()
  test_detector_on_eggs()
