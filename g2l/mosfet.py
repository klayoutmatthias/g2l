
from .component import Component
from .tech import Tech
from .box import Box
from .node import Node
import klayout.db as kl

class MOSFET(Component):

  """
  This component defines a classical planar MOSFET

  This device needs three nodes for gate, source and drain. 
  It also defines two layers for the gate (poly) and active area
  (active).

  The device has two physical parameters width and length.

  The technology parameters will be taken from the 
  technology singleton (Tech.mosfets).
  """

  def __init__(self, gate_node: Node, source_node: Node, drain_node: Node, width: float, length: float):

    """
    Creates a MOSFET device

    :param gate_node: the abstract coordinates for the gate
    :param source_node: the abstract coordinates for the source
    :param drain_node: the abstract coordinates for the drain
    :param width: the transistor width
    :param length: the transistor length
    """

    self.mosfet_tech_definitions = Tech.mosfets

    self.gate_node = gate_node
    (self.source_node, self.drain_node) = (source_node, drain_node)

    self.width = width
    self.length = length
    self.poly_layer = self.mosfet_tech_definitions.poly_layer()
    self.active_layer = self.mosfet_tech_definitions.active_layer()

  def nodes(self) -> [Node]:
    """
    Reimplementation of Components.nodes
    """
    # NOTE: we normalize for left-to-right or bottom-to-top order
    if self.source_node.ixy() < self.drain_node.ixy():
      (sd1, sd2) = (self.source_node, self.drain_node)
    else:
      (sd2, sd1) = (self.source_node, self.drain_node)
    return [ sd1, self.gate_node, sd2 ]

  def layers(self) -> [int]:
    return [ self.active_layer, self.poly_layer ]

  def via_bottom_layer(self) -> int:
    return self.active_layer

  def boxes(self, graph) -> [Box]:

    """
    Builds the boxes for the MOSFET device

    This alorithm is mainly controlled by the "source_drain_active_width" and
    "gate_extensions" value from the technology singleton (Tech.mosfets).
    """

    sd_width = self.mosfet_tech_definitions.source_drain_active_width()
    sd_box = kl.DBox(kl.DPoint(-0.5 * sd_width, -0.5 * self.width), kl.DPoint(0.5 * sd_width, 0.5 * self.width))

    gate_extension = self.mosfet_tech_definitions.gate_extension()
    gate_box = kl.DBox(kl.DPoint(), kl.DPoint()).enlarged(0.5 * self.length, 0.5 * self.width + gate_extension)

    (sn, gn, dn) = self.nodes()

    return [ Box(sn.ix, sn.iy, dn.ix, dn.iy, sd_box, self.active_layer),
             Box(gn.ix, gn.iy, gn.ix, gn.iy, gate_box, self.poly_layer) ]

