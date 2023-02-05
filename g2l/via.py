
from .component import Component
from .tech import Tech
from .box import Box
import klayout.db as kl

class Via(Component):
  
  def __init__(self, node, bottom_layer, via_layer, top_layer):
    self.node = node
    self.bottom_layer = bottom_layer
    self.via_layer = via_layer
    self.top_layer = top_layer
    self.via_tech_definitions = Tech.vias

  def nodes(self):
    return [ self.node ]

  def layers(self):
    return [ self.bottom_layer, self.via_layer, self.top_layer ]

  # for the boxes we use a summarized definition of the farm vias
  def boxes(self, graph):

    widths = self.get_widths(graph)

    (bbox, vbox, tbox) = self.via_tech_definitions.boxes(self.bottom_layer, self.top_layer, widths[0], widths[1])

    v = self.node

    return [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_layer), 
             Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_layer),
             Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_layer) ]

  # for the geometry we use the detailed geometry with the farm vias
  def geometry(self, graph, x_coordinates, y_coordinates):

    widths = self.get_widths(graph)

    (bbox, unused, tbox) = self.via_tech_definitions.boxes(self.bottom_layer, self.top_layer, widths[0], widths[1])
    detailed_vboxes = self.via_tech_definitions.via_geometry(self.bottom_layer, self.top_layer, widths[0], widths[1])

    v = self.node

    geometry = [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_layer), 
                 Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_layer) ]

    for vbox in detailed_vboxes:
      geometry.append(Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_layer))

    return self.geometry_for_boxes(x_coordinates, y_coordinates, geometry)

  def get_widths(self, graph):

    widths = [ [ None, None, None, None ], [ None, None, None, None ] ]

    # analyze wires
    for c in graph.components_for_node(self.node.ixy()):
      li = -1
      if c.via_bottom_layer() == self.bottom_layer:
        li = 0
      elif c.via_top_layer() == self.top_layer:
        li = 1
      if li >= 0:
        widths[li][self.direction_index(c)] = c.width

    return widths

  def direction_index(self, component):
    if component.is_horizontal():
      if component.nodes()[0].ix < self.node.ix:
        return 0
      else:
        return 2
    else:
      if component.nodes()[0].iy < self.node.iy:
        return 1
      else:
        return 3

