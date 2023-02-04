
import klayout.db as kl
import math

# -------------------------------------------------------------

class TechRules(object):

  def __init__(self):
    pass

  # Returns the minimum space/separation for the given layer pair.
  # "layer1" can be identical to "layer2"
  def space(self, layer1, layer2):

    # @@@ demo, functional layers are:
    # 0: diff
    # 1: contact
    # 2: poly
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

    # For efficiency, we don't produce each single via, but just a common box on the cut layer
    # we will later replace the common box by individual boxes for the farm vias.
    vbox = kl.DBox()
    for b in self.via_geometry(bottom_layer, top_layer, bottom_widths, top_widths):
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

    # Simple demo implementation

    top_min_dim = 0.2
    bottom_min_dim = 0.2

    if top_layer == 3:  # contact
      top_min_dim = 0.2
      bottom_min_dim = 0.13
    
    bw = max([ bottom_widths[i] or 0.0 for i in [1, 3] ])
    tw = max([ top_widths[i] or 0.0 for i in [1, 3] ])
    if bw == 0.0:
      bw = tw
    if tw == 0.0:
      tw = bw

    bh = max([ bottom_widths[i] or 0.0 for i in [0, 2] ])
    th = max([ top_widths[i] or 0.0 for i in [0, 2] ])
    if bh == 0.0:
      bh = th
    if th == 0.0:
      th = bh

    bw = max(bw, bottom_min_dim)
    bh = max(bh, bottom_min_dim)

    tw = max(tw, top_min_dim)
    th = max(th, top_min_dim)

    bbox = kl.DBox(-0.5 * bw, -0.5 * bh, 0.5 * bw, 0.5 * bh)
    tbox = kl.DBox(-0.5 * tw, -0.5 * th, 0.5 * tw, 0.5 * th)

    return (bbox, tbox)

  # Creates a farm via (array) covering the given "via_box" with vias
  # with given size and space
  def create_farm_via(self, via_size, via_space, via_box):

    nx = max(1, math.floor(1e-10 + (via_box.width() + via_space) / (via_size + via_space)))
    ny = max(1, math.floor(1e-10 + (via_box.height() + via_space) / (via_size + via_space)))
  
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
  
  def gate_extension(self):
    return 0.08
  
# @@@
mosfet_tech_definitions = MOSFETTechDefinitions()



# -------------------------------------------------------------

# a grid vertex
class Vertex(object):
  
  def __init__(self, ix, iy, layer):
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

  def __repr__(self):
    return f"{self.ix1}/{self.iy1}..{self.ix2}/{self.iy2} layer={self.layer} box={str(self.box)}"

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

    self.components.append(component)

    for v in component.vertexes():

      self.x_indexes.add(v.ix)
      self.y_indexes.add(v.iy)

      if not v.layer in self.components_per_layer:
        self.components_per_layer[v.layer] = [component]
      else:
        self.components_per_layer[v.layer].append(component)

      ixy = v.ixy()
      if not ixy in self.components_per_index:
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

  def layer(self):
    return self.vertexes()[0].layer;

  def is_horizontal(self):
    return self.vertexes()[0].iy == self.vertexes()[-1].iy;

  # default implementation, based on the outline boxes
  def geometry(self, graph, x_coordinates, y_coordinates):
    return self.geometry_for_boxes(x_coordinates, y_coordinates, self.boxes(graph))

  def geometry_for_boxes(self, x_coordinates, y_coordinates, boxes):
    return [ [ b.layer, b.box * kl.DBox(x_coordinates[b.ix1], y_coordinates[b.iy1], x_coordinates[b.ix2], y_coordinates[b.iy2]) ] for b in boxes ]


