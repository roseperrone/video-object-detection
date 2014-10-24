'''
This file contains video metadata and the ImageNet class list.
'''
from collections import OrderedDict

'''
Ozan's dataset of videos basically contains the first 100 videos
for each of the YouTube searches below.

How to +
Hard Boil an Egg (6,785,176 views)
Make Jello Shots (6,440,352 views)
Make French Toast (4,362,799 views)
Bake a Potato in the Microwave (3,486,832 views)
Open a Wine Bottle Without a Corkscrew (3,096,476 views)
Make Pancakes (2,604,187 views)
*Make Scrambled Eggs (2,354,174 views)
*Poach an Egg (2,039,776 views)
Make Chocolate Chip Cookies (1,970,043 views)
Cook an Omelette (1,943,422 views)
Jump Start a Car (1,904,088 views)
Make Yogurt (1,882,532 views)
Remove a Stripped Screw (1,879,962 views)
Drive a Car (1,646,260 views)
Clean Suede Shoes (1,644,476 views)
Make a Grilled Cheese Sandwich (1,644,436 views)
Unclog a Bathtub Drain (1,581,142 views)
Tie a Tie (1,522,161 views)
'''



NOUNS_AND_VIDEO_IDS = OrderedDict([
  ('wine',
    ['n63SWcNNWvg',
    ],
  ),
  ('banana',
    # how to make banana icecream
    ['9uddKYGPEkg', # the classifier has a recall of 50% and precision of 100%
    ],
  ),
  ('egg', # This noun is not in the ImageNet set and won't be detected
          # until we use a different detector
    # how to hard boil an egg
    ['1QK-DGlRcTo',
     '7-9OEohpivA',
     'lbzhyvH74w8',
     'qX7A0LPIuKs',
     's1oUDsonIzg',
     'sSni2HTfvM',
     'wdasrVE5NOc',
     'zuMslqJKQo',
     # how to poach an egg
     'jk36el4_Rbc',
     'JrRqG9Apt6g',
     'KtZ14xEbgzg',
     'pAWduxoCgVk',
     'UMiCy8EH1go',
     'xpN1dlH3tWo',
     'yppgDL0Mn3g',
     # how to scramble an egg
     '65ifzkFi614',
     'FbLU87PYsZE',
     'Nbh64ntT3EM',
     'R4vDqlKMbrk',
     's9r-CxnCXkg',
     'TGyb7uBXe9E',
     'Be0koDmxrtQ',
     'M8SHMUBnm4A',
     'PUP7U5vTMM0',
     's9r-CxnCXkg',
     # how to make an omelet
     '1dGBRGtyzX0',
     '57afEWn-QDg',
     'AgHgbn_sVUw',
     'AJ2uBYCVHik',
     'OQyRuOEKfVk',
     'PLDUqyS2AGA',
     'PzWsyPHoSyQ',
     'r09Hgeb9-6s',
     'zglsDdaBf4g',
    ],
  ),
])

