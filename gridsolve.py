
import klayout.db as kl
import math

# -------------------------------------------------------------

class TechRules(object):

  def __init__(self):
    pass

  # Returns the minimum space/separation for the given layer pair.
  # "layer1" can be identical to "layer2"
  def space_for(self, layer1, layer2):

    # @@@ demo, functional layers are:
    # 0: diff
    # 1: poly
    # 2: contact
    # 3: metal1
    # 4: via1
    # 5: metal2

    if layer1 == 0 and layer2 == 0:
      return 0.2   # diff space
    elif layer1 == 1 and layer2 == 1:
      return 0.2   # poly space
    elif layer1 == 1 and layer2 == 2:
      return 0.05  # poly/contact space
    elif layer1 == 2 and layer2 == 2:
      return 0.2   # contact space
    elif layer1 == 3 and layer2 == 3:
      return 0.2   # metal1 space
    elif layer1 == 4 and layer2 == 4:
      return 0.2   # via1 space
    elif layer1 == 5 and layer2 == 5:
      return 0.2   # metal2 space
    else:
      return None

  # gets the number of functional layer indexes
  def layers(self):
    # @@@
    return 6
    
  def default_wire_width(self, layer):

    if layer == 3:
      return 0.2
    elif layer == 5:
      return 0.2
    else:
      return None

# @@@
tech_rules = TechRules()


# Supplies an algorithm for defining the via enclosures and other via definitions

class ViaTechDefinitions(object):

  def __init__(self):
    pass

  # Gets the landing pad boxes
  # "bottom_widths" are the widths of the attached wires from [ left, bottom, right, top ]
  # ("None" indicates that there is no connection from that side)
  # "top_widths" is the same for the top layer.
  # The returned values need to be minimum boxes for bottom and top layers as a tuple.
  # The boxes are supposed to be 0,0 centered.
  def boxes(self, bottom_layer, top_layer, bottom_widths, top_widths):

    (bbox, tbox) = self.top_bottom_boxes(bottom_layer, top_layer, bottom_widths, top_widths)

    # for efficiency, we don't produce each single via, but just a common box
    vbox = kl.DBox()
    for b in self.via_geometry(bottom_layer, top_layer, bottom_widths, top_widths, bbox & tbox):
      vbox += b
    
    return (bbox, vbox, tbox)

  # Gets the via geometry
  # Parameters as in "boxes". The returned geometry objects are supposed to be 
  # created for a via at 0,0.
  def via_geometry(self, bottom_layer, top_layer, bottom_widths, top_widths):

    # Simple demo implementation with single dimension
    # @@@
    via_size = 0.14
    via_space = 0.2

    (bbox, tbox) = self.top_bottom_boxes(bottom_layer, top_layer, bottom_widths, top_widths)

    return self.create_farm_via(via_size, via_space, bbox & tbox)

  def top_bottom_boxes(self, bottom_layer, top_layer, bottom_widths, top_widths):

    # Simple demo implementation with plain enlargement
    # @@@
    enclosure = 0.05
    
    bw = max([ bottom_widths[i] or 0.0 for i in [1, 3] ])
    bh = max([ bottom_widths[i] or 0.0 for i in [0, 2] ])
    bbox = kl.DBox(-0.5 * bw, -0.5 * bh, 0.5 * bw, 0.5 * bh).enlarged(enclosure, enclosure)

    tw = max([ top_widths[i] or 0.0 for i in [1, 3] ])
    th = max([ top_widths[i] or 0.0 for i in [0, 2] ])
    tbox = kl.DBox(-0.5 * tw, -0.5 * th, 0.5 * tw, 0.5 * th).enlarged(enclosure, enclosure)

    return (bbox, tbox)

  # Creates a farm via (array) covering the given "via_box" with vias
  # with given size and space
  def create_farm_via(self, via_size, via_space, via_box):

    nx = max(1, math.floor(1e-10 + (via_box.width + via_space) / (via_size + via_space)))
    ny = max(1, math.floor(1e-10 + (via_box.height + via_space) / (via_size + via_space)))
  
    geometry = []
    for i in range(0, nx):
      for j in range(0, ny):
        x = (i - (nx - 1) * 0.5) * (via_size + via_space)
        y = (j - (ny - 1) * 0.5) * (via_size + via_space)
        geometry.append(kl.DBox(-0.5 * via_size, -0.5 * via_size, 0.5 * via_size, 0.5 * via_size).moved(x, y))
        
    return geometry

