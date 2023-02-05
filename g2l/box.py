
import klayout.db as kl
import typing

class Box(object):

  """
  Represents a box sitting on the abstract layout grid and layer

  A box spans a range of horizontal and vertical grid points
  from ix1 to ix2 (inclusive) in horizontal direction and 
  from iy1 to iy2 (inclusive) in vertical direction.
  So the box is basically an abstract box.

  The physical dimensions are determined finally by the 
  positions of these grid coordinates, folded with the footprint
  box. The footprint box is a box normalized to 0,0 grid location
  and is given as a KLayout DBox object. The final dimensions
  are determined by shifting and stretching this box according
  to the physical grid locations.

  The layer is an integer value which defines the physical
  layer. The values are technology specific.
  """
  
  def __init__(self, ix1: int, iy1: int, ix2: int, iy2: int, box: kl.DBox, layer: int):
    """
    Creates a Box object

    :param ix1: the left abstract grid coordinate
    :param iy1: the bottom abstract grid coordinate
    :param ix2: the right abstract grid coordinate
    :param iy2: the top abstract grid coordinate
    :param box: the footprint box
    :param layer: the layer the box sits at
    """

    self.ix1 = ix1
    self.iy1 = iy1
    self.ix2 = ix2
    self.iy2 = iy2
    self.layer = layer
    self.box = box

  def ixory1(self, h: bool) -> int:
    """
    Internally used to get ix1 or iy1
    """
    return self.ix1 if h else self.iy1

  def iyorx1(self, h: bool) -> int:
    """
    Internally used to get iy1 or ix1
    """
    return self.iy1 if h else self.ix1

  def ixory2(self, h: bool) -> int:
    """
    Internally used to get ix2 or iy2
    """
    return self.ix2 if h else self.iy2

  def iyorx2(self, h: bool) -> int:
    """
    Internally used to get iy2 or ix2
    """
    return self.iy2 if h else self.ix2

  def xorymin(self, h: bool) -> int:
    """
    Internally used to get the minimum x or y value
    """
    return self.box.left if h else self.box.bottom

  def yorxmin(self, h: bool) -> int:
    """
    Internally used to get the minimum y or x value
    """
    return self.box.bottom if h else self.box.left

  def xorymax(self, h: bool) -> int:
    """
    Internally used to get the maximum x or y value
    """
    return self.box.right if h else self.box.top

  def yorxmax(self, h: bool) -> int:
    """
    Internally used to get the maximum y or x value
    """
    return self.box.top if h else self.box.right

  def __repr__(self) -> str:
    """
    Returns the string representation
    """
    return f"{self.ix1}/{self.iy1}..{self.ix2}/{self.iy2} layer={self.layer} box={str(self.box)}"

  def edge(self, sx: int, sy: int) -> kl.DEdge:
    """
    Gets one edge of the footprint box

    This method is used internally for constraint
    solving.

    Sides are:
    * sx = -1, sy = 0: left side
    * sx = 1, sy = 0: right side
    * sx = 0, sy = -1: bottom side
    * sx = 0, sy = 1: top side
    """
    if sy == 0:
      x = self.box.left + 0.5 * (sx + 1) * self.box.width
      return kl.DEdge(x, box.bottom, x, box.top)
    else:
      y = self.box.bottom + 0.5 * (sy + 1) * self.box.height
      return kl.DEdge(box.left, y, box.right, y)

