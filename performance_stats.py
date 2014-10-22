'''
This file contains functions for measuring performance, and describes the
performance of different steps in the pipeline.
'''

import time

def timeit(f):
  '''Times a function.

  Usage: @timeit
         def my_func():
           ...

        prints 'my_func took 0.8028 seconds'
  '''
  def f_timer(*args, **kwargs):
    start = time.time()
    result = f(*args, **kwargs)
    end = time.time()
    print '===================================================='
    print f.__name__, 'took', '%.4f' % (end - start), 'seconds'
    print '===================================================='
    return result
  return f_timer


'''
10/19:
  This is the amount of time in seconds each step of the pipeline
  takes on a video that contains 2 frames:
    downloading the video       4 (get_video)
    preparing the image frames  6 (prepare_images)
    selecting windows           10, 11, 9 (get_windows)
    predicting nouns in windows 54, 97, 80 (detect_windows)
    drawing the resullts        N (draw_results)


  21 frames:
    downloading the video       4 (get_video)
    preparing the image frames  6 (prepare_images)
    selecting windows           93 (get_windows)
    predicting nouns in windows 1862 (detect_windows)
    drawing the resullts        N (draw_results)

    I think one of these was stalled on something...
    ====================================================
    draw_results took 2910.3690 seconds
    ====================================================
    ====================================================
    detect took 4889.1707 seconds
'''
