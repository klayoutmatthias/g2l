
from g2l import *
import klayout.db as kl
import logging

# technology definitions
import sky130

logging.basicConfig(level = logging.INFO)

# ------------------------------------------------------------------

# a test rig

output = "generated.gds"

diff    = Tech.rules.layer("diff")
contact = Tech.rules.layer("contact")
poly    = Tech.rules.layer("poly")
metal1  = Tech.rules.layer("metal1")
via1    = Tech.rules.layer("via1")
metal2  = Tech.rules.layer("metal2")

metal1w = Tech.rules.default_wire_width(metal1)
metal2w = Tech.rules.default_wire_width(metal2)
polyw   = Tech.rules.default_wire_width(poly)
polywh  = 0.27

l       = Tech.mosfets.default_mos_length()
wpo     = Tech.mosfets.min_pmos_width() * 3
wno     = Tech.mosfets.min_nmos_width() * 3
wp      = Tech.mosfets.min_pmos_width() * 3
wn      = Tech.mosfets.min_nmos_width() * 3

graph   = Graph()

# output stage (n=2) pmos
graph.add(MOSFET(n(1, 3), n(0, 3), n(2, 3), wpo, l))
graph.add(MOSFET(n(3, 3), n(4, 3), n(2, 3), wpo, l))
# output stage (n=2) nmos
graph.add(MOSFET(n(1, 1), n(0, 1), n(2, 1), wno, l))
graph.add(MOSFET(n(3, 1), n(4, 1), n(2, 1), wno, l))

# input stage pmos
graph.add(MOSFET(n(6, 3), n(4, 3), n(7, 3), wp, l))
# input stage nmos
graph.add(MOSFET(n(6, 1), n(4, 1), n(7, 1), wn, l))

# VDD
graph.add(Via(n(0, 3), diff, contact, metal1))
graph.add(Via(n(4, 3), diff, contact, metal1))
graph.add(Wire(metal1w, metal1, n(0, 3), n(0, 4)))
graph.add(Wire(metal1w, metal1, n(4, 3), n(4, 4)))
graph.add(Wire(0.5, metal1, n(0, 4), n(4, 4)))

# VSS
graph.add(Via(n(0, 1), diff, contact, metal1))
graph.add(Via(n(4, 1), diff, contact, metal1))
graph.add(Wire(metal1w, metal1, n(0, 0), n(0, 1)))
graph.add(Wire(metal1w, metal1, n(4, 0), n(4, 1)))
graph.add(Wire(0.5, metal1, n(0, 0), n(4, 0)))

# output
graph.add(Via(n(2, 3), diff, contact, metal1))
graph.add(Via(n(2, 1), diff, contact, metal1))
graph.add(Wire(metal1w, metal1, n(2, 1), n(2, 2)))
graph.add(Wire(metal1w, metal1, n(2, 2), n(2, 3)))

# output stage gate wiring
graph.add(Wire(polyw, poly, n(1, 1), n(1, 2)))
graph.add(Wire(polyw, poly, n(1, 2), n(1, 3)))
graph.add(Wire(polyw, poly, n(3, 1), n(3, 2)))
graph.add(Wire(polyw, poly, n(3, 2), n(3, 3)))
graph.add(Wire(polywh, poly, n(1, 2), n(3, 2)))
graph.add(Wire(polywh, poly, n(3, 2), n(5, 2)))

# output stage gate to m1
graph.add(Via(n(5, 2), poly, contact, metal1))

# input stage to output stage input m1
graph.add(Via(n(7, 3), diff, contact, metal1))
graph.add(Via(n(7, 1), diff, contact, metal1))
graph.add(Wire(metal1w, metal1, n(5, 2), n(7, 2)))
graph.add(Wire(metal1w, metal1, n(7, 1), n(7, 2)))
graph.add(Wire(metal1w, metal1, n(7, 2), n(7, 3)))

# input stage gate wiring
graph.add(Wire(polyw, poly, n(6, 1), n(6, 2)))
graph.add(Wire(polyw, poly, n(6, 2), n(6, 3)))

# input pin
graph.add(Wire(polyw, poly, n(6, 2), n(8, 2)))


solver = Solver(graph)
solver.solve()

layout = kl.Layout()
top_cell = layout.create_cell("TOP")

solver.produce(layout, top_cell)

layout.write(output)
print(f"{output} written.")

