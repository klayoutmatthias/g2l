
from .component import Component
from .tech import Tech
from .box import Box
import klayout.db as kl

class MOSFET(Component):

  def __init__(self, gate_node, source_node, drain_node, poly_layer, diff_layer, width, length):

    # TODO: assert that gate_node.iy == source_node.iy and gate_node.iy == drain_node.iy
    # (or generalize for horizontal orientation)
    self.gate_node = gate_node

    # normalize "source" to be left
    if source_node.ix < drain_node.ix:
      (self.source_node, self.drain_node) = (source_node, drain_node)
    else:
      (self.source_node, self.drain_node) = (drain_node, source_node)

    self.width = width
    self.length = length
    self.poly_layer = poly_layer
    self.diff_layer = diff_layer

    self.mosfet_tech_definitions = Tech.mosfets

  def nodes(self):
    return [ self.source_node, self.gate_node, self.drain_node ]

  def layers(self):
    return [ self.diff_layer, self.poly_layer ]

  def via_bottom_layer(self):
    return self.diff_layer

  def boxes(self, graph):

    sd_width = self.mosfet_tech_definitions.source_drain_active_width()
    sd_box = kl.DBox(kl.DPoint(-0.5 * sd_width, -0.5 * self.width), kl.DPoint(0.5 * sd_width, 0.5 * self.width))

    gate_extension = self.mosfet_tech_definitions.gate_extension()
    gate_box = kl.DBox(kl.DPoint(), kl.DPoint()).enlarged(0.5 * self.length, 0.5 * self.width + gate_extension)

    return [ Box(self.source_node.ix, self.source_node.iy, self.drain_node.ix, self.drain_node.iy, sd_box, self.diff_layer),
             Box(self.gate_node.ix, self.gate_node.iy, self.gate_node.ix, self.gate_node.iy, gate_box, self.poly_layer) ]

