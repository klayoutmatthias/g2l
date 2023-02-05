
from .node import Node
from .box import Box
import klayout.db as kl

class Component(object):

  """
  This class represents a "component" on the abstract grid

  A component is an object that spans a range of grid 
  points and consists of a collection of boxes.

  Components can be wires, vias or devices.

  The basic ability of a component is to declare a number
  a boxes from a component definition. For example a via
  spans a single grid node and delivers boxes for bottom
  conductor, top conductor and the via cut.

  Initially, the boxes are abstract ones, but the component
  needs to be able to deliver some final geometry after the
  grid coordinates have been determined by the solver.
  This is a separate step to allow refinement - e.g. the 
  via component will generate via arrays in that step.

  The "Component" class is the base class for all components.
  """

  def __init__(self):
    pass

  def nodes(self) -> [Node]:
    """
    Returns a list of nodes that the component attaches to

    By convention, the x or y values of the nodes shall be
    sorted in ascending order and there shall be either
    horizontal (all y values identical) or vertical (all
    x values identical) orientation.
    """
    return []

  def layers(self) -> [int]:
    """
    Returns a list of layers the component uses
    """
    return {}

  def boxes(self, graph) -> [Box]:
    """
    Returns the abstract boxes the component is made of

    :param graph: the graph object (Graph)
    """
    return []

  def via_bottom_layer(self) -> int:
    """
    For via components: returns the bottom layer
    """
    return None

  def via_top_layer(self) -> int:
    """
    For via components: returns the top layer
    """
    return None

  def is_horizontal(self) -> bool:
    """
    Returns a value indicating whether the component has horizonal orientation
    """
    return self.nodes()[0].iy == self.nodes()[-1].iy;

  # default implementation, based on the outline boxes
  def geometry(self, graph, x_coordinates: { int: float }, y_coordinates: { int: float }) -> [ [int, kl.DBox] ]:
    """
    Renders a list of physical boxes
    :param graph: the graph object (Graph)
    :param x_coordinates: gives physical coordinates for abstract ones
    :param y_coordinates: gives physical coordinates for abstract ones

    :returns A list of [ layer, physical box ] pairs with the final geometry
    """
    return self.geometry_for_boxes(x_coordinates, y_coordinates, self.boxes(graph))

  @staticmethod
  def geometry_for_boxes(x_coordinates: { int: float }, y_coordinates: { int: float }, boxes: [Box]) -> [ [int, kl.DBox] ]:
    """
    Renders a list of physical boxes from given abstract boxes

    :param x_coordinates: gives physical coordinates for abstract ones
    :param y_coordinates: gives physical coordinates for abstract ones
    :param boxes: A list of abstract boxes

    :returns A list of [ layer, physical box ] pairs with the final geometry
    """
    return [ [ b.layer, b.box * kl.DBox(x_coordinates[b.ix1], y_coordinates[b.iy1], x_coordinates[b.ix2], y_coordinates[b.iy2]) ] for b in boxes ]