# a wire implementation
class Wire(Component):

  def __init__(self, width, v1, v2):
    # TODO: assert that v1.layer == v2.layer and v1.ix == v2.ix || v1.iy == v2.iy
    if v1.ix > v2.ix or v1.iy > v2.iy:
      (self.v1, self.v2) = (v2, v1)
    else:
      (self.v1, self.v2) = (v1, v2)
    self.width = width

  def vertexes(self):
    return [ self.v1, self.v2 ]

  def boxes(self, graph):
    box1 = self.min_box_per_vertex(graph, self.v1)
    box2 = self.min_box_per_vertex(graph, self.v2)
    if self.is_horizontal():
      wire_box = kl.DBox(kl.DPoint(box1.left, -0.5 * self.width), kl.DPoint(box2.right, 0.5 * self.width))
    else:
      wire_box = kl.DBox(kl.DPoint(-0.5 * self.width, box1.bottom), kl.DPoint(0.5 * self.width, box2.top))
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

    widths = self.get_widths(graph)

    (bbox, vbox, tbox) = self.via_tech_definitions.boxes(self.bottom_vertex.layer, self.top_vertex.layer, widths[0], widths[1])

    v = self.bottom_vertex

    return [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_vertex.layer), 
             Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_vertex.layer),
             Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_vertex.layer) ]

  # for the geometry we use the detailed geometry with the farm vias
  def geometry(self, graph, x_coordinates, y_coordinates):

    widths = self.get_widths(graph)

    (bbox, unused, tbox) = self.via_tech_definitions.boxes(self.bottom_vertex.layer, self.top_vertex.layer, widths[0], widths[1])
    detailed_vboxes = self.via_tech_definitions.via_geometry(self.bottom_vertex.layer, self.top_vertex.layer, widths[0], widths[1])

    v = self.bottom_vertex

    geometry = [ Box(v.ix, v.iy, v.ix, v.iy, bbox, self.bottom_vertex.layer), 
                 Box(v.ix, v.iy, v.ix, v.iy, tbox, self.top_vertex.layer) ]

    for vbox in detailed_vboxes:
      geometry.append(Box(v.ix, v.iy, v.ix, v.iy, vbox, self.via_vertex.layer))

    return self.geometry_for_boxes(x_coordinates, y_coordinates, geometry)

  def get_widths(self, graph):

    widths = [ [ None, None, None, None ], [ None, None, None, None ] ]

    # analyze wires
    for c in graph.components_for_vertex(self.via_vertex.ixy()):
      if type(c) is Wire or type(c) is MOSFET:  # @@@ directed element type
        li = -1
        if c.layer() == self.bottom_vertex.layer:
          li = 0
        elif c.layer() == self.top_vertex.layer:
          li = 1
        if li >= 0:
          widths[li][self.direction_index(c)] = c.width

    return widths

  def direction_index(self, component):
    if component.is_horizontal():
      if component.vertexes()[0].ix < self.bottom_vertex.ix:
        return 0
      else:
        return 2
    else:
      if component.vertexes()[0].iy < self.bottom_vertex.iy:
        return 1
      else:
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
    self.length = length
    # @@@ redundant
    self.poly_layer = self.gate_vertex.layer
    self.diff_layer = self.source_vertex.layer

    self.mosfet_tech_definitions = mosfet_tech_definitions

  def vertexes(self):
    return [ self.source_vertex, self.gate_vertex, self.drain_vertex ]

  def boxes(self, graph):

    sd_width = self.mosfet_tech_definitions.source_drain_active_width()
    sd_box = kl.DBox(kl.DPoint(-0.5 * sd_width, -0.5 * self.width), kl.DPoint(0.5 * sd_width, 0.5 * self.width))

    gate_extension = self.mosfet_tech_definitions.gate_extension()
    gate_box = kl.DBox(kl.DPoint(), kl.DPoint()).enlarged(0.5 * self.length, 0.5 * self.width + gate_extension)

    return [ Box(self.source_vertex.ix, self.source_vertex.iy, self.drain_vertex.ix, self.drain_vertex.iy, sd_box, self.diff_layer),
             Box(self.gate_vertex.ix, self.gate_vertex.iy, self.gate_vertex.ix, self.gate_vertex.iy, gate_box, self.poly_layer) ]


