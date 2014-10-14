'''
Utility methods for downloading and preparing video frames.
'''
from os.path import dirname, abspath, exists, splitext, basename, join
from os import system, listdir
from PIL import Image
import numpy as np
import cv2
import re
import pafy
import shelve
import pylab
import tempfile

import pdb

ROOT = dirname(abspath(__file__))
IMAGE_MEAN = [103.939, 116.779, 123.68]

def get_prepared_images(url, ms_between_frames, use_cache=True):
  '''
  Returns:
    The  directory that contains the image frames.
    The image filenames take the format:
      <milliseconds_into_the_video>.jpg
    The directory name is stored in data/images and takes the format:
      <sanitized video url>_<milliseconds_between_frames>

  '''
  image_dir = image_frames_dir(url, ms_between_frames)
  if exists(image_dir):
    if use_cache:
      return image_dir
    else:
      system('rm -rf ' + image_dir)
  system('mkdir -p ' + image_dir)
  video_filename = get_video(url)
  cap = cv2.VideoCapture(video_filename)
  frame_count = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
  frames_per_s = int(cap.get(cv2.cv.CV_CAP_PROP_FPS))

  step = (ms_between_frames / 1000) * frames_per_s
  image_count = 0
  for i in range(frame_count)[::step]:
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, i)
    retval, image = cap.read()
    filename = join(image_dir, str(image_count * ms_between_frames) + '.jpg')
    Image.fromarray(prepare_image(Image.fromarray(image))).save(filename,
                                                            format='JPEG')
    image_count += 1
    print image_count, '/', frame_count/step
  return image_dir

def image_frames_dir(url, ms_between_frames):
  '''
  Generates the image frames directory name unique to the video's url and
  the frame rate in milliseconds.
  '''
  return join(ROOT, 'data/images', get_video_id(url) + '_' +
              str(ms_between_frames))

def get_video(url):
  '''
  Returns the filename of the downloaded mp4
  '''
  video = pafy.new(url)
  stream = get_stream(video)
  filename = downloaded_filename(url, video.title, stream.extension)
  # First check if we cached it
  mp4_filename = converted_mp4_filename(filename)
  if exists(mp4_filename):
    return mp4_filename
  stream.download(filename)
  return convert_video_to_mp4(filename)

def prepare_image(image):
  'Resizes the images to 256x256 and demeans the images.'
  image = resize_and_paste(image, (256, 256))
  image = np.asarray(image)
  return (image - np.array(IMAGE_MEAN)).astype(np.uint8)

def resize_and_paste(image, new_shape):
  '''
  The original image proportions are left unchanged; any left over area
  is filled with black.
  '''
  new_width, new_height = new_shape[:2]
  cw, ch = image.size
  result = Image.new('RGB', (new_width, new_height), color=(0,0,0))

  dw = float(new_width) / cw
  dh = float(new_height) / ch

  if dw < dh:
    ratio = float(new_width) / cw
    image = image.resize((int(cw * ratio), int(ch * ratio)))
    cw, ch = image.size
    result.paste(image, (0, (new_height - ch) / 2))
  else:
    ratio = float(new_height) / ch
    image = image.resize((int(cw * ratio), int(ch * ratio)))
    cw, ch = image.size
    result.paste(image, ((new_width - cw) / 2, 0))
  return result

def add_image_mean(image_filename):
  '''
  Adds back the neural net training set image mean that was subtracted
  during classification.
  '''
  image = np.asarray(Image.open(image_filename)) # TODO open straight from np?
  image = (image + np.asarray(IMAGE_MEAN)).astype(np.uint8)
  image = Image.fromarray(image)
  tf = tempfile.NamedTemporaryFile(dir='/tmp', delete=False)
  image.save(tf.name, format='JPEG')
  return tf.name

def draw_image_labels(image_filename, labels):
  'Draws the labels on the image and returns the new image filename.'
  filename = add_image_mean(image_filename)
  text = '\n'.join(labels)
  target_parent = join('data/labelled-images',
                       basename(dirname(image_filename)))
  system('mkdir -p '+ target_parent)
  target = join(target_parent, basename(image_filename))
  cmd = ' '.join(
    ['convert ' + image_filename,
     '-pointsize 14 -fill green ',
     '-draw "text 20%%,20%% \'%s\'"' % text,
     target])
  system(cmd)
  return target

def show_image(image):
  pylab.imshow(image)
  pylab.show()

def get_stream(video):
  'Gets the lowest resolution stream that has the smallest dimension >= 256'
  # my ffmpeg build doesn't convert webm's, so I'm just using m4v for now
  dimensions = [stream.dimensions for stream in video.videostreams \
    if stream.dimensions[0] >= 256 and stream.dimensions[1] >= 256 \
      and str(stream.extension) == 'm4v']
  if len(dimensions) == 0:
    raise Exception('Video does not have a suffciently high resolution')
  res = min(dimensions, key=lambda x:x[0]*x[1])

  for stream in video.videostreams:
    if stream.resolution == str(res[0]) + 'x' + str(res[1]):
      return stream

def convert_video_to_mp4(filename):
  'OpenCV seems to only like mp4'
  target = converted_mp4_filename(filename)
  print target
  system('ffmpeg -i ' + filename + ' -vcodec copy ' + target)
  return target

def converted_mp4_filename(filename):
  return ROOT + '/data/videos/' + splitext(basename(filename))[0] + '.mp4'

def downloaded_filename(url, title, extension):
  return dirname(abspath(__file__)) + '/data/videos/' + get_video_id(url) + \
         sanitized_video_title(title) + '.' + extension

def sanitized_video_title(title):
  return ''.join(x for x in title if x.isalnum())

def get_video_id(url):
  return re.match('.*v=(.*$)', url).groups()[0]

def video_url(video_id):
  return 'https://www.youtube.com/watch?v=' + video_id

def write_video(image_dir):
  '''
  Writes a video from a set of images in `image_dir`
  '''
  target = join('data/labelled-videos',
                basename(image_dir) + '.mp4v')
  codec = cv2.cv.CV_FOURCC('m', 'p', '4', 'v')
  size = (256, 256)
  fps = 16
  actual_frames_per_second = 0.25
  v = cv2.VideoWriter(target, codec, fps, size)
  for image_name in listdir(image_dir):
    image_filename = join(image_dir, image_name)
    arr = np.asarray(Image.open(image_filename))
    assert arr.shape[:2] == size
    for i in range(int(fps/actual_frames_per_second)):
      v.write(arr)

def approximate_video_segments(times):
  '''
  Arguments:
    times: The times at which the noun was detected in the video, in seconds
  Returns:
    approximate segments of time at which the noun was detected
  '''
  pass
