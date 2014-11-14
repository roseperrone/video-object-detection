'''
Usage:
  up-arrow    - copy this image to `dst`
  down-arrow  - don't
  u           - undo. Re-judge the previous image. You can undo as many
                judgements as you wish.

Example use case of this script:
  This script is useful if, for example, I want to take all my images of
  eggs in the `src` directory, and move only the ones that are of whole
  eggs and not scrambled eggs into `dst`.
'''

import sys
import pygame
import pygame.locals as pygame_locals
import shutil
from os import system, listdir
from os.path import join, basename

import gflags
from gflags import FLAGS
from flags import set_gflags

gflags.DEFINE_string('src', None, 'The directory of images to filter')
gflags.DEFINE_string('dst', None, 'The directory of filtered images')
gflags.MarkFlagAsRequired('src')
gflags.MarkFlagAsRequired('dst')

def show_image(filename):
  img = pygame.image.load(filename)
  _screen = pygame.display.set_mode((img.get_width(), img.get_height()))
  _screen.blit(img,(0, 0))
  pygame.display.flip()

if __name__ == '__main__':
  set_gflags()
  pygame.init()

  system('mkdir -p ' + FLAGS.dst)
  not_yet_judged_images = [join(FLAGS.src, name) for name in \
                           listdir(FLAGS.src)]
  judged_images = []

  while len(not_yet_judged_images) > 0:
    filename = not_yet_judged_images.pop()
    show_image(filename)
    done = False
    while not done:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
        if event.type == pygame_locals.KEYDOWN:
          if event.key == pygame.K_u:
            print 'u'
            # Undo the judgement
            if len(judged_images) > 0:
              # skip the current image
              not_yet_judged_images.append(filename)

              filename = judged_images.pop()
              # remove the previous file from `dst`, if it's there
              # I hate doing this haha...
              system('rm -f ' + join(FLAGS.dst, basename(filename)))
              show_image(filename)
          elif event.key == pygame.K_UP:
            shutil.copyfile(filename, join(FLAGS.dst, basename(filename)))
            done = True
            break
          elif event.key == pygame.K_DOWN:
            done = True
            break
    judged_images.append(filename)
