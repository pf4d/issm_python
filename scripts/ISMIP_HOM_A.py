from numpy           import *
from squaremesh      import *
from model           import *
from solve           import *
from setmask         import *
from setflowequation import *
from verbose         import *
#from plotmodel       import *
from SetIceSheetBC   import SetIceSheetBC
from socket          import gethostname
import matplotlib.pyplot as plt
import matplotlib.tri    as tri

# ISMIP HOM A experiment :
md = model()
md.miscellaneous.name = 'ISMIP_HOM_A'

# Geometry :
print '   Constructing Geometry'

# Define the geometry of the simulation :
#md = triangle(md, './exp/square.exp', 80000)
L  = 80000.0
n  = 20
md = squaremesh(md, L, L, n, n)
md = setmask(md, 'all', '')

#surface
md.geometry.surface = - md.mesh.x * tan(0.5*pi/180.0)

# base of ice sheet with 'L' the size of the side of the square :
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
md = SetIceSheetBC(md)  # create placeholder arrays for indicies 
md.extrude(5, 1.0)
md = setflowequation(md,'HO','all')
	
md.stressbalance.spcvx = np.nan * np.ones(md.mesh.numberofvertices)
md.stressbalance.spcvy = np.nan * np.ones(md.mesh.numberofvertices)
md.stressbalance.spcvz = np.nan * np.ones(md.mesh.numberofvertices)

# set no-slip basal velocity BC :
basal_v                         = md.mesh.vertexonbase
md.stressbalance.spcvx[basal_v] = 0.0
md.stressbalance.spcvy[basal_v] = 0.0
md.stressbalance.spcvz[basal_v] = 0.0

"""
  maxY=find(md.mesh.y==max(md.mesh.y) & md.mesh.x~=max(md.mesh.x) & md.mesh.x~=min(md.mesh.x));
	% create minY
	%->
	minY=find(md.mesh.y==min(md.mesh.y) & md.mesh.x~=max(md.mesh.x) & md.mesh.x~=min(md.mesh.x));
	% set the node that should be paired together
	% #md.stressbalance.vertex_pairing
	%->
	md.stressbalance.vertex_pairing=[minX,maxX;minY,maxY];
"""

# set periodic lateral boundary conditions :
minX = np.where(md.mesh.x == 0)[0] + 1
maxX = np.where(md.mesh.x == L)[0] + 1

# for y, maxX and minX should be excluded :
minY = np.where(np.logical_and(md.mesh.y == 0,
                               md.mesh.x != L,
                               md.mesh.x != 0))[0] + 1
maxY = np.where(np.logical_and(md.mesh.y == L,
                               md.mesh.x != L,
                               md.mesh.x != 0))[0] + 1

# set the nodes that should be paired together :
md.stressbalance.vertex_pairing = np.array([np.append(minX, minY),
                                            np.append(maxX, maxY)]).T
#md.stressbalance.vertex_pairing = np.vstack((np.vstack((minX+1,maxX+1)).T,
#                                             np.vstack((minY+1,maxY+1)).T))

# solve :
md.cluster = generic('name', gethostname(), 'np', 2)
md.verbose = verbose('convergence', True)
md         = solve(md, 'Stressbalance')

# plot the results :
p   = md.results.StressbalanceSolution.Pressure[md.mesh.vertexonbase]
u_x = md.results.StressbalanceSolution.Vx[md.mesh.vertexonsurface] 
u_y = md.results.StressbalanceSolution.Vy[md.mesh.vertexonsurface] 
u   = (u_x.flatten(), u_y.flatten()) 

from fenics_viz      import *

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 1.0,
                 'color'          : 'k',
                 'alpha'          : 0.5}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : 'k',
                 'scale'          : None,
                 'alpha'          : 0.8,
                 'width'          : 0.005,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

plot_variable(u                   = u,
              name                = 'U',
              direc               = './output/', 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (8,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,
              levels_2            = None,
              umin                = None,
              umax                = None,
              tp                  = True,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_ax_tick_labels = False,
              xlabel              = r'$x$',
              ylabel              = r'$y$',
              equal_axes          = True,
              title               = '',
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',
              extend              = 'neither',
              ext                 = '.png',
              normalize_vec       = True,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%.1e')




