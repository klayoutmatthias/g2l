
from .component import Component

class Graph(object):

  """
  This class represents the abstract layout graph

  The graph is basically a collection of components
  which connect to each other through abstract layout
  nodes.

  Public attributes:
  * components: The list of components
  """

  def __init__(self):
    self.components = []
    self.x_indexes = set()
    self.y_indexes = set()
    self.components_per_layer = {}
    self.components_per_index = {}

  def add(self, component: Component):
    """
    Adds a new component to the graph
    """

    self.components.append(component)

    for v in component.nodes():

      self.x_indexes.add(v.ix)
      self.y_indexes.add(v.iy)

      ixy = v.ixy()
      if not ixy in self.components_per_index:
        self.components_per_index[ixy] = [component]
      else:
        self.components_per_index[ixy].append(component)

    for l in component.layers():

      if not l in self.components_per_layer:
        self.components_per_layer[l] = [component]
      else:
        self.components_per_layer[l].append(component)


  def components_for_node(self, ixy: (int, int)) -> [Component]:
    """
    Gets the components attached to a certain node
    """
    if ixy not in self.components_per_index:
      return []
    else:
      return self.components_per_index[ixy]
      
