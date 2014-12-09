
'''
Uses the Network In Network detector, the best performer on the
ImageNet 2014 detection competition.

SPP_net is faster, but making it work on Mac turned out to be difficult.
'''

from os.path import join, dirname, abspath
from os import system

from image_utils import ordered_listdir
from config import N_FRAMES, NUM_FIRST_FRAMES_SKIPPED

ROOT = dirname(abspath(__file__))

def detect(image_dir, output_filename,
      caffemodel='data/models/bvlc_reference_caffenet.caffemodel',
      deploy_prototxt='data/models/bvlc_reference_caffenet/deploy.prototxt'):
  '''
  On mac 10.9 running MATLAB R2013a, to make the selective_search work
  (the generator of the windows over which the classifier is run),
  I needed to change 10.7 to 10.9 in
  /Applications/MATLAB_R2013a_Student.app/bin/mexopts.sh, and
  (see http://www.mathworks.com/matlabcentral/answers/87709-just-upgraded-to-x-code-5-0-on-my-mac)
  add -std=c++11 to CXXFLAGS in said script.
  Then in /Users/rose/video-object-detection/caffe/python/caffe/selective_search_ijcv_with_python/selective_search_rcnn
  I needed to add -Dchar16_t=uint16_t to
  mex Dependencies/anigaussm/anigauss_mex.c Dependencies/anigaussm/anigauss.c -output anigauss
  (see http://stackoverflow.com/questions/22367516/mex-compile-error-unknown-type-name-char16-t)
  '''
  image_filenames_txt = '/tmp/image_filenames.txt'
  with open(image_filenames_txt, 'w') as f:
    # the first frame is usually blank, or a title screen
    image_filenames = ordered_listdir(
      image_dir)[NUM_FIRST_FRAMES_SKIPPED:N_FRAMES+1]
    f.write('\n'.join(image_filenames))
  cmd = join(ROOT, 'caffe/python/detect.py')
  cmd += ' --pretrained_model=' + caffemodel
  cmd += ' --model_def=' + deploy_prototxt

  cmd += ' ' + image_filenames_txt
  # In detect.py, the .csv output
  # code is buggy, and the hdf5 gave weird uint8 prediction values, so I
  # pickled the pandas DataFrame instead.
  cmd += ' ' + output_filename
  system(cmd)