class ConstraintSolver(object):

  def __init__(self, graph):

    self.graph = graph
    self.ix = sorted([ v for v in graph.x_indexes ])
    self.iy = sorted([ v for v in graph.y_indexes ])
    self.x_coordinates = None
    self.y_coordinates = None

    self.tech_rules = tech_rules

  def solve(self, initial_grid_x = 10.0, initial_grid_y = 10.0):

    self.x_coordinates = {}
    self.y_coordinates = {}
    for i in self.ix:
      self.x_coordinates[i] = initial_grid_x * i
    for i in self.iy:
      self.y_coordinates[i] = initial_grid_y * i

    threshold = 0.05 # @@@?
    max_iter = 10

    delta = threshold * 2
    niter = 0
    
    while delta > threshold and niter < max_iter:

      xc = self.x_coordinates.copy()
      yc = self.y_coordinates.copy()

      self.compute_coordinates_h()
      self.compute_coordinates_v()

      niter += 1
      delta = self.diff(xc, self.x_coordinates) + self.diff(yc, self.y_coordinates)

      print(f"@@@ x=" + ",".join([ "%.12g" % v for v in self.x_coordinates.values() ]))
      print(f"@@@ y=" + ",".join([ "%.12g" % v for v in self.y_coordinates.values() ]))
      print(f"@@@ iter={niter} -> delta={delta}")

    return niter < max_iter

  # generates the layout
  # layout and cell are layout and top cell objects respectively
  # layers are the layer indexes in the layout by functional layer index
  def produce(self, layout, cell, layers):

    for c in self.graph.components:

      for g in c.geometry(self.graph, self.x_coordinates, self.y_coordinates):
        cell.shapes(layers[g[0]]).insert(g[1])


  def diff(self, a, b):
    d = 0.0
    for i in a.keys():
      d += math.sqrt((a[i] - b[i]) ** 2)
    return d


  def compute_coordinates_h(self):

    prev_boxes = []

    for i in self.ix:

      current_boxes = []
      for j in self.iy:
        for c in self.graph.components_for_vertex(( i, j )):
          for b in c.boxes(self.graph):
            if b.ix1 == i:
              current_boxes.append(b)

      if len(current_boxes) > 0:

        min_coord = 0.0

        # NOTE: this is rather brute force - the complexity boils down to O(2)
        for cb in current_boxes:
          if self.box_is_shielded_h(cb, prev_boxes):
            continue
          for pb in prev_boxes:
            space = self.tech_rules.space(min(pb.layer, cb.layer), max(pb.layer, cb.layer))
            if space is not None:
              coord = self.compute_coord_h(space, pb, cb)
              if coord is not None and coord > min_coord:
                min_coord = coord

      self.x_coordinates[i] = min_coord

      prev_boxes += current_boxes

  def box_is_shielded_h(self, b, other_boxes):

    for ob in other_boxes:
      if ob.iy1 > b.iy1 or ob.iy2 < b.iy2 or b.layer != ob.layer or ob.ix2 < b.ix1:
        continue
      if ob.box.bottom > b.box.bottom + 1e-10 or ob.box.top < b.box.top - 1e-10:
        continue
      return True

    return False
        
  def compute_coord_h(self, space, b1, b2):

    if b1.ix2 >= b2.ix1:
      return None

    dbox1 = b1.box * kl.DBox(self.x_coordinates[b1.ix1], self.y_coordinates[b1.iy1], self.x_coordinates[b1.ix2], self.y_coordinates[b1.iy2])
    dbox2 = b2.box * kl.DBox(0.0, self.y_coordinates[b2.iy1], 0.0, self.y_coordinates[b2.iy2])

    dbox1 = dbox1.enlarged(space, space)

    # no perpendicular overlap
    if dbox1.bottom > dbox2.top - 1e-10 or dbox1.top < dbox2.bottom + 1e-10:
      return None 
    
    return dbox1.right - dbox2.left

  def compute_coordinates_v(self):

    prev_boxes = []

    for i in self.iy:

      current_boxes = []
      for j in self.ix:
        for c in self.graph.components_for_vertex(( j, i )):
          for b in c.boxes(self.graph):
            if b.iy1 == i:
              current_boxes.append(b)

      if len(current_boxes) > 0:

        min_coord = 0.0

        # NOTE: this is rather brute force
        for cb in current_boxes:
          for pb in prev_boxes:
            space = self.tech_rules.space(min(pb.layer, cb.layer), max(pb.layer, cb.layer))
            if space is not None:
              coord = self.compute_coord_v(space, pb, cb)
              if coord is not None and coord > min_coord and not self.box_is_shielded_v(cb, pb, prev_boxes):
                min_coord = coord

      self.y_coordinates[i] = min_coord

      prev_boxes += current_boxes

  def box_is_shielded_v(self, b, wrt, other_boxes):

    ix1 = max(b.ix1, wrt.ix1)
    ix2 = min(b.ix2, wrt.ix2)
    left = max(b.box.left, wrt.box.left)
    right = max(b.box.right, wrt.box.right)

    for ob in other_boxes:
      if ob.ix1 > ix1 or ob.ix2 < ix2 or b.layer != ob.layer or ob.iy2 < b.iy1:
        continue
      if ob.box.left > left + 1e-10 or ob.box.right < right - 1e-10:
        continue
      return True

    return False
        
        
  def compute_coord_v(self, space, b1, b2):

    if b1.iy2 >= b2.iy1:
      return None

    dbox1 = b1.box * kl.DBox(self.x_coordinates[b1.ix1], self.y_coordinates[b1.iy1], self.x_coordinates[b1.ix2], self.y_coordinates[b1.iy2])
    dbox2 = b2.box * kl.DBox(self.x_coordinates[b2.ix1], 0.0, self.x_coordinates[b2.ix2], 0.0)

    dbox1 = dbox1.enlarged(space, space)

    # no perpendicular overlap
    if dbox1.left > dbox2.right - 1e-10 or dbox1.right < dbox2.left + 1e-10:
      return None 
    
    return dbox1.top - dbox2.bottom


