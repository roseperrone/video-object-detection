'''
  Detection and classification use the 19-layer neural net from:
    Very Deep Convolutional Networks for Large-Scale Image Recognition
    K. Simonyan, A. Zisserman
    arXiv:1409.1556
  You can find information about this neural net here:
    https://gist.github.com/ksimonyan/3785162f95cd2d5fee77#file-readme-md
'''
from os.path import dirname, abspath, basename, join
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

from config import TOP_PERCENTAGE

ROOT = dirname(abspath(__file__))


def where_is_noun_in_video(video_id, wnid):
  '''
  Returns:
    a list of tuples of video segments in which that noun appears,
    in seconds. e.g. [(14.4, 20.2), (34.2, 89.2)]
  '''
  # TODO change 10,000 to 1,000 after the full pipeline works
  url = video_url(video_id)
  video_filename = fetch_video(url)
  image_dir = get_prepared_images(url, 10000, video_filename, wnid)
  wnid_dir = join(ROOT, 'data/imagenet', wnid)
  detections_filename = detect(image_dir, '/tmp/bvlc_detection_results.bin')

    #join(wnid_dir, 'aux/snapshots/snapshots_iter_1000.caffemodel'),
    #join(wnid_dir, 'aux/deploy.prototxt'))
  # detections_filename = '/tmp/detection_results.bin'
  draw_detection_results(detections_filename,
    join(ROOT, 'data/imagenet', wnid, 'annotated', basename(image_dir)))

def show_nouns_in_videos(num_videos_per_noun):
  '''
  Run tail -f /tmp/detector_log.txt to see progress.
  '''
  log_filename = '/tmp/detector_log.txt'
  with open(log_filename, 'a') as f:
    for noun_id, video_id_list in get_noun_ids_and_video_ids(
                        num_videos_per_noun).iteritems():
      for i, video_id in enumerate(video_id_list):
        where_is_noun_in_video(video_id, noun_id)
        f.write(' '.join([str(datetime.now()),
                          noun_id,
                          video_id,
                          str(i) + '/' + str(num_videos_per_noun) + '\n',
                         ]))
        f.flush()

def test_classification(image_filename, wnid):
  '''
  Classifies one BGR image and shows the results
  '''
  # TODO this is out of date
  predictions = classify(image_filename)
  image = np.asarray(Image.open(
    draw_classifier_results(predictions, wnid, image_filename)))
  Image.fromarray(image).save(
    'data/labelled-test-images/' + basename(image_filename))
  show_image(image)

def test_classification_of_bananas():
  image_that_contains_bananas = '/Users/rose/video-object-detection/' + \
                                'data/images/9uddKYGPEkg_10000/30000.jpg'

  # the same image above, but cropped to contain only bananas
  image_that_contains_only_bananas = '/Users/rose/' + \
    'video-object-detection/data/test-images/bananas_only_30000.jpg'

  images = [image_that_contains_bananas,
            image_that_contains_only_bananas]

  for image in images:
    test_classification(image, 'banana')

def test_image_annotator():
  # set the TOP_PERCENTAGE to 0.005 to not detect the noun
  # set the TOP_PERCENTAGE to 0.01 to detect the noun
  draw_detector_results('/tmp/detection_results.bin',
    'zPN6ec7SevU_10000_n02965783',
    'n02965783')

def test_detector_on_eggs():
  video_ids = get_egg_video_ids(10)
  for video_id in video_ids:
    where_is_noun_in_video(video_id, 'n07840804')

if __name__ == '__main__':
  test_detector_on_eggs()
