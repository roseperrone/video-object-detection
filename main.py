import pafy

def where_is_noun_in_video(url, noun):
  '''
  Returns:
    a list of tuples of video segments in which that noun appears,
    in seconds. e.g. [(14.4, 20.2), (34.2, 89.2)]
  '''
  video = pafy.new(url)
  print 'Finding "' + noun + '" in "' + video.title + '"'
  return [(14.4, 20.2), (34.2, 89.2)]


if __name__ == '__main__':
  # Video is how to make coffee
  print where_is_noun_in_video('https://www.youtube.com/watch?v=2Ao5b6uqI40',
                               'cup')
