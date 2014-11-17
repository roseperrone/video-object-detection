
import datetime
import csv
from PIL import Image
from os.path import dirname, abspath, join
from random import randint

ROOT = dirname(abspath(__file__))

def get_crop_box(row, offset, width, height):
  '''
  Arguments:
    row:    a row of the bounding_boxes.txt csv
    offset: at which token index the bounding box values begin for a
            certain bounding box. The csv row contains a bounding box
            followed by the box dimensions, measured in the percentage
            of the image size
    width:  width of the original image
    height: height of the original image
  '''
  # in the csv, each bounding box dimensions is a percentage of the
  # image size
  box = (int(float(row[offset]) * width),    # left
         int(float(row[offset+1]) * height), # top
         int(float(row[offset+2]) * width),  # right
         int(float(row[offset+3]) * height)) # bottom
  # Depending on the order in which the dots were drawn (upper left
  # first or bottom left), the dimensions might be swapped. The
  # following code rectifies this.
  left = min(box[0], box[2])
  top = min(box[1], box[3])
  right = max(box[0], box[2])
  bottom = max(box[1], box[3])

  return left, top, right, bottom

def crop_image_randomly(positive_wnid, src_image_filename, dst_image_filename):
  '''
  Arguments:
    positive_wnid:      the wordnet id of the noun in positive images
    src_image_filename: the image to crop
    dst_image_filename: the cropped image is placed here
  Returns:
    True on success, False on failure

  The negative images are cropped by a random crop_box in
  `imagenet/<wnid>/bounding_boxes.csv`, because the positive images
  are, and are therefore often more zoomed-in than the typical
  imagenet photo.

  If an original image doesn't have bounding boxes, that means the noun
  was not found in the image.
  '''
  wnid_dir = join(ROOT, 'data/imagenet', positive_wnid)
  found = False
  with open(join(wnid_dir, 'bounding_boxes.csv')) as csvfile:
    rows = [row for row in list(csv.reader(csvfile)) if len(row) >= 5]
    row = rows[randint(0, len(rows) - 1)]
    try:
      image = Image.open(src_image_filename)
    except IOError as e:
      # If the image is corrupt, it raises this error:
      # IOError: cannot identify image file
      print e
      return False
    width, height = image.size
    if len(row) == 5:
      box_index = 1
    else:
      box_index = 1 + 4*randint(0, (len(row) - 1)/4 - 1)
    try:
      crop_box = get_crop_box(row, box_index, width, height)
      image.crop(crop_box).save(dst_image_filename)
    except IOError as e:
      # A workaround for "IOError: cannot write mode P as JPEG"
      try:
        crop_box = get_crop_box(row, box_index, width, height)
        image.crop(crop_box).convert('RGB').save(dst_image_filename)
      except SystemError as e:
        log_error(e, width, height, crop_box)
        return False
    except SystemError as e:
      log_error(e, width, height, crop_box)
      return False
  return True

def log_error(e, width, height, crop_box):
  with open('/tmp/crop_error_log.txt', 'a') as f:
    f.write('\n'.join(['time: ' + str(datetime.datetime.now()),
                       'error: ' + str(e),
                       'width: ' + str(width),
                       'height: ' + str(height),
                       'crop_box: ' + str(crop_box)]))
