
from g2l import Tech
import klayout.db as kl
import math

class TechRules(object):

  """
  General technology rules
  """

  def __init__(self):
    pass

  def space(self, layer1: int, layer2: int) -> float:
    """
    Returns the minimum space/separation for the given layer pair.

    "layer1" can be identical to "layer2"

    Returns None if no space constraint exists.
    """
    return None

  def create_layers(self, layout: kl.Layout) -> { int: int }:
    """
    Creates the necessary layers inside the Layout object

    Returns a hash of layer numbers (keys) and 
    KLayout Layout layer indexes (values).
    """
    return {}
    
  def default_wire_width(self, layer: int) -> float:
    """
    Returns the default wire width for a given layer

    Returns None if no default is given.
    """
    return None


# install the technology singleton
Tech.rules = TechRules()


class ViaTechDefinitions(object):

  """
  Provides via definitions
  """

  def __init__(self):
    pass

  def boxes(self, bottom_layer: int, top_layer: int, bottom_widths: [float], top_widths: [float]) -> (kl.DBox, kl.DBox, kl.DBox):
    """
    Gets the coarse via geometry

    "bottom_layer" and "top_layer" define the type of via.

    "bottom_widths" are the widths of the attached wires from [ left, bottom, right, top ]
    ("None" indicates that there is no connection from that side)
    "top_widths" is the same for the top layer.
    The returned values need to be minimum boxes for bottom and top layers as a tuple.
    The boxes are supposed to be 0,0 centered.

    This method delivers "coarse" geometry which is sufficient to position
    the via. Specifically array vias can be represented by a hull box
    rather than individual boxes.
    """

    # this is just a sample
    return ( kl.DBox(-1, -1, 1, 1), kl.DBox(-0.5, -0.5, 0.5, 0.5), kl.DBox(-1, -1, 1, 1) )

  def via_geometry(self, bottom_layer: int, top_layer: int, bottom_widths: [float], top_widths: [float]) -> (kl.DBox, kl.DBox, kl.DBox):
    """
    Gets the detailed via geometry

    This method acts similar to "boxes", but delivers the final geometry
    rather than the coarse geometry.
    """

    # this is just a sample
    return ( kl.DBox(-1, -1, 1, 1), kl.DBox(-0.5, -0.5, 0.5, 0.5), kl.DBox(-1, -1, 1, 1) )


# install the technology singleton
Tech.vias = ViaTechDefinitions()


class MOSFETTechDefinitions(object):

  """
  Provides definitions for MOSFET devices
  """

  def __init__(self):
    pass

  def source_drain_active_width(self):
    """
    Returns the width of the source/drain active region
    """
    return 0.5
  
  def gate_extension(self):
    """
    Returns the poly gate extension over active region
    """
    return 0.1

  def poly_layer(self):
    """
    Returns the layer number of the poly layer
    """
    return 1

  def active_layer(self):
    """
    Returns the layer number of the active area layer
    """
    return 0
  

# install the technology singleton
Tech.mosfets = MOSFETTechDefinitions()

