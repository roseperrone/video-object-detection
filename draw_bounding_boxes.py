'''
This script is used to record the bounding boxes of the noun in all images.
There may be 0, 1, or many bounding boxes per image.

All images must be in `data/imagenet/<wnid>/images/all-positive-uncropped`.
Use `imagenet_image_fetcher` to do so.

Usage:
  Click the top-left and then the bottom-right corner of the
  bounding box of each noun so that the noun is tightly bounded.

  u - undo the last click
  Enter, Return, or SPACE - Move on to the next image

  To redo an image, delete the line in the log that begins
  with the image's filename.
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

# This default wnid is for eggs
gflags.DEFINE_string('wnid', 'n07840804',
                     'The wordnet id of the noun in the positive images')

# It's easier to draw on bigger images
gflags.DEFINE_integer('screen_size', 800, '')

import csv
import glob
import Image
import pygame
import pygame.locals as pygame_locals
from os import system
from os.path import dirname, abspath, join, basename

COLORS = [(0, 255, 0),    # green
          (255, 0, 0),    # red
          (255, 171, 0),  # orange
          (246, 253, 35), # yellow
          (0, 255, 255),  # blue
          (186, 94, 255), # purple
          (255, 0, 255),  # pink
          (96, 0, 0),     # dark red
         ]
RADIUS = 5
ROOT = dirname(abspath(__file__))


def add_line_to_csv(filename, game, outfile):
  row = [filename]
  width, height = Image.open(filename).size
  # Record the ratios of the x or y measurement to the file width or height,
  # respectively
  coordinates = game.mark_imprint_boxes(filename)
  for i in xrange(0, len(coordinates), 2):
    x = "%.4f" % (float(coordinates[i])/float(width))
    y = "%.4f" % (float(coordinates[i+1])/float(height))
    row.extend((x,y))
  with open(outfile, 'a') as csvfile:
    csv.writer(csvfile).writerow(row)

class PyGame:
  def __init__(self):
    pygame.init()
    self.coordinates = []

  # Render text on image
  def print_text(self, text):
    font = pygame.font.Font(None, 50)
    rendered_text = font.render(text, True, (153,0,0))
    text_rect = rendered_text.get_rect()
    text_rect.centerx = self._screen.get_rect().centerx
    text_rect.centery = self._screen.get_rect().centery
    self._screen.blit(rendered_text, text_rect)
    pygame.display.flip()

  def draw_brush(self):
    # Draw a vertical and horizontal line emanating from the cursor,
    # to make it easier to determine bounding boxes.
    pos = pygame.mouse.get_pos()
    self._screen.blit(self.screen_layers[-1], (0,0))
    pygame.draw.circle(self._screen,
                       COLORS[len(self.coordinates)/4 % len(COLORS)],
                       pos, 5)
    w = self._screen.get_width()
    h = self._screen.get_height()
    # Horizontal line
    pygame.draw.lines(self._screen,
                      COLORS[len(self.coordinates)/4 % len(COLORS)],
                      True, [(0, pos[1]), (w, pos[1])], 1)
    # Vertical line
    pygame.draw.lines(self._screen,
                      COLORS[len(self.coordinates)/4 % len(COLORS)], True,
                      [(pos[0], 0), (pos[0], h)], 1)
    pygame.display.flip()

  def mark_imprint_boxes(self, filename):
    '''
    Returns:
      A list of [(x0,y0),(x1,y1)] coordinates for each marked bounding
      box, where:
        (x0,y0) is the top left corner
        (x1,y1) is the bottom right corner
    '''
    img = Image.open(filename)

    original_pyimg = pygame.image.load(filename)
    original_width = original_pyimg.get_width()
    original_height = original_pyimg.get_height()
    scale_factor = \
      float(FLAGS.screen_size) / float(max(original_width, original_height))
    width = int(original_width * scale_factor)
    height = int(original_height * scale_factor)
    pyimg = pygame.transform.scale(original_pyimg, (width, height))

    self._screen = pygame.display.set_mode((width, height))
    self._screen.blit(pyimg,(0, 0))
    pygame.display.flip()

    self.screen_layers = [pygame.Surface.copy(self._screen)]
    self.coordinates = []

    while 1:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()

        if event.type == pygame_locals.KEYDOWN:

          if event.key == pygame.K_u:
            # Undo the last click
            if len(self.coordinates) > 0:
              self._screen.blit(self.screen_layers.pop(), (0,0))
              self.coordinates.pop()
              self.coordinates.pop()
              pygame.display.flip()
              self.draw_brush()

          # Move on to the next image
          elif event.key == pygame.K_RETURN \
            or event.key == pygame.K_KP_ENTER \
            or event.key == pygame.K_SPACE:
            if len(self.coordinates) % 4 != 0:
              self.print_text(
                'There must be an even number of marked coordinates.')
            else:
              # Scale the coordinates back to the size of the original image
              scaled_coordinates = []
              for k in self.coordinates:
                scaled_coordinates.append(int(k/scale_factor))
              return scaled_coordinates

        elif event.type == pygame.MOUSEBUTTONDOWN:
          pos = pygame.mouse.get_pos()
          pygame.draw.circle(self._screen,
                             COLORS[len(self.coordinates)/4 % len(COLORS)],
                             pos, RADIUS)
          self.screen_layers.append(pygame.Surface.copy(self._screen))
          self.coordinates.append(pos[0])
          self.coordinates.append(pos[1])
        elif event.type == pygame.MOUSEMOTION:
          self.draw_brush()

def get_done_basenames(csvfile):
  done_basenames = set()
  with open(csvfile, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
      done_basenames.add(basename(row[0]))
  return done_basenames

if __name__ == '__main__':
  set_gflags()
  game = PyGame()
  outfile = join(ROOT, 'data/imagenet', FLAGS.wnid, 'bounding_boxes.csv')
  system('touch ' + outfile)

  # Loop over the source filenames in case a line was deleted from the csv
  while 1:
    source_filenames = glob.glob(join(
      ROOT, 'data/imagenet', FLAGS.wnid, 'images/all-positive-uncropped', '*.[Jj][Pp][Gg]'))
    done_basenames = get_done_basenames(outfile)
    if len(done_basenames.intersection(
         set([basename(f) for f in source_filenames]))) == \
         len(source_filenames):
      break
    for source_filename in source_filenames:
      if basename(source_filename) not in done_basenames:
        add_line_to_csv(source_filename, game, outfile)

