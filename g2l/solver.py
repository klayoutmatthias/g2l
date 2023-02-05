
from .tech import Tech
import klayout.db as kl
import math
import logging

class Solver(object):

  def __init__(self, graph):

    self.graph = graph
    self.ix = sorted([ v for v in graph.x_indexes ])
    self.iy = sorted([ v for v in graph.y_indexes ])
    self.x_coordinates = None
    self.y_coordinates = None

    self.tech_rules = Tech.rules

  def solve(self, initial_grid_x = 10.0, initial_grid_y = 10.0, threshold = 0.05, max_iter = 10, horizonal_first = True):

    self.x_coordinates = {}
    self.y_coordinates = {}
    for i in self.ix:
      self.x_coordinates[i] = initial_grid_x * i
    for i in self.iy:
      self.y_coordinates[i] = initial_grid_y * i

    delta = threshold * 2
    niter = 0

    logger = logging.getLogger("g2l-solver")
    
    logger.info("solving constraints")
    logger.info(f"x=" + ",".join([ "%.12g" % v for v in self.x_coordinates.values() ]))
    logger.info(f"y=" + ",".join([ "%.12g" % v for v in self.y_coordinates.values() ]))

    while delta > threshold and niter < max_iter:

      xc = self.x_coordinates.copy()
      yc = self.y_coordinates.copy()

      self.compute_coordinates(horizonal_first)
      self.compute_coordinates(not horizonal_first)

      niter += 1
      delta = self.diff(xc, self.x_coordinates) + self.diff(yc, self.y_coordinates)

      logger.info(f"iteration {niter}:")
      logger.info(f"x=" + ",".join([ "%.12g" % v for v in self.x_coordinates.values() ]))
      logger.info(f"y=" + ",".join([ "%.12g" % v for v in self.y_coordinates.values() ]))
      logger.info(f"difference to previous iteration: {'%.12g' % delta} (threshold is {'%.12g' % threshold})")

    logger.info("solver stopped.")

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


  def compute_coordinates(self, h):

    prev_boxes = []
    min_coord = 0.0

    for i in (self.ix if h else self.iy):

      current_boxes = []
      for j in (self.iy if h else self.ix):
        for c in self.graph.components_for_node((i, j) if h else (j, i)):
          for b in c.boxes(self.graph):
            if b.ixory1(h) == i:
              current_boxes.append(b)

      if len(current_boxes) > 0:

        min_coord = 0.0

        # NOTE: this is rather brute force - the complexity boils down to O(2)
        for cb in current_boxes:
          for pb in prev_boxes:
            space = self.tech_rules.space(min(pb.layer, cb.layer), max(pb.layer, cb.layer))
            if space is not None:
              coord = self.compute_coord(space, pb, cb, h)
              if coord is not None and coord > min_coord and not self.box_is_shielded(cb, pb, prev_boxes, h):
                min_coord = coord

      if h:
        self.x_coordinates[i] = min_coord
      else:
        self.y_coordinates[i] = min_coord

      prev_boxes += current_boxes

  def box_is_shielded(self, b, wrt, other_boxes, h):

    iyorx1 = max(b.iyorx1(h), wrt.iyorx1(h))
    iyorx2 = min(b.iyorx2(h), wrt.iyorx2(h))
    yorxmin = max(b.yorxmin(h), wrt.yorxmin(h))
    yorxmax = min(b.yorxmax(h), wrt.yorxmax(h))

    for ob in other_boxes:
      if ob.iyorx1(h) > iyorx1 or ob.iyorx2(h) < iyorx2 or (b.layer != ob.layer and wrt.layer != ob.layer) or ob.ixory2(h) < b.ixory1(h):
        continue
      if ob.yorxmin(h) > yorxmin + 1e-10 or ob.yorxmax(h) < yorxmax - 1e-10:
        continue
      return True

    return False

  def compute_coord(self, space, b1, b2, h):
    if h:
      return self.compute_coord_h(space, b1, b2)
    else:
      return self.compute_coord_v(space, b1, b2)

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

