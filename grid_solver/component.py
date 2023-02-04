
import klayout.db as kl

# base class for a component
class Component(object):

  def __init__(self):
    pass

  def nodes(self):
    return []

  def layers(self):
    return {}

  def boxes(self, graph):
    return []

  def via_bottom_layer(self):
    return None

  def via_top_layer(self):
    return None

  def is_horizontal(self):
    return self.nodes()[0].iy == self.nodes()[-1].iy;

  # default implementation, based on the outline boxes
  def geometry(self, graph, x_coordinates, y_coordinates):
    return self.geometry_for_boxes(x_coordinates, y_coordinates, self.boxes(graph))

  def geometry_for_boxes(self, x_coordinates, y_coordinates, boxes):
    return [ [ b.layer, b.box * kl.DBox(x_coordinates[b.ix1], y_coordinates[b.iy1], x_coordinates[b.ix2], y_coordinates[b.iy2]) ] for b in boxes ]

