'''
The purpose of this pygame is to determine precision and recall for
the noun detector, and to gather data to learn a function to
determine which labels are correct, especially in light of information
about repeated detections in an image.

Usage:
  Run python judge_predictions.py
  For each image, one of the following letters:
    Correct cases:
      Up arrow  - The image is correctly labelled, and the bounding box
                  is correct.
      l (label only is corect) - The noun is present in the image (the
                  label is correct) but the bounding box is incorrect.
      n (not present) - The dector correctly predicted the noun is not
                        present in the image.
    Incorrect cases:
      p (false positive) - The noun is not in the image, but it was
                           predicted to be.
      n (false negative) - The noun is present in the image, but it's
                           not boxed or labelled

The information logged in json includes the following:
guid:        the date judged in milliseconds
video_id:    the video's YouTube id, found in video's the url
noun_id:     the noun_id to be detected
ms_between_frames: milleseconds between the video frames that were used as
             input to the detector
window_number: the detector sometimes returns many results for one image.
             This number uniquely identifies each result.
num_top_results: The noun is only considered "detected" in the image if
             its prediction score is in the `num_top_results` highest out of
             1000 scores.
score:       1000 times the score the detector gave the noun, if it was in the
             `TOP_PERCENTAGE` of predictions, else 0
mean:        1000 times the mean score of the `TOP_PERCENTAGE` of predictions for
             this frame, if the noun was in the `TOP_PERCENTAGE` of
             predictions, else 0.
correctness: whether the label, the bounding box, or both were correct

In order to check whether an image must be judged, check whether
this collection of identifiers is present in the log:
  video_id, noun_id, ms_between_frames, num_top_results

When the detector accurately locates the noun, it often does so
over more windows that overlap the noun than on incorrect objects.
TODO: Include the bounding box coordinates in the labelled image name,
      as well as the log. Inform the weighting function of this
      information.
'''

