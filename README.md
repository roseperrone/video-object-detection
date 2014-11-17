# Simple object detection in YouTube videos.

## Order in which to use the scripts to train a net on a single noun

```
fetch_positive_images.py
optional:
  filter_positive_images.py
  or
  draw_bounding_boxes.py and then bounded_box_cropper.py
create_data_splits.py
prepare_data.py
Manually create the prototxt files now. See prototxt_generation_instructions.md
...

```


## Order in which to use the scripts to test a net on youtube videos to detect a single noun

```
...
accuracy.py
```