# @@@ 
via_tech_definitions = ViaTechDefinitions()


class MOSFETTechDefinitions(object):

  def __init__(self):
    pass

  # @@@ dummy definitions

  # the extension the gate poly needs to have over active area
  def poly_gate_extensions(self):
    return 0.05

  def source_drain_active_width(self):
    return 0.2
  
# @@@
mosfet_tech_definitions = MOSFETTechDefinitions()



# -------------------------------------------------------------

# a grid vertex
class Vertex(object):
  
  def __init__(self, ix, iy, layer)
    self.ix = ix
    self.iy = iy
    self.layer = layer

  def ixy(self):
    return (self.ix, self.iy)

# a geometrical box
class Box(object):
  
  def __init__(self, ix1, iy1, ix2, iy2, box, layer):
    self.ix1 = ix1
    self.iy1 = iy1
    self.ix2 = ix2
    self.iy2 = iy2
    self.layer = layer
    self.box = box

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

  
class Graph(object):

  def __init__(self):
    self.components = []
    self.x_indexes = set()
    self.y_indexes = set()
    self.components_per_layer = {}
    self.components_per_index = {}

  def add(self, component):

    self.components.add(component)

    for v in component.vertexes():

      self.x_indexes.add(v.ix)
      self.y_indexes.add(v.iy)

      if not v.layer in self.components_per_layer:
        self.components_per_layer[v.layer] = [component]
      else:
        self.components_per_layer[v.layer].append(component)

      ixy = v.ixy()
      if ixy in self.components_per_index:
        self.components_per_index[ixy] = [component]
      else:
        self.components_per_index[ixy].append(component)

  def components_for_vertex(self, ixy):
    if ixy not in self.components_per_index:
      return []
    else:
      return self.components_per_index[ixy]
      

# base class for a component
class Component(object):

  def __init__(self):
    pass

  def vertexes(self):
    return []

  def boxes(self, graph):
    return []

  # default implementation, based on the outline boxes
  def geometry(self, graph, x_coordinates, y_coordinates):
    return self.geometry_for_boxes(x_coordinates, y_coordinates, self.boxes(graph))

  def geometry_for_boxes(self, x_coordinates, y_coordinates, boxes):
    return [ b.box * kl.DBox(x_coordinates[b.ix1], y_coordinates[b.iy1], x_coordinates[b.ix2], y_coordinates[b.iy2]) for b in boxes ]


# a wire implementation
class Wire(Component):

  def __self__(self, width, v1, v2)
    # TODO: assert that v1.layer == v2.layer and v1.ix == v2.ix || v1.iy == v2.iy
    if self.v1.ix > self.v2.ix or self.v1.iy > self.v2.iy:
      (self.v1, self.v2) = (v2, v1)
    else:
      (self.v1, self.v2) = (v1, v2)
    self.width = width

  def vertexes(self):
    return [ self.v1, self.v2 ]

  def layer(self):
    return self.v1.layer;

  def is_horizontal(self):
    return self.v1.iy == self.v2.iy

  def boxes(self, graph):
    box1 = self.min_box_per_vertex(graph, self.v1)
    box2 = self.min_box_per_vertex(graph, self.v2)
    if self.is_horizontal():
      wire_box = kl.DBox(kl.DPoint(box1.left, -0.5 * width), kl.DPoint(box2.right, 0.5 * width))
    else:
      wire_box = kl.DBox(kl.DPoint(-0.5 * width, box1.bottom), kl.DPoint(0.5 * width, box2.top))
    return [ Box(self.v1.ix, self.v1.iy, self.v2.ix, self.v2.iy, wire_box, self.layer()) ]

  # computes the minimum box as imposed by perpendicular wires
  def min_box_per_vertex(self, graph, v):
    box = kl.DBox(0, 0, 0, 0)
    for c in graph.components_for_vertex(v.ixy()):
      if type(c) is Wire and c.layer() == self.layer():
        if c.is_horizontal():
          box += kl.DBox(0, -0.5 * c.width, 0, 0.5 * c.width)
        else:
          box += kl.DBox(-0.5 * c.width, 0, 0.5 * c.width, 0)
    return box


