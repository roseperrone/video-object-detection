'''
# Each model takes this fomrmat:
# The key is the trained model name, and the value is a tuple containing:
#   - a path to the caffemodel
#   - a path to the deploy.prototxt of the trained model
# Below each model, I also comment some information about statistics the
# model printed during training.
'''
MODELS = {
  'alexnet': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/'
    'alexnet/snapshots/snapshot_iter_6000.caffemodel',
    '/Users/rose/home/video-object-detection/aux/alxenet/deploy.prototxt'
  ),
  # Accuracy per test iteration:
  #  0:    0.904
  #  2000: 0.976
  #  4000: 0.970
  #  6000: 0.965
  # I stopped training this at iteration 7000
  # lr = 0.01



  'nin-equal': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/'
    'images/nin-equal/snapshots/snapshot_iter_6500.caffemodel',
    '/Users/rose/home/video-object-detection/aux/nin-equal/deploy.prototxt'
  ),
  # Accuracy per test iteration:
  #  0:    0.738
  #  1500: 0.944
  #  3000: 0.953
  #  4500: 0.979
  #  6000: 0.981
  # lr = 0.001. When I trained with 0.01, the loss remained constant at 0.63
  # I stopped training this at iter 6500
  # I judged predictions on 10 videos and computed this accuracy:
  #   precision: 0.28
  #   recall: 0.22


  'nin-high-neg': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/'
    'nin-high-neg/snapshots/snapshot_iter_9000.caffemodel',
    '/Users/rose/home/video-object-detection/aux/high-neg/deploy.prototxt'
  ),
  # Accuracy per test iteration:
  #  0:    0.910
  #  1000: 0.908
  #  2000: 0.919
  #  3000: 0.931
  #  4000: 0.934
  #  5000: 0.951
  #  6000: 0.9524
  #  7000: 0.9518
  #  8000: 0.954
  #  9000: 0.952

  # I trained this with lr = 0.001. When I trained with 0.01, the loss
  # remained constant at 0.63. I trained this model with a 7:1 negative to
  # positive training ratio.
  # This data skew caused the predictions for the negative class to be all 0s.
  # That is, pred[0], pred[1] scores look like this:
  # 11.9817 0.0
  # 8.1218 0.0
  # 13.3314 0.0
  # 6.01843 0.0
  # 10.6878 0.0
  # 15.3691 0.0
  # 18.2615 0.0
  # I'll keep equal numbers of negative and positive training images
  # in the future. It's curious, though, that the test accuracy was steadily
  # improving. I'm sure I'm using the correct model for detection, because
  # this is the first model I've trained up to iteration 9000.

  # A similar skew happened before with this NIN model, when an LMDB bug caused
  # me to have way more positive training images than negative training images.
  # In that situation, the positive class had pred[0], pred[1] scores like this:
  # 0.0 10.1965
  # 0.0 89.606
  # 0.0 15.007
  # 0.0 8.72097
  # 0.0 27.801
  # 0.0 55.6223


  'nin-finetuned': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/'
    'nin-finetuned/snapshots/snapshot_iter_xxxx.caffemodel',
    '/Users/rose/home/video-object-detection/aux/finetuned/deploy.prototxt'
  ),
  # This model uses an equal neg:pos train ratio. I also removed all images from
  # the positive set except clean, white or off-white, mostly-unobscured
  # whole eggs. In doing so, I reduced the numbor of positive images from
  # 2226 to 523. I also changed the neg:pos test ratio to 8, and I changed
  # the train:test ratio to 20 instead of 40.
  #
  # The initial output is unhealthy. The same constant loss of 0.693 occured
  # when the learning rate was too high at 0.01. I could try taking the learning
  # rate down to 0.005, or maybe base_lr of layer ccc8-finetuned should be halved.
  # TODO find out what causes low initial accuarcy far lower than the fraction
  # of images in the majority class.
  #
  # I1207 19:49:35.855978 2113241856 solver.cpp:247] Iteration 0, Testing net (#0)
  # I1207 19:57:59.032723 2113241856 solver.cpp:298]     Test net output #0: accuracy = 0.110674
  # I1207 19:58:10.862572 2113241856 solver.cpp:191] Iteration 0, loss = 1.35524
  # I1207 19:58:10.862649 2113241856 solver.cpp:403] Iteration 0, lr = 0.001
  # I1207 20:01:23.613678 2113241856 solver.cpp:191] Iteration 20, loss = 0.693147
  # I1207 20:01:23.620987 2113241856 solver.cpp:403] Iteration 20, lr = 0.001
  # I1207 20:04:30.676769 2113241856 solver.cpp:191] Iteration 40, loss = 0.693147
  # I1207 20:04:30.684061 2113241856 solver.cpp:403] Iteration 40, lr = 0.001
  # I1207 20:07:41.066269 2113241856 solver.cpp:191] Iteration 60, loss = 0.693147
  #
  # TODO find out what the base leraning rate has to do with the first iteration.
  # When I changed base_lr to 0.0003, I got this healthier training output:
  #
  # I1207 22:48:26.989333 2113241856 solver.cpp:247] Iteration 0, Testing net (#0)
  # I1207 22:56:44.848688 2113241856 solver.cpp:298]     Test net output #0: accuracy = 0.782135
  # I1207 22:56:57.263177 2113241856 solver.cpp:191] Iteration 0, loss = 0.667033
  # I1207 22:56:57.263277 2113241856 solver.cpp:403] Iteration 0, lr = 0.0003
  # I1207 23:00:22.607585 2113241856 solver.cpp:191] Iteration 20, loss = 0.693147
  # I1207 23:00:22.614925 2113241856 solver.cpp:403] Iteration 20, lr = 0.0003
  # I1207 23:04:01.619460 2113241856 solver.cpp:191] Iteration 40, loss = 0.693147
  #
  # TODO this might have something to do with the massive skew in the nin-high-neg
  # A learning rate of 0.0001 gradually decreased the loss from 0.78 down to
  # 0.43 at iteration 280, but it wavered. E.g. at iter 300, it was back up to 0.45.


  'nin-clean': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/'
    'nin-clean/snapshots/snapshot_iter_2000.caffemodel',
    '/Users/rose/home/video-object-detection/aux/nin-clean/deploy.prototxt'
  ),
  # The same data prep for nin-finetuned applies to nin-clean
  #
  # Accuracy per test iteration:
  #  0:    0.891
  #  1000: 0.966
  #  2000: 0.989 (retested at 0.985)
  #  3000: 0.989

  'bvlc-finetuned': (
    '/Users/rose/home/video-object-detection/data/imagenet/n07840804/images/'
    'bvlc-finetuned/snapshots/snapshot_iter_9000.caffemodel',
    '/Users/rose/home/video-object-detection/aux/bvlc-finetuned/deploy.prototxt'
  ),
  # The same data prep for nin-finetuned applies to bvlc-finetuned
  # Note that I forgot to change the two blobs_lr fields of the the layer
  # I reset to random weights to 10 and 20.
  #
  # Accuracy per test iteration:
  #  0:    0.54
  #  1000: 0.99
  #  2000: 0.985
  #  3000: 0.995
  #  4000: 0.99
  #  5000: 1
  #  6000: 0.99
  #  7000: 0.995
  #  8000: 0.995
  #  9000: 0.995
  #
  # I annotated these images using the model at snapshot_iter_2000.caffemodel:
  #   M8SHMUBnm4A_10000
  #   PUP7U5vTMM0_10000
  #   PzWsyPHoSyQ_10000
  #   r09Hgeb9-6s_10000
  #   zglsDdaBf4g_10000
  # All the others I annotated using snapshot_iter_9000.caffemodel.
}

