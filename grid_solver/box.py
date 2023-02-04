
import klayout.db as kl

# A geometrical box

class Box(object):
  
  def __init__(self, ix1, iy1, ix2, iy2, box, layer):
    self.ix1 = ix1
    self.iy1 = iy1
    self.ix2 = ix2
    self.iy2 = iy2
    self.layer = layer
    self.box = box

  def ixory1(self, h):
    return self.ix1 if h else self.iy1

  def iyorx1(self, h):
    return self.iy1 if h else self.ix1

  def ixory2(self, h):
    return self.ix2 if h else self.iy2

  def iyorx2(self, h):
    return self.iy2 if h else self.ix2

  def xorymin(self, h):
    return self.box.left if h else self.box.bottom

  def yorxmin(self, h):
    return self.box.bottom if h else self.box.left

  def xorymax(self, h):
    return self.box.right if h else self.box.top

  def yorxmax(self, h):
    return self.box.top if h else self.box.right

  def __repr__(self):
    return f"{self.ix1}/{self.iy1}..{self.ix2}/{self.iy2} layer={self.layer} box={str(self.box)}"

  # side is:
  # sx  sy
  # -1  0    -> left
  # 1   0    -> right
  # 0   -1   -> bottom
  # 0   1    -> top
  def edge(self, sx, sy):
    if sy == 0:
      x = self.box.left + 0.5 * (sx + 1) * self.box.width
      return kl.DEdge(x, box.bottom, x, box.top)
    else:
      y = self.box.bottom + 0.5 * (sy + 1) * self.box.height
      return kl.DEdge(box.left, y, box.right, y)

