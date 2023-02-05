
from g2l import Tech
import klayout.db as kl
import math

# -------------------------------------------------------------

# Name        Stream  Layer number
# nwell       64/20   0
# diff        65/20   1
# tap         65/44   2
# poly        66/20   3
# licon       66/44   4
# li          67/20   5
# mcon        67/44   6
# met1        68/20   7
# via         68/44   8
# met2        69/20   9
# via2        69/44   10
# met3        70/20   11
# via3        70/44   12
# met4        71/20   13
# via4        71/44   14
# met5        72/20   15

# Layer indexes 
nwell       = 0
diff        = 1
tap         = 2
poly        = 3
licon       = 4
li          = 5
mcon        = 6
met1        = 7
via         = 8
met2        = 9
via2        = 10
met3        = 11
via3        = 12
met4        = 13
via4        = 14
met5        = 15

# -------------------------------------------------------------

class TechRules(object):

  def __init__(self):
    pass

  def layer(self, generic_name: str) -> int:
    """
    Translates a generic layer name into a technology specific layer index

    The motivation for this function is a provide technology
    agnostic layers.
    """
    if generic_name == "diff":
      return diff
    elif generic_name == "nwell":
      return nwell
    elif generic_name == "contact":
      return licon
    elif generic_name == "poly":
      return poly
    elif generic_name == "metal1":
      return li
    elif generic_name == "via1":
      return mcon
    elif generic_name == "metal2":
      return met1
    elif generic_name == "via2":
      return via
    elif generic_name == "metal3":
      return met2
    elif generic_name == "via3":
      return via2
    elif generic_name == "metal4":
      return met3
    elif generic_name == "via4":
      return via3
    elif generic_name == "metal5":
      return met4
    else:
      raise Exception(f"Invalid generic layer name: {generic_name}")

  def space(self, layer1, layer2):
    """
    Returns the minimum space/separation for the given layer pair.
    """
    if layer1 == diff and layer2 == diff:
      return 0.27  # diff space
    elif layer1 == poly and layer2 == poly:
      return 0.21  # poly space
    elif layer1 == licon and layer2 == licon:
      return 0.17  # licon space
    elif layer1 == min(licon, poly) and layer2 == max(licon, poly):
      return 0.05  # poly/licon space
    elif layer1 == min(diff, poly) and layer2 == max(diff, poly):
      return 0.075 # poly/diff space
    elif layer1 == li and layer2 == li:
      return 0.17  # li space
    elif layer1 == mcon and layer2 == mcon:
      return 0.17  # mcon space
    elif layer1 == met1 and layer2 == met1:
      return 0.14  # met1 space
    elif layer1 == via and layer2 == via:
      return 0.17  # via space
    elif layer1 == met2 and layer2 == met2:
      return 0.2   # met2 space
    elif layer1 == via2 and layer2 == via2:
      return 0.2   # via2 space
    elif layer1 == met3 and layer2 == met3:
      return 0.3   # met3 space
    # TODO: more
    else:
      return None

  def create_layers(self, layout):
    """
    Creates output layout layers (stream layer mapping)
    """
    layers = {}
    layers[nwell]   = layout.layer(64, 20)
    layers[diff]    = layout.layer(65, 20)
    layers[tap]     = layout.layer(65, 44)
    layers[poly]    = layout.layer(66, 20)
    layers[licon]   = layout.layer(66, 44)
    layers[li]      = layout.layer(67, 20)
    layers[mcon]    = layout.layer(67, 44)
    layers[met1]    = layout.layer(68, 20)
    layers[via]     = layout.layer(68, 44)
    layers[met2]    = layout.layer(69, 20)
    layers[via2]    = layout.layer(69, 44)
    layers[met3]    = layout.layer(70, 20)
    layers[via3]    = layout.layer(70, 44)
    layers[met4]    = layout.layer(71, 20)
    layers[via4]    = layout.layer(71, 44)
    layers[met5]    = layout.layer(72, 20)
    return layers
    
  def default_wire_width(self, layer):
    """
    Returns the default wire widths
    """
    if layer == poly:
      return 0.15
    elif layer == li:
      return 0.17
    elif layer == met1:
      return 0.14
    elif layer == met2:
      return 0.14
    else:
      return None

# Installs the technology singleton
Tech.rules = TechRules()


# Supplies an algorithm for defining the via enclosures and other via definitions

