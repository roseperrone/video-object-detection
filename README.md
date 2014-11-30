# Simple object detection in YouTube videos.

## To train a net on a single noun, run these scripts

```
fetch_positive_images.py
optional:
  filter_positive_images.py
  or
  draw_bounding_boxes.py and then bounded_box_cropper.py
create_data_splits.py
prepare_data.py
Manually create the auxiliary prototxt files now. See
prototxt_generation_instructions.txt
train.py
```

## To run the net on youtube videos to produce frames with the detected noun drawn in a bounding box, run these scripts

```
main.py
judge_predictions.py
accuracy.py
```
