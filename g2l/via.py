
from .component import Component
from .tech import Tech
from .box import Box
from .node import Node
import klayout.db as kl

class Via(Component):

  """
  Represents a via 

  A via sits one a single node and is specified by the
  node position and three layers: bottom layer, via (cut) layer 
  and top layer.

  The via geometry is defined by the wire widths attaching to
  the via at the bottom and the top. Via array generation is 
  supported by delivery of a coarse hull first and detailed
  geometry later.

  The main logic of via generation is delegated to the 
  technology singleton (Tech.vias), because the actual
  via generation is highly technology specific in terms
  of extensions or landing pad generation.
  """
  
  def __init__(self, node: Node, bottom_layer: int, via_layer: int, top_layer: int):

    """
    Creates a via object

    :param node: the node the via sits at
    :param bottom_layer: the bottom layer number
    :param via_layer: the via (cut) layer number
    :param top_layer: the top layer number
    """

    self.node = node
    self.bottom_layer = bottom_layer
    self.via_layer = via_layer
    self.top_layer = top_layer
    self.via_tech_definitions = Tech.vias

  def nodes(self) -> [Node]:
    """
    Reimplementation of the Component interface
    """
    return [ self.node ]

  def layers(self) -> [int]:
    """
    Reimplementation of the Component interface
    """
    return [ self.bottom_layer, self.via_layer, self.top_layer ]

  def boxes(self, graph) -> [Box]:
    """
    Gets the coarse form of the via boxes

    The main implementation is delegated to the technology singleton
    (Tech.vias).

    The basic information for this is the width of the wires attaching from
    left, bottom, right and top to the bottom and top conductors
    of the via. This allows the technology delegate to make a 
    decision about extensions needed for a specific configuration.
    """

    widths = self._get_widths(graph)

    (bbox, vbox, tbox) = self.via_tech_definitions.boxes(self.bottom_layer, self.top_layer, widths[0], widths[1])

    v = self.node

    return [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_layer), 
             Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_layer),
             Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_layer) ]

  def geometry(self, graph, x_coordinates: { int: float }, y_coordinates: { int: float }) -> [Box]:
    """
    Gets the detailed via geometry for actual coordinates

    This method also implements via arrays.
    The main implementation is delegated to the technology singleton
    (Tech.vias).
    """

    widths = self._get_widths(graph)

    (bbox, unused, tbox) = self.via_tech_definitions.boxes(self.bottom_layer, self.top_layer, widths[0], widths[1])
    detailed_vboxes = self.via_tech_definitions.via_geometry(self.bottom_layer, self.top_layer, widths[0], widths[1])

    v = self.node

    geometry = [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_layer), 
                 Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_layer) ]

    for vbox in detailed_vboxes:
      geometry.append(Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_layer))

    return self.geometry_for_boxes(x_coordinates, y_coordinates, geometry)

  def _get_widths(self, graph) -> [ [float], [float] ]:
    """
    Gets the widths of attaching wires

    Returns four width values or None in case no wire
    attaches from this side for left, bottom, right and top side.
    Two such sets are returned from bottom and top metal.
    """

    widths = [ [ None, None, None, None ], [ None, None, None, None ] ]

    # analyze wires
    for c in graph.components_for_node(self.node.ixy()):
      li = -1
      if c.via_bottom_layer() == self.bottom_layer:
        li = 0
      elif c.via_top_layer() == self.top_layer:
        li = 1
      if li >= 0:
        widths[li][self._direction_index(c)] = c.width

    return widths

  def _direction_index(self, component):
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