class ViaTechDefinitions(object):

  def __init__(self):
    pass

  def boxes(self, bottom_layer, top_layer, bottom_widths, top_widths):
    """
    Gets the landing pad boxes

    "bottom_widths" are the widths of the attached wires from [ left, bottom, right, top ]
    ("None" indicates that there is no connection from that side)
    "top_widths" is the same for the top layer.
    The returned values need to be minimum boxes for bottom and top layers as a tuple.
    The boxes are supposed to be 0,0 centered.
    """

    (bbox, tbox) = self._top_bottom_boxes(bottom_layer, top_layer, bottom_widths, top_widths)

    # For efficiency, we don't produce each single via, but just a common box on the cut layer
    # we will later replace the common box by individual boxes for the farm vias.
    vbox = kl.DBox()
    for b in self.via_geometry(bottom_layer, top_layer, bottom_widths, top_widths):
      vbox += b
    
    return (bbox, vbox, tbox)

  def via_geometry(self, bottom_layer, top_layer, bottom_widths, top_widths):
    """
    Gets the via geometry

    Parameters as in "boxes". The returned geometry objects are supposed to be 
    created for a via at 0,0.
    """

    if bottom_layer == met2:
      # via2 
      via_size = 0.2
      via_space = 0.2
    else:
      # licon, mcon, via
      via_size = 0.17
      via_space = 0.17

    # distance to border for farm via generation
    enclosure = 0.05

    (bbox, tbox) = self._top_bottom_boxes(bottom_layer, top_layer, bottom_widths, top_widths)

    return self._create_farm_via(via_size, via_space, (bbox & tbox).enlarged(-enclosure, -enclosure))

  def _top_bottom_boxes(self, bottom_layer, top_layer, bottom_widths, top_widths):

    # compute minimum width according to attached wires
    bw = max([ bottom_widths[i] or 0.0 for i in [1, 3] ])
    tw = max([ top_widths[i] or 0.0 for i in [1, 3] ])
    if bw == 0.0:
      bw = tw
    if tw == 0.0:
      tw = bw

    # compute minimum height according to attached wires
    bh = max([ bottom_widths[i] or 0.0 for i in [0, 2] ])
    th = max([ top_widths[i] or 0.0 for i in [0, 2] ])
    if bh == 0.0:
      bh = th
    if th == 0.0:
      th = bh

    if top_layer == li:

      # licon 
      # poly: simple landing pad
      if bottom_layer == poly:
        bw = max(0.27, bw)
        bh = max(0.27, bh)

      # li: 
      if top_widths[0] is None and top_widths[2] is None:
        # connection from vertical only
        th = max(0.27, th)
      else:
        tw = max(0.27, tw)
        
    elif bottom_layer == li:

      # mcon 
      # met2: simple landing pad
      tw = max(0.3, tw)
      th = max(0.3, th)

      # li: 
      if bottom_widths[0] is None and bottom_widths[2] is None:
        # connection from vertical only
        bh = max(0.27, bh)
      else:
        bw = max(0.27, bw)
        
    # generate boxes

    bbox = kl.DBox(-0.5 * bw, -0.5 * bh, 0.5 * bw, 0.5 * bh)
    tbox = kl.DBox(-0.5 * tw, -0.5 * th, 0.5 * tw, 0.5 * th)

    return (bbox, tbox)

  # Creates a farm via (array) covering the given "via_box" with vias
  # with given size and space
  def _create_farm_via(self, via_size, via_space, via_box):

    nx = max(1, math.floor(1e-10 + (via_box.width() + via_space) / (via_size + via_space)))
    ny = max(1, math.floor(1e-10 + (via_box.height() + via_space) / (via_size + via_space)))
  
    geometry = []
    for i in range(0, nx):
      for j in range(0, ny):
        x = (i - (nx - 1) * 0.5) * (via_size + via_space)
        y = (j - (ny - 1) * 0.5) * (via_size + via_space)
        geometry.append(kl.DBox(-0.5 * via_size, -0.5 * via_size, 0.5 * via_size, 0.5 * via_size).moved(x, y))
        
    return geometry

# Installs the technology singleton
Tech.vias = ViaTechDefinitions()


class MOSFETTechDefinitions(object):

  def __init__(self):
    pass

  def default_mos_length(self):
    return 0.15

  def min_nmos_width(self):
    return 0.4

  def min_pmos_width(self):
    return 0.25

  def source_drain_active_width(self):
    return 0.27
  
  def gate_extension(self):
    return 0.13

  def poly_layer(self):
    return poly

  def active_layer(self):
    return diff
  
# Installs the technology singleton
Tech.mosfets = MOSFETTechDefinitions()

