from collections import OrderedDict, defaultdict

from youtube_crawler import search_youtube

# TODO put this in the config
QUERIES_AND_NOUNS = OrderedDict([
  # egg is not present in the 1000 ImageNet categories
  ('how to hard boil an egg', ['stove']),
  ('how to make scrambled eggs', ['stove', 'skillet']),
  ('how to cook an omelet', ['stove', 'skillet']),
  ('how to poach an egg', ['stove']),
  #('how to make jello shots', ['measuring cup']),
  ('how to make french toast', ['skillet', 'mixing bowl', 'stove']),
  ('how to make pancakes', ['skillet', 'mixing bowl', 'stove']),
  ('how to make chocolate chip cookies', ['skillet', 'mixing bowl', 'stove']),
  ('how to make a grilled cheese sandwich', ['skillet', 'stove']),
  #('how to bake a potato in the microwave', ['microwave']),
  #('how to open a wine bottle without a corkscrew', ['wine']),
  ('how to jump start your car', ['sport car', 'street sign', 'car wheel']),
  ('how to make yogurt', ['soup boowl']),
  ('how to remove a stripped screw', ['screw', 'screwdriver']),
  ('how to drive a car', ['sport car', 'street sign', 'car mirror']),
  #('how to clean suede shoes', ['cowboy boot']),
  #('how to unclog a bathtub drain', ['bathtub']),
  #('how to tie a tie', ['Windsor tie']),
])

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

def get_nouns_and_video_ids(num_videos_per_noun):
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
      d[noun].extend(search_youtube(query, fetch_this_many_video_ids))
  return OrderedDict(sorted(d.items()))
      # TODO make sure there are no duplicate video_ids, and maybe have a
      # (noun,video_id) blacklist if the noun isn't present in the video
      # The blacklist can serve both purposes.





