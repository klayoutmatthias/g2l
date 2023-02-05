
import typing

class Node(object):

  """
  Represents a node on the abstract layout grid

  A node sits on a x/y coordinate where x and y 
  are abstract integer grid indexes. Usually they
  run from 0 to n, but there is no specific 
  convention. 

  Identical node coordinates will later be assigned
  identical x or y physical coordinates by the 
  constraint solver.

  Attributes:
  * ix: the x grid coordinate
  * iy: the y grid coordinate
  """
  
  def __init__(self, ix: int, iy: int):
    """
    Creates a node with the given coordinate
    """
    self.ix = ix
    self.iy = iy

  def ixy(self) -> (int, int):
    """
    Returns the node coordinates as a tuple
    """
    return (self.ix, self.iy)

# A shortcut to generate a node

def n(ix: int, iy: int) -> Node:
  return Node(ix, iy)

