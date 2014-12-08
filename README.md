# Simple object detection in YouTube videos, using Caffe

![alt tag](https://github.com/roseperrone/video-object-detection/blob/master/good-egg.jpg)

## Components of this pipeline

- YouTube video fetcher
- ImageNet image fetcher
- A pygame to select images to use for training and testing the net
- A pygame to draw bounding boxes on said images
- A script to create data splits (positive/negative train/test) for the neural net
- A script to construct LMDB dbs and compute the image mean, for use by the neural net
- Instructions to generate the auxillary files necessary for training a model from scratch, or finetuning it
- Neural net trainer (a wrapper around Caffe's solver)
- Object detector, using a trained net (a wrapper around Caffe's detector)
- Image annotator, which draws detected bounding boxes
- A pygame to judge the detections
- A script to compute the precision and recall of said judgements

## Usage

#### To train a net on a single noun, run these scripts

```
fetch_positive_images.py
optional:
  filter_positive_images.py
  or
  draw_bounding_boxes.py and then bounded_box_cropper.py
create_data_splits.py
prepare_data.py
Manually create the auxillary prototxt files now. See prototxt_generation_instructions.txt
train.py
```

#### To run the net on youtube videos to produce frames with the detected noun drawn in a bounding box, run these scripts

```
main.py
judge_predictions.py
accuracy.py
```

The only change I made to my local caffe repo is in python/detect.py:main,
I return `df.to_pickle(args.output_file)` rather than a csv or h5.

## Discussion

#### Why use neural nets for object detection in YouTube videos? Why not track objects between frames?

I'm trying to detect not a specific object, but a class of an object (e.g. all whole eggs, regardless of color, shape, size, decoration, orientation, shadows and partial obscurity). Deep nets can learn more complex models than shallow ones.

Unlike surveillance, YouTube videos typically cut from scene to scene quickly, making object tracking of limited use. Furthermore, the object is typically not present in a vast majority of the scenes, so much time would be wasted tracking irrelevant objects, but an object tracker could be used after the this system identifies a handful of scenes in which the object is present.

#### Does it work well enough to be useful for robots?

That depends on the noun you're trying to detect. It currently does not work well for detecting whole eggs. The detections in the image above are the best I've seen so far. (the `nin-clean` model detected that)

#### In what ways can this system improve?

- Refinement of data (for detection of eggs, use only non-decorated white chicken eggs. In the current dataset I included all sorts of different whole eggs, like dirty eggs, painted eggs, ostritch eggs, in hopes that the net would better generalize to different egg sizes, shadows, and orientations)
- More data, which is easy to fetch, but must be manually bounded. It took me, what, over three hours to bound about 2281 images.
- Longer training of the neural nets. I've just been training nets overnight on my macbook, which lacks a GPU.
- Use the SPP neural net for speed. Try other neural nets.

#### Why use Caffe? Why not Theano, Torch7, or cudaconvnet?

Caffe has more desireable publicly available trained models.

#### Why did you choose the neural nets that you did?

There are few neural nets available on the Caffe Model Zoo. The net that has performed the best so far I selected because it scored highest in object detection in the 2014 ILSVRC.

#### Why not use unmodified neural nets already trained on the ImageNet ILSVRC 2012 dataset?

The 1000 classes in the dataset does not contain eggs, or an analog. I tried classification using such an unmodified net, and the results weren't useful. I am, however, finetuning a couple of these pretrained nets.

