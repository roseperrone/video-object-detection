
from os.path import join, dirname, abspath
from os import system

from performance import timeit
from image_utils import ordered_listdir

N_FRAMES = 7
HUSH_CAFFE = False
ROOT = dirname(abspath(__file__))

@timeit
def detect(image_dir, noun):
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
  output_filename = '/tmp/detection_results.bin'
  with open(image_filenames_txt, 'w') as f:
    # skip the mac .DS_Store file
    image_filenames = [join(image_dir, x) for x in ordered_listdir(image_dir) if not x == '.DS_Store'][:N_FRAMES] # TODO take out [:N_FRAMES]
    if len(image_filenames) > 1:
      f.write('\n'.join(image_filenames))
    else:
      f.write(image_filenames[0])
  cmd = join(ROOT, 'caffe/python/detect.py')
  #cmd += ' --pretrained_model=../data/models/VGG_ILSVRC_19_layers.caffemodel'
  cmd += ' --pretrained_model=data/models/bvlc_reference_caffenet.caffemodel'
  cmd += ' --model_def=data/models/bvlc_reference_caffenet/deploy.prototxt'
  cmd += ' ' + image_filenames_txt
  # In detect.py, the .csv output
  # code is buggy, and the hdf5 gave weird uint8 prediction values, so I
  # pickled the pandas DataFrame instead.
  cmd += ' ' + output_filename
  if HUSH_CAFFE:
    cmd += ' > /dev/null'
  print cmd
  system(cmd)
  return output_filename
