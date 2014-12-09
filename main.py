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
from models import MODELS

import gflags
from gflags import FLAGS
from flags import set_gflags

gflags.DEFINE_string('model', None, 'The name of the model in'
  ' models.py to use to detect objects')
gflags.MarkFlagAsRequired('model')
gflags.DEFINE_integer('ms_between_frames', 10000, 'The number of milliseconds'
  ' between frames in each video')

ROOT = dirname(abspath(__file__))

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
  if video_filename is None:
    print video_id, 'skipped'
    return
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
    detect(image_dir, detections_filename,
           MODELS[FLAGS.model][0], MODELS[FLAGS.model][1])
  else:
    print detections_filename, 'already exists'
  if not exists(detections_filename):
    print 'Something went wrong during detection'
    sys.exit(1)
  draw_detection_results(detections_filename, annotated_dir)

def test_detector_on_eggs():
  # I choose 200 because we have 4 egg queries, and can fetch a maximum
  # of 50 search items (including playlists, channels and video-ids) per
  # query
  video_ids = get_egg_video_ids(200)
  for video_id in video_ids:
    draw_noun_detections_on_video_frames(video_id, 'n07840804')

if __name__ == '__main__':
  set_gflags()
  test_detector_on_eggs()
