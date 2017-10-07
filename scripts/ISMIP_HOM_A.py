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
n  = 50
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
md.friction.coefficient = 10 * np.ones(md.mesh.numberofvertices)
#floating_v = numpy.where(md.mask.groundedice_levelset < 0)[0]
#md.friction.coefficient[floating_v] = 0

# one friciton exponent (p,q) per element :
md.friction.p = ones(md.mesh.numberofelements)
md.friction.q = zeros(md.mesh.numberofelements)

print '   Construct ice rheological properties'

# The rheology parameters sit in the material section :

# B has one value per vertex :
n   = 3.0
spy = 31556926.0    # s a^{-1}
A   = 1e-16         # Pa^{-n} s^{-1}
B   = (A / spy)**(-1/n)
md.materials.rheology_B = B * ones(md.mesh.numberofvertices)

# n has one value per element :
md.materials.rheology_n = n * ones(md.mesh.numberofelements)

print '   Set boundary conditions'

# Set the default boundary conditions for an ice-sheet :
md = SetIceSheetBC(md)  # create placeholder arrays for indicies 
md.extrude(6, 1.0)
md = setflowequation(md,'HO','all')
	
md.stressbalance.spcvx = np.nan * np.ones(md.mesh.numberofvertices)
md.stressbalance.spcvy = np.nan * np.ones(md.mesh.numberofvertices)
md.stressbalance.spcvz = np.nan * np.ones(md.mesh.numberofvertices)

# set no-slip basal velocity BC :
basal_v                         = md.mesh.vertexonbase
md.stressbalance.spcvx[basal_v] = 0.0
md.stressbalance.spcvy[basal_v] = 0.0
md.stressbalance.spcvz[basal_v] = 0.0

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

# solve :
md.cluster = generic('name', gethostname(), 'np', 1)
md.verbose = verbose('convergence', True)
md         = solve(md, 'Stressbalance')

# plot the results :
p   = md.results.StressbalanceSolution.Pressure[md.mesh.vertexonbase]
u_x = md.results.StressbalanceSolution.Vx[md.mesh.vertexonsurface] 
u_y = md.results.StressbalanceSolution.Vy[md.mesh.vertexonsurface] 
u   = np.array([u_x.flatten(), u_y.flatten()]) 

from fenics_viz      import *

U_lvls = array([u.min(), 10, 20, 30, 40, 50, 60, 70, 80, u.max()])

mdl_odr = 'BP'

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
              direc               = './images/issm/' + mdl_odr + '/', 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (8,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = U_lvls,
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
              title               = r'$\underline{u} |_S^{\mathrm{ISSM}}$',
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',
              extend              = 'neither',
              ext                 = '.pdf',
              normalize_vec       = True,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')



