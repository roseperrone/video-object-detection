'''
After the bounding boxes have been drawn using `draw_bounding_boxes.py`,
every bounded box must be cropped and copied into its own image in order
to train and test the net on them. No resizing to 256x256 is necessary
because I let caffe do that.
TODO make sure caffe warps rather than crops.

The source images should be in `data/imagenet/<wnid>/images/all`,
and the cropped images will be placed in
`data/imagenet/<wnid>/images/cropped`.
'''
