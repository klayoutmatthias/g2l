
from .component import Component
from .box import Box
import klayout.db as kl

# a wire implementation
class Wire(Component):

  def __init__(self, width, layer, v1, v2):
    # TODO: assert that v1.layer == v2.layer and v1.ix == v2.ix || v1.iy == v2.iy
    if v1.ix > v2.ix or v1.iy > v2.iy:
      (self.v1, self.v2) = (v2, v1)
    else:
      (self.v1, self.v2) = (v1, v2)
    self.width = width
    self.layer = layer

  def layers(self):
    return [ self.layer ]

  def via_bottom_layer(self):
    return self.layer

  def via_top_layer(self):
    return self.layer

  def nodes(self):
    return [ self.v1, self.v2 ]

  def boxes(self, graph):
    box1 = self.min_box_per_node(graph, self.v1)
    box2 = self.min_box_per_node(graph, self.v2)
    if self.is_horizontal():
      wire_box = kl.DBox(kl.DPoint(box1.left, -0.5 * self.width), kl.DPoint(box2.right, 0.5 * self.width))
    else:
      wire_box = kl.DBox(kl.DPoint(-0.5 * self.width, box1.bottom), kl.DPoint(0.5 * self.width, box2.top))
    return [ Box(self.v1.ix, self.v1.iy, self.v2.ix, self.v2.iy, wire_box, self.layer) ]

  # computes the minimum box as imposed by perpendicular wires
  def min_box_per_node(self, graph, v):
    box = kl.DBox(0, 0, 0, 0)
    for c in graph.components_for_node(v.ixy()):
      if type(c) is Wire and c.layer in self.layers():
        if c.is_horizontal():
          box += kl.DBox(0, -0.5 * c.width, 0, 0.5 * c.width)
        else:
          box += kl.DBox(-0.5 * c.width, 0, 0.5 * c.width, 0)
    return box