# ------------------------------------------------------------------

# a test rig

output = "generated.gds"

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
wp = 0.9
wn = 0.6

graph = Graph()

# output stage (n=2) pmos
graph.add(MOSFET(Vertex(1, 3, poly), Vertex(0, 3, diff), Vertex(2, 3, diff), wp, l))
graph.add(MOSFET(Vertex(3, 3, poly), Vertex(4, 3, diff), Vertex(2, 3, diff), wp, l))
# output stage (n=2) nmos
graph.add(MOSFET(Vertex(1, 1, poly), Vertex(0, 1, diff), Vertex(2, 1, diff), wn, l))
graph.add(MOSFET(Vertex(3, 1, poly), Vertex(4, 1, diff), Vertex(2, 1, diff), wn, l))

# input stage pmos
graph.add(MOSFET(Vertex(6, 3, poly), Vertex(4, 3, diff), Vertex(7, 3, diff), wp, l))
# input stage nmos
graph.add(MOSFET(Vertex(6, 1, poly), Vertex(4, 1, diff), Vertex(7, 1, diff), wn, l))

# VDD
graph.add(Via(Vertex(0, 3, diff), Vertex(0, 3, metal1), Vertex(0, 3, contact)))
graph.add(Via(Vertex(4, 3, diff), Vertex(4, 3, metal1), Vertex(4, 3, contact)))
graph.add(Wire(metal1w, Vertex(0, 3, metal1), Vertex(0, 4, metal1)))
graph.add(Wire(metal1w, Vertex(4, 3, metal1), Vertex(4, 4, metal1)))
graph.add(Wire(0.5, Vertex(0, 4, metal1), Vertex(4, 4, metal1)))

# VSS
graph.add(Via(Vertex(0, 1, diff), Vertex(0, 1, metal1), Vertex(0, 1, contact)))
graph.add(Via(Vertex(4, 1, diff), Vertex(4, 1, metal1), Vertex(4, 1, contact)))
graph.add(Wire(metal1w, Vertex(0, 0, metal1), Vertex(0, 1, metal1)))
graph.add(Wire(metal1w, Vertex(4, 0, metal1), Vertex(4, 1, metal1)))
graph.add(Wire(0.5, Vertex(0, 0, metal1), Vertex(4, 0, metal1)))

# output
graph.add(Via(Vertex(2, 3, diff), Vertex(2, 3, metal1), Vertex(2, 3, contact)))
graph.add(Via(Vertex(2, 1, diff), Vertex(2, 1, metal1), Vertex(2, 1, contact)))
graph.add(Wire(metal1w, Vertex(2, 1, metal1), Vertex(2, 2, metal1)))
graph.add(Wire(metal1w, Vertex(2, 2, metal1), Vertex(2, 3, metal1)))

# output stage gate wiring
graph.add(Wire(polyw, Vertex(1, 1, poly), Vertex(1, 2, poly)))
graph.add(Wire(polyw, Vertex(1, 2, poly), Vertex(1, 3, poly)))
graph.add(Wire(polyw, Vertex(3, 1, poly), Vertex(3, 2, poly)))
graph.add(Wire(polyw, Vertex(3, 2, poly), Vertex(3, 3, poly)))
graph.add(Wire(polyw, Vertex(1, 2, poly), Vertex(3, 2, poly)))
graph.add(Wire(polyw, Vertex(3, 2, poly), Vertex(5, 2, poly)))

# output stage gate to m1
graph.add(Via(Vertex(5, 2, poly), Vertex(5, 2, metal1), Vertex(5, 2, contact)))

# input stage to output stage input m1
graph.add(Wire(metal1w, Vertex(5, 2, metal1), Vertex(7, 2, metal1)))
graph.add(Wire(metal1w, Vertex(7, 1, metal1), Vertex(7, 2, metal1)))
graph.add(Wire(metal1w, Vertex(7, 2, metal1), Vertex(7, 3, metal1)))

# input stage gate wiring
graph.add(Wire(polyw, Vertex(6, 1, poly), Vertex(6, 2, poly)))
graph.add(Wire(polyw, Vertex(6, 2, poly), Vertex(6, 3, poly)))

# input pin
graph.add(Wire(polyw, Vertex(6, 2, poly), Vertex(8, 2, poly)))


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

layout.write(output)
print(f"{output} written.")