class Via(Component):
  
  def __init__(self, bottom_vertex, top_vertex, via_vertex):
    # TODO: assert that bottom_vertex.ixy() == top_vertex.ixy() == via_vertex.ixy()
    self.bottom_vertex = bottom_vertex
    self.top_vertex = top_vertex
    self.via_vertex = via_vertex
    self.via_tech_definitions = via_tech_definitions

  def vertexes(self):
    return [ self.bottom_vertex, self.top_vertex ]

  # for the boxes we use a summarized definition of the farm vias
  def boxes(self, graph):

    widths = get_widths(graph)

    (bbox, vbox, tbox) = self.via_tech_definitions.boxes(self.bottom_vertex.layer, self.top_vertex.layer, widths[0], widths[1])

    v = self.bottom_vertex

    return [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_vertex.layer), 
             Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_vertex.layer),
             Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_vertex.layer) ]

  # for the geometry we use the detailed geometry with the farm vias
  def geometry(self, graph):

    widths = get_widths(graph)

    (bbox, -, tbox) = self.via_tech_definitions.boxes(self.bottom_vertex.layer, self.top_vertex.layer, widths[0], widths[1])
    detailed_vboxes = self.via_tech_definitions.via_geometry(self.bottom_vertex.layer, self.top_vertex.layer, widths[0], widths[1])

    v = self.bottom_vertex

    geometry = [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_vertex.layer), 
                 Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_vertex.layer) ]

    for vbox in detailed_vboxes:
      geometry.append(Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_vertex.layer))

    return geometry

  def get_widths(self, graph):

    widths = [ [ None ] * 4 ] * 2

    # analyze wires
    for c in graph.components_for_vertex(v.ixy()):
      if type(c) is Wire:
        li = -1
        if c.layer() == self.bottom_vertex.layer():
          li = 0
        elif c.layer() == self.top_vertex.layer():
          li = 1
        if li >= 0:
          widths[li][self.direction_index(c)] = c.width

    return widths

  def direction_index(self, wire):
    if wire.is_horizontal():
      if wire.v1.ix < self.bottom_vertex.ix:
        return 0
      else
        return 2
    else:
      if wire.v1.iy < self.bottom_vertex.iy:
        return 1
      else
        return 3


class MOSFET(Component):

  def __init__(self, gate_vertex, source_vertex, drain_vertex, width, length):

    # TODO: assert that gate_vertex.iy == source_vertex.iy and gate_vertex.iy == drain_vertex.iy
    # (or generalize for horizontal orientation)
    self.gate_vertex = gate_vertex

    # normalize "source" to be left
    if source_vertex.ix < drain_vertex.ix:
      (self.source_vertex, self.drain_vertex) = (source_vertex, drain_vertex)
    else:
      (self.source_vertex, self.drain_vertex) = (drain_vertex, source_vertex)

    self.width = width
    self.height = height
    # @@@ redundant
    self.poly_layer = self.gate_vertex.layer
    self.diff_layer = self.source_vertex.layer

    self.mosfet_tech_definitions = mosfet_tech_definitions

  def vertexes(self):
    return [ self.source_vertex, self.gate_vertex, self.drain_vertex ]

  def boxes(self, graph):

    sd_width = self.mosfet_tech_definitions.source_drain_active_width()
    sd_box = kl.DBox(kl.DPoint(-0.5 * sd_width, -0.5 * width), kl.DPoint(0.5 * sd_width, 0.5 * width))

    gate_box = kl.DBox(kl.DPoint(), kl.DPoint()).enlarged(0.5 * length, 0.5 * width)

    return [ Box(self.source_vertex.ix, self.source_vertex.iy, self.drain_vertex.ix, self.drain_vertex.iy, sd_box, self.diff_layer),
             Box(self.gate_vertex.ix, self.gate_vertex.iy, self.gate_vertex.ix, self.gate_vertex.iy, gate_box, self.gate_layer) ]


