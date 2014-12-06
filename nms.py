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
      data = np.empty(shape=[0, 5])
    pred = df.prediction[i].as_matrix()
    if pred[1] > 0.99:
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

# I found the following code at
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
        each row is ['xmin', 'ymin', 'xmax', 'ymax', 'score']
    overlap: float
        minimum overlap ratio (0.3 default)

    Output
    ------
    dets: ndarray
        remaining after suppression.
    '''
    x1 = dets[:, 0]
    y1 = dets[:, 1]
    x2 = dets[:, 2]
    y2 = dets[:, 3]
    ind = np.argsort(dets[:, 4])

    w = x2 - x1
    h = y2 - y1
    area = (w * h).astype(float)

    pick = []
    while len(ind) > 0:
        i = ind[-1]
        pick.append(i)
        ind = ind[:-1]

        xx1 = np.maximum(x1[i], x1[ind])
        yy1 = np.maximum(y1[i], y1[ind])
        xx2 = np.minimum(x2[i], x2[ind])
        yy2 = np.minimum(y2[i], y2[ind])

        w = np.maximum(0., xx2 - xx1)
        h = np.maximum(0., yy2 - yy1)

        wh = w * h
        o = wh / (area[i] + area[ind] - wh)

        ind = ind[np.nonzero(o <= overlap)[0]]

    return dets[pick, :]
