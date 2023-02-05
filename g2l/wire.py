
from .component import Component
from .box import Box
from .node import Node
import klayout.db as kl

class Wire(Component):

  """
  A component representing a wire

  A wire is a horizontal or vertical connection between two nodes.
  A wire has a width and a layer that it runs on.
  """

  def __init__(self, width: float, layer: int, n1: Node, n2: Node):

    """
    Creates a wire

    :param width: the width of the wire
    :param layer: the layer the wire runs on (layer number)
    :param n1: The start position in abstract coordinates
    :param n2: The end position in abstract coordinates

    The wire needs to be either horizontal or vertical, so that
    n1.ix == n2.ix or n1.iy == n2.iy.
    """

    if n1.ix != n2.ix and n1.iy != n2.iy:
      raise Exception("A wire needs to be either horizontal or vertical")

    if n1.ix > n2.ix or n1.iy > n2.iy:
      (self.n1, self.n2) = (n2, n1)
    else:
      (self.n1, self.n2) = (n1, n2)

    self.width = width
    self.layer = layer

  def layers(self) -> [int]:
    """
    Reimplements the Component interface
    """
    return [ self.layer ]

  def via_bottom_layer(self) -> int:
    """
    Indicates that this component delivers a layer suitable as via bottom layer
    """
    return self.layer

  def via_top_layer(self) -> int:
    """
    Indicates that this component delivers a layer suitable as via top layer
    """
    return self.layer

  def nodes(self) -> [Node]:
    """
    Reimplements the Component interface
    """
    return [ self.n1, self.n2 ]

  def boxes(self, graph) -> [Box]:
    """
    Delivers the abstract box for the wire
    """

    box1 = self._min_box_per_node(graph, self.n1)
    box2 = self._min_box_per_node(graph, self.n2)
    if self.is_horizontal():
      wire_box = kl.DBox(kl.DPoint(box1.left, -0.5 * self.width), kl.DPoint(box2.right, 0.5 * self.width))
    else:
      wire_box = kl.DBox(kl.DPoint(-0.5 * self.width, box1.bottom), kl.DPoint(0.5 * self.width, box2.top))

    ix1 = min(self.n1.ix, self.n2.ix)
    ix2 = max(self.n1.ix, self.n2.ix)
    iy1 = min(self.n1.iy, self.n2.iy)
    iy2 = max(self.n1.iy, self.n2.iy)

    return [ Box(ix1, iy1, ix2, iy2, wire_box, self.layer) ]

  def _min_box_per_node(self, graph, v: Node) -> kl.DBox:
    """
    Computes the minimum box as imposed by perpendicular wires
    """

    box = kl.DBox(0, 0, 0, 0)
    for c in graph.components_for_node(v.ixy()):
      if type(c) is Wire and c.layer in self.layers():
        if c.is_horizontal():
          box += kl.DBox(0, -0.5 * c.width, 0, 0.5 * c.width)
        else:
          box += kl.DBox(-0.5 * c.width, 0, 0.5 * c.width, 0)

    return box

