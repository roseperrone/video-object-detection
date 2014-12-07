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


def draw_detection_results(detection_output_filename, target_dir):
  boxes = get_boxes(detection_output_filename)

  system('rm -rf ' + target_dir)
  system('mkdir -p ' + target_dir)

  for image_filename, bs in boxes.iteritems():
    cmd = 'convert ' + convert_bgr_to_rgb(image_filename)
    cmd += ' -fill none -stroke chartreuse -strokewidth 2'
    for xmin, ymin, xmax, ymax, score in bs:
      cmd += (' -draw "rectangle %s,%s,%s,%s" ' %
                (int(xmin), int(ymin), int(xmax), int(ymax)))
      # Text drawing code strangely doesn't work on my machine.
      # See the question I posted on SO:
      # http://stackoverflow.com/questions/27324930/convert-non-conforming-drawing-primitive-definition-text/27332225#27332225
      #cmd += ' -pointsize 17 -fill chartreuse'
      #text = 'Score:' + "{:.2f}".format(score)
      #cmd += ' -draw "text 20%%,20%% \'%s\'"' % text
    target = join(target_dir, splitext(basename(image_filename))[0] + '.jpg')
    cmd += ' ' + target
    print cmd
    system(cmd)

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
