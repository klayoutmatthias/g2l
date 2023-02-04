
from grid_solver import Tech
import klayout.db as kl
import math

# -------------------------------------------------------------

# Layer indexes 

diff    = 0
contact = 1
poly    = 2
metal1  = 3
via1    = 4
metal2  = 5

num_layers = 6

def create_layers(layout):

  layers = {}

  layers[diff]    = layout.layer(2, 0)
  layers[poly]    = layout.layer(7, 0)
  layers[contact] = layout.layer(14, 0)
  layers[metal1]  = layout.layer(15, 0)
  layers[via1]    = layout.layer(16, 0)
  layers[metal2]  = layout.layer(17, 0)

  return layers
  

# -------------------------------------------------------------

class TechRules(object):

  def __init__(self):
    pass

  # Returns the minimum space/separation for the given layer pair.
  # "layer1" can be identical to "layer2"
  def space(self, layer1, layer2):

    # @@@ demo, functional layers are:
    if layer1 == diff and layer2 == diff:
      return 0.4   # diff space
    elif layer1 == poly and layer2 == poly:
      return 0.17   # poly space
    elif layer1 == contact and layer2 == contact:
      return 0.14  # contact space
    elif layer1 == min(contact, poly) and layer2 == max(contact, poly):
      return 0.05  # poly/contact space
    elif layer1 == min(diff, poly) and layer2 == max(diff, poly):
      return 0.10  # poly/diff space
    elif layer1 == metal1 and layer2 == metal1:
      return 0.17  # metal1 space
    elif layer1 == via1 and layer2 == via1:
      return 0.2   # via1 space
    elif layer1 == metal2 and layer2 == metal2:
      return 0.2   # metal2 space
    else:
      return None

  # gets the number of functional layer indexes
  def layers(self):
    return num_layers
    
  def default_wire_width(self, layer):

    if layer == poly:
      return 0.13
    elif layer == metal1:
      return 0.2
    elif layer == metal2:
      return 0.2
    else:
      return None

# @@@
Tech.rules = TechRules()


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
    via_space = 0.17

    (bbox, tbox) = self.top_bottom_boxes(bottom_layer, top_layer, bottom_widths, top_widths)

    return self.create_farm_via(via_size, via_space, bbox & tbox)

  def top_bottom_boxes(self, bottom_layer, top_layer, bottom_widths, top_widths):

    # Simple demo implementation

    top_min_dim = 0.2
    bottom_min_dim = 0.2

    if top_layer == metal1:  # contact
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
Tech.vias = ViaTechDefinitions()


class MOSFETTechDefinitions(object):

  def __init__(self):
    pass

  # @@@ dummy definitions

  # the extension the gate poly needs to have over active area
  def poly_gate_extensions(self):
    return 0.05

  def source_drain_active_width(self):
    return 0.25
  
  def gate_extension(self):
    return 0.08
  
# @@@
Tech.mosfets = MOSFETTechDefinitions()

