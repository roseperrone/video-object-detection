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
      c (correct) - A noun is "correctly" in the box. A correct bounding
                    box means that the
                    intersection of the bounding box with what you think
                    should be the actual bounding box is 50% of the union
                    of these two boxes.
      p (false positive) - The noun is not "correctly" in the bounding box,
                           but it was predicted to be.
      n (false negative) - The noun is present in the image, but it's
                           not boxed with a "correct" bounding box.
  If you mistype a letter, you may delete the letter.
  If you want to redo the judgement of the previous image, type 'u'.

Name the log file with the information required to uniquely identify the
set if images. For YouTube videos, that's video_id, noun_id, ms_between_frames,
and today's date. Specifically:
  video_id:    the video's YouTube id, found in video's the url
  noun_id:     the noun_id to be detected
  ms_between_frames: milleseconds between the video frames that were used as
               input to the detector

Each line logged in json includes the following:
  name: the basename of the imgae name
  correctness code: a string of zero or more of 'c', 'p', or 'n'.

This script may be interrupted and rerun, and images will not need
to be re-judged.
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
gflags.DEFINE_string('log', None, 'The name of the log of judgements. '
  'This log is used by accuracy.py to compute precision and recall')
gflags.MarkFlagAsRequired('src')
gflags.MarkFlagAsRequired('log')

ROOT = direname(abspath(__file__))

def show_image(name):
  img = pygame.image.load(join(FLAGS.src, name))
  _screen = pygame.display.set_mode((img.get_width(), img.get_height()))
  _screen.blit(img, (0, 0))
  pygame.display.flip()
  return img

# Render text on image
def print_text(text, img):
  _screen = pygame.display.set_mode((img.get_width(), img.get_height()))
  font = pygame.font.Font(None, 50)
  rendered_text = font.render(text, True, (153,100,0))
  text_rect = rendered_text.get_rect()
  text_rect.centerx = _screen.get_rect().centerx
  text_rect.centery = _screen.get_rect().centery
  _screen.blit(rendered_text, text_rect)
  pygame.display.flip()

def finished():
  with open(FLAGS.log) as f_done:
    lines = list(f_done)
    done = [json.loads(line)['filename'] for line in lines]
  names = listdir(FLAGS.src)
  for name in names:
    if name not in done:
      return False
  return True

def add_line_to_log(name, code):
  with open(FLAGS.log, 'a') as f:
    f.write(json.dumps({'name':name,
                        'code':code


def remove_line_from_log(name):
  with open(FLAGS.log) as f:
    lines = f.readlines()
  with open(FLAGS.log, 'w') as f:
    for line in lines:
      if not json.loads(line)['name'] == name:
        f.write(line)

if __name__ == '__main__':
  set_gflags()
  pygame.init()

  system('mkdir -p ' + FLAGS.dst)
  system('touch ' + FLAGS.log)
  judged = []

  while not finished():
    with open(FLAGS.log, 'r') as f_done:
      lines = list(f_done)
      done = [json.loads(line)['name'] for line in lines]
    unjudged = [name in listdir(FLAGS.src) if name not in done]

    while len(unjudged) > 0:
      name = unjudged.pop()
      img = show_image(join(FLAGS.src, name))
      done = False
      code = ''
      while not done:
        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            pygame.quit()
          if event.type == pygame_locals.KEYDOWN:
            if event.key == pygame.K_u:
              print 'u'
              # Undo the judgement
              if len(judged) > 0:
                # skip the current image
                code = ''
                unjudged.append(name)
                name = judged.pop()
                remove_line_from_log(name)
                img = show_image(name)
            elif event.key == pygame.K_c:
              code += 'c'
              print_text(code, img)
            elif event.key == pygame.K_p:
              code += 'p'
              print_text(code, img)
            elif event.key == pygame.K_n:
              code += 'n'
              print_text(code, img)
            # Move on to the next image
            elif event.key == pygame.K_RETURN \
              or event.key == pygame.K_KP_ENTER \
              or event.key == pygame.K_SPACE:
              elif event.key == pygame.K_DOWN:
                done = True
                add_line_to_log(name, code)
                break
    judged_images.append(name)
