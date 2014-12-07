import numpy as np
import pandas as pd
from collections import defaultdict

from config import NON_MAXIMAL_SUPPRESSION_OVERLAP_THRESHOLD

def get_boxes(detection_output_file):
  '''
  Runs non-maximal suppression over each image.

  Returns all boxes that have the score for label "1" > 0.99.
  Label "1" is the positive category.

  The data frame has these fields:
    index (which is the image filename)
    prediction (a matrix of one score per class. Here we have two classes)
    xmin
    xmax
    ymin
    ymax
  '''
  df = pd.read_pickle(detection_output_file)
  boxes = defaultdict()
  neg = 0
  pos = 0
  filename = None
  data = None
  data = np.empty(shape=[0, 5])
  for i in range(df.index.shape[0]):
    if df.index[i] != filename:
      filename = df.index[i]
      if data.size > 0:
        boxes[filename] = nms_detections(data, 0.1)
      else:
        boxes[filename] = np.array([])
      data = np.empty(shape=[0, 5])
    pred = df.prediction[i].as_matrix()
    if pred[1] / (pred[0] + pred[1]) > 0.5:
      pos += 1
      data = np.append(data,
                [[df.xmin[i], df.xmax[i], df.ymin[i], df.ymax[i], pred[1]]],
                axis=0)
    else:
      neg += 1
  print '================================================='
  print pos, 'positive results and', neg, 'negative results'
  print '================================================='
  return boxes

# I adapted the following code from
# http://nbviewer.ipython.org/github/BVLC/caffe/blob/master/examples/detection.ipynb
def nms_detections(dets, overlap=0.3):
    '''
    Non-maximum suppression: Greedily select high-scoring detections and
    skip detections that are significantly covered by a previously
    selected detection.

    This version is translated from Matlab code by Tomasz Malisiewicz,
    who sped up Pedro Felzenszwalb's code.

    Parameters
    ----------
    dets: ndarray
        each row is ['xmin', 'xmax', 'ymin', 'ymax', 'score']
    overlap: float
        minimum overlap ratio (0.3 default)

    Output
    ------
    dets: ndarray
        remaining after suppression.
    '''
    x1 = dets[:, 0]
    x2 = dets[:, 1]
    y1 = dets[:, 2]
    y2 = dets[:, 3]
    ind = np.argsort(dets[:, 4])

    w = x2 - x1
    h = y2 - y1
    area = (w * h).astype(float)

    pick = []
    while len(ind) > 0:
      # Select the detection with the highest score that hasn't already
      # been skipped due to overlap with a detection that has a higher score.
      i = ind[-1]
      pick.append(i)
      ind = ind[:-1]

      # Find the overlap region between the ith detection and the rest of
      # the detections not yet considered. The goal is to remove the detections
      # that overlap too much with the ith detection.
      xx1 = np.maximum(x1[i], x1[ind])
      yy1 = np.maximum(y1[i], y1[ind])
      xx2 = np.minimum(x2[i], x2[ind])
      yy2 = np.minimum(y2[i], y2[ind])

      # intersection width and weight
      w = np.maximum(0., xx2 - xx1)
      h = np.maximum(0., yy2 - yy1)

      # intersection area
      wh = w * h

      # area[i] + area[ind] is the union of the areas. wh is the intersection.
      # I'm not sure why the "- wh" is present in the denominator. That's
      # not the behavior I want.
      # e.g. if the intersection is 5, but the union of the areas is 10, I want
      #      the overlap to be measured as 0.5, but this equation would
      #      measure it as 1.0
      #o = wh / (area[i] + area[ind] - wh)
      o = wh / (area[i] + area[ind])

      # Remove the detections that are significantly covered by a
      # previously selected detection.
      # Currently this code allows a small boxes within a big box. That behavior
      # doesn't make sense in my case, because I'm only detecting one object, and
      # they don't differ in size by an order of magnitude, so it wouldn't be
      # useful to detect a small object in front of a big object.
      # TODO add another condition on keeping the lower-score detections to avoid
      # boxes within boxes. If the intersection area is equal to either area
      # individually, one box is inside the other.
      ind = ind[np.nonzero(o <= overlap)[0]]

    return dets[pick, :]
