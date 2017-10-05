from numpy           import *
from triangle        import *
from model           import *
from solve           import *
from setmask         import *
from setflowequation import *
#from plotmodel       import *
from SetIceSheetBC   import SetIceSheetBC
from socket          import gethostname

# ISMIP HOM A experiment :
md = model()
md.miscellaneous.name = 'ISMIP_HOM_A'

# Geometry :
print '   Constructing Geometry'

# Define the geometry of the simulation :
md = triangle(md, './exp/square.exp', 80000)
md = setmask(md, 'all', '')
md = setflowequation(md,'HO','all')

#surface
md.geometry.surface = - md.mesh.x * tan(0.5*pi/180.0)

# base of ice sheet with 'L' the size of the side of the square :
L                = max(md.mesh.x) - min(md.mesh.x)
md.geometry.base = + md.geometry.surface - 1000.0 \
                   + 500.0 * sin(md.mesh.x*2*pi/L) * sin(md.mesh.y*2*pi/L)

#thickness is the difference between surface and base :
md.geometry.thickness = md.geometry.surface - md.geometry.base

# plot the geometry to check it out :
#plotmodel(md, 'data', md.geometry.thickness)

print '   Defining friction parameters'

# one friciton coefficient per node :
md.friction.coefficient = 200.0 * ones(md.mesh.numberofvertices)
#md.friction.coefficient[numpy.nonzero(md.mask.groundedice_levelset < 0)[0]] = 0

# one friciton exponent (p,q) per element :
md.friction.p = ones(md.mesh.numberofelements)
md.friction.q = ones(md.mesh.numberofelements)

print '   Construct ice rheological properties'

# The rheology parameters sit in the material section :

# B has one value per vertex :
md.materials.rheology_B = 6.8067e7 * ones(md.mesh.numberofvertices)

# n has one value per element :
md.materials.rheology_n = 3 * ones(md.mesh.numberofelements)

print '   Set boundary conditions'

# Set the default boundary conditions for an ice-sheet :
md.extrude(10, 1.0)
md = SetIceSheetBC(md)

# solve :
md.cluster = generic('name', gethostname(), 'np', 2)
md         = solve(md, 'Stressbalance')

# Fields and tolerances to track changes :
field_names      = ['Vx',   'Vy',   'Vz',  'Vel',  'Pressure']
field_tolerances = [ 1e-08,  1e-08,  1e-06, 1e-08,  1e-08]
field_values     = [md.results.StressbalanceSolution.Vx,
						     	  md.results.StressbalanceSolution.Vy,
						     	  md.results.StressbalanceSolution.Vz,
						     	  md.results.StressbalanceSolution.Vel,
						     	  md.results.StressbalanceSolution.Pressure]



