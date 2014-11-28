'''
The purpose of this pygame is to determine precision and recall for
the noun detector.

The images to be judged must be present in `src`. These images are probably
frames of YouTube videos, but that's irrelevant. Each image must be annotated
with all boxes of the detected noun, so that we can record for each image
how many of the nouns present in the picture were detected or not detected.

Usage:
  Run python judge_predictions.py
  For each image, type one of the following letters for each of the nouns
  or bounding boxes you see in the image. E.g. if you see 3 nouns, one box
  covers one of the nouns, and one box covers no nouns, you should type
  "cnnp" and then hit enter.
  If there are no nouns and no bounding boxes, you should just hit enter.
      c (correct) - True positive. A noun is "correctly" in the box.
                    A correct bounding box means that the
                    intersection of the bounding box with what you think
                    should be the actual bounding box is 50% of the union
                    of these two boxes.
      p (false positive) - The noun is not "correctly" in the bounding box,
                           but it was predicted to be.
      n (false negative) - The noun is present in the image, but it's
                           not boxed with a "correct" bounding box.
  If you mistype a letter, you may delete the letter.
  If you want to redo the judgement of the previous image, type 'u'.

The prediction log (the output of this script) is stored in
data/imagenet/<wnid>/prediction_logs/<video_id>_<ms_between_frames>.csv

Each line logged in json includes the following:
  name: the basename of the imgae name
  correctness code: a string of zero or more of 'c', 'p', or 'n'.

This script may be interrupted and rerun, and images will not need
to be re-judged.

When you finish judging all the images, run accuracy.py to compute
precision and recall.
'''

import sys
import pygame
import pygame.locals as pygame_locals
import shutil
from os import system, listdir
import json
from os.path import join, basename, abspath, dirname

import gflags
from gflags import FLAGS
from flags import set_gflags

gflags.DEFINE_string('src', None,
  'The directory of the annotated images to be judged')
gflags.MarkFlagAsRequired('src')

ROOT = dirname(abspath(__file__))

def show_image(name):
  img = pygame.image.load(join(FLAGS.src, name))
  screen = pygame.display.set_mode((img.get_width(), img.get_height()))
  screen.blit(img, (0, 0))
  pygame.display.flip()
  return img, screen

# Render text on image
def print_text(text, img, screen):
  screen.blit(img, (0, 0))
  font = pygame.font.Font(None, 50)
  rendered_text = font.render(text, True, (50,255,255))
  text_rect = rendered_text.get_rect()
  text_rect.centerx = screen.get_rect().centerx
  text_rect.centery = screen.get_rect().centery
  screen.blit(rendered_text, text_rect)
  pygame.display.flip()

def finished():
  with open(LOG) as f_done:
    lines = list(f_done)
    done = [json.loads(line)['name'] for line in lines]
  names = listdir(FLAGS.src)
  for name in names:
    if name not in done:
      return False
  return True

def add_line_to_log(name, code):
  with open(LOG, 'a') as f:
    f.write(json.dumps({'name':name,
                        'code':code}) + '\n');

def remove_line_from_log(name):
  with open(LOG) as f:
    lines = f.readlines()
  with open(LOG, 'w') as f:
    for line in lines:
      if not json.loads(line)['name'] == name:
        f.write(line)

if __name__ == '__main__':
  global LOG
  set_gflags()
  LOG = join(dirname(dirname(abspath(FLAGS.src))),
             'prediction-logs', basename(FLAGS.src) + '.csv')
  system('mkdir -p ' + basename(LOG));
  system('touch ' + LOG);
  pygame.init()
  judged = []

  while not finished():
    with open(LOG, 'r') as f_done:
      lines = list(f_done)
      done = [json.loads(line)['name'] for line in lines]
    unjudged = [name for name in listdir(FLAGS.src) if name not in done]

    while len(unjudged) > 0:
      name = unjudged.pop()
      img, screen = show_image(join(FLAGS.src, name))
      done = False
      code = ''
      while not done:
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            pygame.quit()
          if event.type == pygame_locals.KEYDOWN:
            if event.key == pygame.K_u:
              # Undo the judgement
              if len(judged) > 0:
                # skip the current image
                code = ''
                unjudged.append(name)
                name = judged.pop()
                remove_line_from_log(name)
                img, screen = show_image(name)
            elif event.key == pygame.K_c:
              code += 'c'
              print_text(code, img, screen)
            elif event.key == pygame.K_p:
              code += 'p'
              print_text(code, img, screen)
            elif event.key == pygame.K_n:
              code += 'n'
              print_text(code, img, screen)
            # Move on to the next image
            elif event.key == pygame.K_RETURN \
              or event.key == pygame.K_KP_ENTER \
              or event.key == pygame.K_SPACE:
                done = True
                add_line_to_log(name, code)
                break
      judged.append(name)
