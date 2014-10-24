

# If the noun is in this percentage of the highest predictions
# of ImageNet classes, annotate the image frame with the
# noun, the prediction score, and the bounding box.
TOP_PERCENTAGE = 0.01

# The videos in which nouns are detected are the top search results
# for these queries
from collections import OrderedDict
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
  ('how to make yogurt', ['soup bowl']),
  ('how to remove a stripped screw', ['screw', 'screwdriver']),
  ('how to drive a car', ['sport car', 'street sign', 'car mirror']),
  #('how to clean suede shoes', ['cowboy boot']),
  #('how to unclog a bathtub drain', ['bathtub']),
  #('how to tie a tie', ['Windsor tie']),
])

# The number of frames per video in which detect the noun
# (to be removed when parameters and models are improved)
N_FRAMES = 1

# The number of frames skipped at the beggining of each video,
# Because they're usually title screens
NUM_FIRST_FRAMES_SKIPPED = 1

# caffe prints a lot
HUSH_CAFFE = True
