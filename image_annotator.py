from os.path import dirname, basename, join, splitext
from os import system, listdir
from collections import defaultdict
from PIL import Image
import numpy as np
import cv2

from imagenet import top_labels, boxes_and_top_labels
from image_utils import convert_bgr_to_rgb
from performance import timeit


def draw_image_labels(image_filename, labels):
  '''
  Converts the image from BGR to RGB, draws the labels on the image.
  Returns the new image filename.
  '''
  text = '\n'.join(labels)
  target_parent = join('data/labelled-images',
                       basename(dirname(image_filename)))
  system('mkdir -p '+ target_parent)
  target = join(target_parent, basename(image_filename))
  cmd = ' '.join(
    ['convert ' + convert_bgr_to_rgb(image_filename),
     '-pointsize 14 -fill green ',
     '-draw "text 20%%,20%% \'%s\'"' % text,
     target])
  system(cmd)
  return target

def draw_boxes(labelled_boxes, image_dir_name):
  target_dir = join('data/boxed-images', image_dir_name)
  system('mkdir -p ' + target_dir)
  for image_filename, boxes in labelled_boxes.iteritems():
    for i, tup in enumerate(boxes):
      xmin, xmax, ymin, ymax, labels = tup
      target = join(target_dir,
                    splitext(basename(image_filename))[0] + '_' + \
                    str(i) + '.jpg')
      cmd = 'convert ' + convert_bgr_to_rgb(image_filename)
      if not (xmin == 0 and ymin == 0 and xmax == 0 and ymax == 0):
        cmd += ' -fill none -stroke green -strokewidth 2'
        cmd += (' -draw "rectangle %s,%s,%s,%s" ' %
                  (int(xmin), int(ymin), int(xmax), int(ymax)))
      cmd += ' -pointsize 14 -fill green '
      cmd += ' -draw "text 20%%,20%% \'%s\'"' % '\n'.join(labels)
      cmd += ' ' + target
      print cmd
      system(cmd)

def draw_classifier_results(predictions, noun, image_filename):
  top_100_labels, top_100_score_mean = top_labels(predictions, 100)
  matching_label = [label for label in top_100_labels if noun in label]
  label = '' if len(matching_label) == 0 else matching_label[0]
  labels = [label, "{0:.4f}".format(top_100_score_mean) + ' Top 10% mean']
  print '\n'.join(labels)
  return draw_image_labels(image_filename, labels)

@timeit
def draw_detector_results(output_filename, image_dir_name, noun):
  labelled_boxes = boxes_and_top_labels(output_filename, 100)
  boxes_containing_noun = _find_boxes_containing_noun(labelled_boxes, noun)
  draw_boxes(boxes_containing_noun, image_dir_name)

def _find_boxes_containing_noun(labelled_boxes, noun):
  found = defaultdict(list)
  for image_filename, boxes in labelled_boxes.iteritems():
    for i, tup in enumerate(boxes):
      xmin, xmax, ymin, ymax, labels = tup
      for label in labels:
        if noun in label: # FIXME: egg is not eggnog.
          found[image_filename].append((xmin, xmax, ymin, ymax, [label]))
    if len(found[image_filename]) == 0:
      found[image_filename].append((0, 0, 0, 0, ['Not found']))
  return found

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