class ConstraintSolver(object):

  def __init__(self, graph):

    self.graph = graph
    self.ix = sort([ v for v in graph.x_indexes ])
    self.iy = sort([ v for v in graph.y_indexes ])
    self.x_coordinates = None
    self.y_coordinates = None

    self.tech_rules = tech_rules

  def solve(self, initial_grid_x = 0.4, initial_grid_y = 0.5):

    self.x_coordinates = {}
    self.y_coordinates = {}
    for i in self.ix:
      self.x_coordinates[i] = i * initial_grid_x
    for i in self.iy:
      self.y_coordinates[i] = i * initial_grid_y

    threshold = 0.05 # @@@?
    max_iter = 10

    delta = threshold
    niter = 0
    
    while delta > threshold and niter < max_iter:

      xc = self.x_coordinates.copy()
      yc = self.y_coordinates.copy()

      self.compute_coordinates_h
      self.compute_coordinates_v

      niter += 1
      delta = diff(xc, self.x_coordinates) + diff(yc, self.y_coordinates)

      print(f"@@@ iter={iter} -> delta={delta}")

    return niter < max_item

  # generates the layout
  # layout and cell are layout and top cell objects respectively
  # layers are the layer indexes in the layout by functional layer index
  def produce(self, layout, cell, layers):

    for layer in range(0, self.tech_rules.layers()):

      shapes = cell.shapes(layers[layer])

      for c in self.graph.components_per_layer(layer):
        for g in c.geometry(layer, self.graph, self.x_coordinates, self.y_coordinates):
          shapes.insert(g)


  def diff(self, a, b):
    d = 0.0
    for i in len(a):
      d += math.sqrt((a[i] - b[i]) ** 2)
    return d


  def compute_coordinates_h(self):

    prev_boxes = []

    for i in self.ix:

      current_boxes = []
      for j in self.iy:
        for c in self.graph.components_for_vertex(( i, j )):
          for b in c.boxes(self):
            if b.ix1 == i:
              current_boxes.append(b)

      # NOTE: this is rather brute force
      min_coord = 0.0
      for cb in current_boxes:
        for pb in prev_boxes:
          space = self.tech_rules.space(pb.layer, cb.layer)
          if space is not None:
            coord = self.compute_coord_h(space, pb, cb)
            if coord is not None and coord > min_coord:
              min_coord = coord

      self.x_coordinates[i] = min_coord

      prev_boxes += current_boxes

        
  def compute_coord_h(self, space, b1, b2):

    if b1.ix2 >= b2.ix1:
      return None

    dbox1 = b1.box * kl.DBox(self.x_coordinates[b1.ix1], self.y_coordinates[b.iy1], self.x_coordinates[b1.ix2], self.y_coordinates[b1.iy2])
    dbox2 = b2.box * kl.DBox(0.0, self.y_coordinates[b2.iy1], 0.0, self.y_coordinates[b2.iy2])

    dbox1 = dbox1.enlarged(space, space)

    # no vertical overlap
    if dbox1.bottom > dbox2.top - 1e-10 or dbox1.top < dbox2.bottom + 1e-10:
      return None 
    
    return dbox1.right - dbox2.left

  def compute_coordinates_v(self):

    prev_boxes = []

    for i in self.iy:

      current_boxes = []
      for j in self.ix:
        for c in self.graph.components_for_vertex(( j, i )):
          for b in c.boxes(self):
            if b.iy1 == i:
              current_boxes.append(b)

      # NOTE: this is rather brute force
      min_coord = 0.0
      for cb in current_boxes:
        for pb in prev_boxes:
          space = self.tech_rules.space(pb.layer, cb.layer)
          if space is not None:
            coord = self.compute_coord_v(space, pb, cb)
            if coord is not None and coord > min_coord:
              min_coord = coord

      self.y_coordinates[i] = min_coord

      prev_boxes += current_boxes

        
  def compute_coord_v(self, space, b1, b2):

    if b1.iy2 >= b2.iy1:
      return None

    dbox1 = b1.box * kl.DBox(self.x_coordinates[b1.ix1], self.y_coordinates[b.iy1], self.x_coordinates[b1.ix2], self.y_coordinates[b1.iy2])
    dbox2 = b2.box * kl.DBox(self.x_coordinates[b2.ix1], 0.0, self.x_coordinates[b2.ix2], 0.0)

    dbox1 = dbox1.enlarged(space, space)

    # no vertical overlap
    if dbox1.left > dbox2.right - 1e-10 or dbox1.right < dbox2.left + 1e-10:
      return None 
    
    return dbox1.top - dbox2.bottom


