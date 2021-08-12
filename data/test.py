import gmsh

# init gmsh
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)

gfile="03032015J_H2-HR.brep"
volumes = gmsh.model.occ.importShapes(gfile)
gmsh.model.occ.synchronize()

print(volumes)
pgrp = gmsh.model.addPhysicalGroup(3, [1])
gmsh.model.setPhysicalName(2, pgrp, "Cu")

"""
gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 2)
gmsh.option.setNumber("Mesh.Algorithm", 5)
gmsh.model.mesh.generate(3) 
gmsh.write("test.msh")
"""

gmsh.finalize()
