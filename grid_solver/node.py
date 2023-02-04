
# A grid node

class Node(object):
  
  def __init__(self, ix, iy):
    self.ix = ix
    self.iy = iy

  def ixy(self):
    return (self.ix, self.iy)

# A shortcut to generate a node

def n(ix, iy):
  return Node(ix, iy)

