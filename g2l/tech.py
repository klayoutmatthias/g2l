
class Tech(object):

  """
  The technology singleton

  This class is a hook for plugging in technology
  implementation classes.
  
  Implementations of a specific technologies
  are supposed to set the rules, vias and mosfets
  class attributes to a specific implementation
  """

  rules = None
  vias = None
  mosfets = None

