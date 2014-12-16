'''
Fetches images for a certain query from a Custom Google Search Engine.

Usage:
  Create a Custom Google Search Engine and put your api_key
  and cx (Custom Google Search Engine ID) in
  data/google_auth.yaml
  Then run this script.
'''

import gflags
from gflags import FLAGS
from flags import set_gflags

gflags.DEFINE_string('query', None, 'The google image search query')
gflags.DEFINE_integer('num_results', None, 'How many images to fetch')
gflags.MarkFlagAsRequired('query')
gflags.MarkFlagAsRequired('num_results')

from os.path import dirname, abspath, join, exists
from os import system
import yaml
from apiclient.discovery import build

ROOT = dirname(abspath(__file__))

if __name__ == '__main__':
  set_gflags()
  system('mkdir -p ' + join(ROOT, 'data', 'google-images', FLAGS.query))
  links_dir = join(ROOT, 'data', 'google-image-links')
  system('mkdir -p ' + links_dir)
  links_file = join(links_dir, FLAGS.query + '.txt')
  with open(join(ROOT, 'data/google_auth.yaml')) as f:
    contents = yaml.load(f)
    api_key = contents['api_key']
    cx = contents['cx']

  # Build a service object for interacting with the API. Visit
  # the Google APIs Console <http://code.google.com/apis/console>
  # to get an API key for your own application.
  service = build('customsearch', 'v1', developerKey=api_key)

  # Ensure entries in the output txt file contains unique links
  found_filenames = set()
  if exists(links_file):
    with open(links_file) as f:
      for filename in f:
        found_filenames.add(filename[:-1]) # strip off newline

  # Get search results
  num_results_found = 0
  start = 1 # strange that I can't start at 0...
  with open(links_file, 'a') as f:
    while num_results_found < FLAGS.num_results:
      res = service.cse().list(
          q=FLAGS.query,
          searchType='image',
          fileType='jpg',
          imgType='photo',
          start=start, # index of the first result to return
          cx=cx, # a Custom Search Engine I created
        ).execute()
      start += len(res['items'])
      print start, '/', FLAGS.num_results
      for item in res['items']:
        if item['link'] not in found_filenames:
          f.write(item['link'] + '\n')
