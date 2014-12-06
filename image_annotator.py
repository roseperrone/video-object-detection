from os.path import dirname, basename, join, splitext
from os import system, listdir
from collections import defaultdict
from PIL import Image
import numpy as np
import cv2

from imagenet import top_boxed_scores, get_description
from nms import get_boxes
from image_utils import convert_bgr_to_rgb
from performance import timeit
from config import TOP_PERCENTAGE


@timeit
def draw_detection_results(detection_output_filename, target_dir):
  print detection_output_filename
  print target_dir

  # boxed_scores =  # _find_boxes_containing_noun(wnid,
  boxes = get_boxes(detection_output_filename)
  draw_boxes(boxes, target_dir)

def _find_boxes_containing_noun(wnid, labelled_boxes):
  found = defaultdict(list)
  for image_filename, boxes in labelled_boxes.iteritems():
    for i, tup in enumerate(boxes):
      xmin, xmax, ymin, ymax, wnids, scores = tup
      for index, id in enumerate(wnids):
        if wnid == id:
          found[image_filename].append(
            (xmin, xmax, ymin, ymax, wnid, scores[index]))
    if len(found[image_filename]) == 0:
      found[image_filename].append(None)
  return found

def draw_boxes(boxes, target_dir):
  system('rm -rf ' + target_dir)
  system('mkdir -p ' + target_dir)

  for image_filename, bs in boxes.iteritems():
    cmd = 'convert ' + convert_bgr_to_rgb(image_filename)
    cmd += ' -fill none -stroke chartreuse -strokewidth 2'
    for xmin, ymin, xmax, ymax, score in bs:
      cmd += (' -draw "rectangle %s,%s,%s,%s" ' %
                (int(xmin), int(ymin), int(xmax), int(ymax)))
    target = join(target_dir, splitext(basename(image_filename))[0] + '.jpg')
    cmd += ' ' + target
    print cmd
    system(cmd)

def _draw_box(image_filename, window_id, coordinates, target_dir):
  xmin, xmax, ymin, ymax, score = coordinates
  cmd = 'convert ' + convert_bgr_to_rgb(image_filename)
  cmd += ' -fill none -stroke chartreuse -strokewidth 2'
  cmd += (' -draw "rectangle %s,%s,%s,%s" ' %
            (int(xmin), int(ymin), int(xmax), int(ymax)))
  #cmd += ' -pointsize 17 -fill chartreuse'
  #text = 'Score:' + "{:.2f}".format(score)
  #cmd += ' -draw "text 20%%,20%% \'%s\'"' % text
  target = join(target_dir,
                '_'.join([splitext(basename(image_filename))[0],
                          str(window_id) + '.jpg']))
  cmd += ' ' + target
  print cmd
  system(cmd)

def _mean_scores(labelled_boxes):
  '''
  Finds the mean score per frame, averaged over all the scores
  of each windowed detection on that frame.
  '''
  totals = defaultdict(int)
  counts = defaultdict(int)
  for image_filename, boxes in labelled_boxes.iteritems():
    if boxes[0] is None:
      continue
    for box in boxes:
      totals[image_filename] += box[5]
      counts[image_filename] += 1

  means = defaultdict(int)
  for image_filename, total in totals.iteritems():
    if counts[image_filename] == 0:
      means[image_filename] = 0
    else:
      means[image_filename] = total / float(counts[image_filename])

  return means

def write_video(image_dir):
  '''
  Writes a video from a set of images in `image_dir`
  '''
  target = join('data/labelled-videos',
                basename(image_dir) + '.mp4v')
  codec = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
  size = (256, 256)
  fps = 16
  actual_frames_per_second = 0.5
  v = cv2.VideoWriter(target, codec, fps, size)
  for image_name in listdir(image_dir):
    image_filename = join(image_dir, image_name)
    arr = np.asarray(Image.open(image_filename))
    assert arr.shape[:2] == size
    for i in range(int(fps/actual_frames_per_second)):
      v.write(arr[:, :, (2, 1, 0)]) # convert RGB to BGR, the opencv standard
