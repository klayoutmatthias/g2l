
from .tech import Tech
from .graph import Graph
from .box import Box
import klayout.db as kl
import math
import logging

class Solver(object):

  """
  The constraint solver

  The solver will use the constraints it finds int he 
  technology singleton (Tech.rules) and us them to 
  create physical layout from the abstract layout graph.

  This implementation is not very elaborate and rather
  brute force. It is intended as a demonstrator currently.

  To use the solver instantiate it with the graph and 
  use the "solve" method. After this, use "produce"
  to produce the physical layout as a KLayout Cell.
  """

  def __init__(self, graph: Graph):

    """
    Creates a solver object

    :param graph: the abstract layout graph
    """

    self.graph = graph
    self.ix = sorted([ v for v in graph.x_indexes ])
    self.iy = sorted([ v for v in graph.y_indexes ])
    self.x_coordinates = None
    self.y_coordinates = None

    self.tech_rules = Tech.rules

  def solve(self, initial_grid_x = 10.0, initial_grid_y = 10.0, threshold = 0.001, max_iter = 10, horizonal_first = True) -> bool:
    """
    Solves the constraint puzzle

    This method will try to solve the constraints given by 
    the technology singleton (Tech.rules) and the components/boxes
    inside the graph and determine actual coordinates for the 
    abstract node coordinates such that the design rules are 
    fulfilled.

    It starts with an initial distribution on an initial grid.
    If "horizontal_first" is present, it will first determine 
    a compact as possible horizontal arrangement, followed by
    the same step in the vertical direction.

    It will iterate these steps until either the maximum number
    of iterations is reached or the geometry converges.

    The idea of the initial grid is to be large enough, so that
    the iterations perform a compaction. During one-dimensional
    compaction, parts may shift in the way they block compaction
    in the perpendicular direction. So you can try starting with
    horizonal or vertical compaction - whatever gives a better
    result.

    :param initial_grid_x: the initial x spacing of the grid coordinates
    :param initial_grid_y: the initial y spacing of the grid coordinates
    :param threshold: the maximum coordinate change below which iteration will stop
    :param max_iter: the maxmum number of iterations
    :param horizontal_first: true, if the horizontal compaction is to be done first

    :returns True, if the algorithm converged
    """

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

      self._compute_coordinates(horizonal_first)
      self._compute_coordinates(not horizonal_first)

      niter += 1
      delta = max(self._diff(xc, self.x_coordinates), self._diff(yc, self.y_coordinates))

      logger.info(f"iteration {niter}:")
      logger.info(f"x=" + ",".join([ "%.12g" % v for v in self.x_coordinates.values() ]))
      logger.info(f"y=" + ",".join([ "%.12g" % v for v in self.y_coordinates.values() ]))
      logger.info(f"difference to previous iteration: {'%.12g' % delta} (threshold is {'%.12g' % threshold})")

    logger.info("solver stopped.")

    return niter < max_iter

  def produce(self, layout: kl.Layout, cell: kl.Cell):
    """
    Generates the layout

    This method will fill the given cell with the shapes
    from the components.

    It uses the "create_layers" from the technology singleton
    (Tech.rules) to generate the output layers.
    """

    layers = self.tech_rules.create_layers(layout)

    for c in self.graph.components:

      for g in c.geometry(self.graph, self.x_coordinates, self.y_coordinates):
        (layer, box) = g
        cell.shapes(layers[layer]).insert(box)


  def _diff(self, a: [float], b: [float]) -> float:
    """
    Computes the maximum difference between two coordinate sets
    """
    d = 0.0
    for i in a.keys():
      d = max(d, abs(a[i] - b[i]))
    return d

  def _compute_coordinates(self, h: bool):

    """
    One iteration step

    Updates the coordinates either in horizontal (h = True) or vertical (h = False) direction
    """

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
              coord = self._compute_coord(space, pb, cb, h)
              if coord is not None and coord > min_coord and not self._box_is_shielded(cb, pb, prev_boxes, h):
                min_coord = coord

      if h:
        self.x_coordinates[i] = min_coord
      else:
        self.y_coordinates[i] = min_coord

      prev_boxes += current_boxes

  def _box_is_shielded(self, b: Box, wrt: Box, other_boxes: [Box], h: bool) -> bool:

    """
    Determines whether a box is shielded by other boxes

    Given an interacting pair of boxes (b, wrt), this
    method determines whether other boxes from the "other_boxes"
    collection shield this interaction (overlap the gap).
    """

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

  def _compute_coord(self, space: float, b1: Box, b2: Box, h: bool) -> float:

    """
    Computes a coordinate for a box relative to another one

    Given an already fixed box b1 and a new box b2 plus a 
    mandatory space between both, this method will compute the
    location of the new box b2 (ix1 position if h is True or 
    iy1 position if h is False).
    """

    if h:
      return self._compute_coord_h(space, b1, b2)
    else:
      return self._compute_coord_v(space, b1, b2)

  def _compute_coord_h(self, space: float, b1: Box, b2: Box) -> float:

    if b1.ix2 >= b2.ix1:
      return None

    dbox1 = b1.box * kl.DBox(self.x_coordinates[b1.ix1], self.y_coordinates[b1.iy1], self.x_coordinates[b1.ix2], self.y_coordinates[b1.iy2])
    dbox2 = b2.box * kl.DBox(0.0, self.y_coordinates[b2.iy1], 0.0, self.y_coordinates[b2.iy2])

    dbox1 = dbox1.enlarged(space, space)

    # no perpendicular overlap
    if dbox1.bottom > dbox2.top - 1e-10 or dbox1.top < dbox2.bottom + 1e-10:
      return None 
    
    return dbox1.right - dbox2.left

  def _compute_coord_v(self, space: float, b1: Box, b2: Box) -> float:

    if b1.iy2 >= b2.iy1:
      return None

    dbox1 = b1.box * kl.DBox(self.x_coordinates[b1.ix1], self.y_coordinates[b1.iy1], self.x_coordinates[b1.ix2], self.y_coordinates[b1.iy2])
    dbox2 = b2.box * kl.DBox(self.x_coordinates[b2.ix1], 0.0, self.x_coordinates[b2.ix2], 0.0)

    dbox1 = dbox1.enlarged(space, space)

    # no perpendicular overlap
    if dbox1.left > dbox2.right - 1e-10 or dbox1.right < dbox2.left + 1e-10:
      return None 
    
    return dbox1.top - dbox2.bottom

