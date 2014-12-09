from collections import OrderedDict, defaultdict

from youtube_crawler import search_youtube
from queries import QUERIES_AND_NOUNS, EGG_QUERIES
from imagenet import get_noun_id

def invert_dictionary(d):
  '''
  Swaps the keys and values of a dictionary where each key is a
  string, and each value is a list of strings.

  Returns:
    A dictionary where each key is a string, and each value is a
    list of strings (keys of `d`)
  '''
  new_dict = defaultdict(list)
  for k, v in d.iteritems():
    for elem in v:
      new_dict[elem].append(k)
  return new_dict

# These videos don't have eggs in them, or they only
# have tiny eggs in people's hands, at leats when the
# ms_between_frames is 10000
BLACKLIST = ['Zp2kJ2cstmU',
             'pAWduxoCgVk',
             'PLDUqyS2AGA',
             'R4vDqlKMbrk',
             's9r-CxnCXkg',
             'ShnyBIm2GOQ',
             'wdasrVE5NOc',
             'lbzhyvH74w8', # selective_search fails on this one
             'DKkNi7enlUk',
             'PN2gYHJNT3Y',
             'PUP7U5vTMM0',
             'zglsDdaBf4g',
             'yppgDL0Mn3g',
             '8ki3-ASg9c8',
            ]

def get_egg_video_ids(count):
  video_ids = []
  videos_per_query = count / len(EGG_QUERIES)
  remainder = count - videos_per_query * len(EGG_QUERIES)
  for query in EGG_QUERIES:
    fetch_this_many_video_ids = videos_per_query
    if remainder > 0:
      fetch_this_many_video_ids += remainder
      remainder = 0
    video_ids.extend(search_youtube(query,
                                    fetch_this_many_video_ids))
  return [id for id in video_ids if id not in BLACKLIST]

def get_noun_ids_and_video_ids(num_videos_per_noun):
  '''
  Returns:
    an OrderedDict that contains alphabetically ordered nouns as keys,
    and each value is a list of `num_videos_per_noun` video ids of videos
    that likely contain that noun, as per the search queries in
    `QUERIES_AND_NOUNS`.
  '''
  d = defaultdict(list)
  for noun, queries in invert_dictionary(QUERIES_AND_NOUNS).iteritems():
    videos_per_query = num_videos_per_noun / len(queries)
    remainder = num_videos_per_noun - videos_per_query * len(queries)
    for query in queries:
      fetch_this_many_video_ids = videos_per_query
      if remainder > 0:
        fetch_this_many_video_ids += remainder
        remainder = 0
      d[get_noun_id(noun)].extend(search_youtube(query,
                                                 fetch_this_many_video_ids))
  return OrderedDict(sorted(d.items()))
      # TODO make sure there are no duplicate video_ids, and maybe have a
      # (noun,video_id) blacklist if the noun isn't present in the video
      # The blacklist can serve both purposes.