# ------------------------------------------------------------------

# a test rig

graph = Graph()

diff = 0
contact = 1
poly = 2
metal1 = 3
via1 = 4
metal2 = 5

metal1w = 0.2
metal2w = 0.2
polyw = 0.13

l = 0.13
wp = 0.6
wn = 0.4

graph.add(MOSFET(Vertex(1, 3, poly), Vertex(0, 3, diff), Vertex(2, 3, diff), wp, l))
graph.add(MOSFET(Vertex(3, 3, poly), Vertex(4, 3, diff), Vertex(2, 3, diff), wp, l))
graph.add(MOSFET(Vertex(5, 3, poly), Vertex(4, 3, diff), Vertex(6, 3, diff), wp, l))
graph.add(MOSFET(Vertex(1, 1, poly), Vertex(0, 1, diff), Vertex(2, 1, diff), wn, l))
graph.add(MOSFET(Vertex(3, 1, poly), Vertex(4, 1, diff), Vertex(2, 1, diff), wn, l))
graph.add(MOSFET(Vertex(5, 1, poly), Vertex(4, 1, diff), Vertex(6, 1, diff), wn, l))

graph.add(Wire(metal1w, Vertex(0, 4, metal1), Vertex(0, 5, metal1)))
graph.add(Wire(metal1w, Vertex(4, 4, metal1), Vertex(4, 5, metal1)))
graph.add(Wire(0.5, Vertex(0, 5, metal1), Vertex(4, 5, metal1)))
graph.add(Wire(metal1w, Vertex(0, 0, metal1), Vertex(0, 1, metal1)))
graph.add(Wire(metal1w, Vertex(4, 0, metal1), Vertex(4, 1, metal1)))
graph.add(Wire(0.5, Vertex(0, 0, metal1), Vertex(4, 0, metal1)))

graph.add(Wire(0.5, Vertex(2, 1, metal1), Vertex(2, 2, metal1)))
graph.add(Wire(0.5, Vertex(2, 2, metal1), Vertex(2, 3, metal1)))

graph.add(Wire(polyw, Vertex(1, 1, poly), Vertex(1, 2, poly)))
graph.add(Wire(polyw, Vertex(1, 2, poly), Vertex(1, 3, poly)))
graph.add(Wire(polyw, Vertex(1, 2, poly), Vertex(2, 2, poly)))
graph.add(Wire(polyw, Vertex(2, 1, poly), Vertex(2, 2, poly)))
graph.add(Wire(polyw, Vertex(2, 2, poly), Vertex(2, 3, poly)))

graph.add(Wire(polyw, Vertex(2, 2, poly), Vertex(2, 3, poly)))

graph.add(Via(Vertex(3, 2, poly), Vertex(3, 2, metal1), Vertex(3, 2, contact)))

graph.add(Wire(0.5, Vertex(3, 2, metal1), Vertex(6, 2, metal1)))
graph.add(Wire(0.5, Vertex(6, 1, metal1), Vertex(6, 2, metal1)))
graph.add(Wire(0.5, Vertex(6, 2, metal1), Vertex(6, 3, metal1)))

graph.add(Wire(polyw, Vertex(5, 1, poly), Vertex(5, 2, poly)))
graph.add(Wire(polyw, Vertex(5, 2, poly), Vertex(5, 3, poly)))
graph.add(Wire(polyw, Vertex(5, 2, poly), Vertex(7, 2, poly)))


solver = ConstraintSolver(graph)
solver.solve()

layout = kl.Layout()
top_cell = layout.create_cell("TOP")

layers = {}
layers[diff]    = layout.layer(2, 0)
layers[poly]    = layout.layer(7, 0)
layers[contact] = layout.layer(14, 0)
layers[metal1]  = layout.layer(15, 0)
layers[via1]    = layout.layer(16, 0)
layers[metal2]  = layout.layer(17, 0)

solver.produce(layout, top_cell, layers)

layout.write("generated.gds")

