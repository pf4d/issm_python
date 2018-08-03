from fenics_viz      import *
import issm              as im
import numpy             as np
import os

# directories for saving data :
mdl_odr = 'HO'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/issm/' + mdl_pfx + '/'
out_dir = './results/issm/' + mdl_pfx + '/'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# ISMIP HOM A experiment :
md = im.model()
md.miscellaneous.name = 'ISMIP_HOM_A'

# Geometry :
print_text('::: issm -- constructing geometry :::', 'red')

# Define the geometry of the simulation :
#md = triangle(md, './exp/square.exp', 80000)
L  = 80000.0
n  = 15
md = im.squaremesh(md, L, L, n, n)
md = im.setmask(md, 'all', '')

#surface
md.geometry.surface = - md.mesh.x * np.tan(0.5*np.pi/180.0)

# base of ice sheet with 'L' the size of the side of the square :
md.geometry.base = + md.geometry.surface - 1000.0 \
                   + 500.0 * np.sin(md.mesh.x*2*np.pi/L) \
                           * np.sin(md.mesh.y*2*np.pi/L)

#thickness is the difference between surface and base :
md.geometry.thickness = md.geometry.surface - md.geometry.base

# ISMIP_HOM experiment :
md.materials.rho_ice = 910.0
md.constants.g       = 9.80665
md.constants.yts     = 31556926.0

# set up element-wise multiplicative identities :
v_ones = np.ones(md.mesh.numberofvertices)  # rank-zero tensor vertex
e_ones = np.ones(md.mesh.numberofelements)  # rank-zero tensor element

# one friciton coefficient per node :
print_text('::: issm -- defining friction parameters :::', 'red')

md.friction.coefficient = 10 * v_ones
#floating_v = numpy.where(md.mask.groundedice_levelset < 0)[0]
#md.friction.coefficient[floating_v] = 0

# one friciton exponent (p,q) per element :
md.friction.p = 1.0 * e_ones
md.friction.q = 0.0 * e_ones

print_text('::: issm -- construct ice rheological properties :::', 'red')

# The rheology parameters sit in the material section :

# B has one value per vertex :
n   = 3.0
spy = md.constants.yts   # s a^{-1}
A   = 1e-16              # Pa^{-n} s^{-1}
B   = (A / spy)**(-1/n)
md.materials.rheology_B = B * v_ones

# n has one value per element :
md.materials.rheology_n = n * e_ones

print_text('::: issm -- set boundary conditions :::', 'red')

# Set the default boundary conditions for an ice-sheet :
md = im.SetIceSheetBC(md)  # create placeholder arrays for indicies 
md.extrude(6, 1.0)
md = im.setflowequation(md, mdl_odr, 'all')

# FIXME: if you do not call ``md.extrude()`` before, ``md.mesh.vertexonbase``
#        does not exist.
basal_v  = md.mesh.vertexonbase

# FIXME: since the model was extruded, we have to re-define the element-wise 
#        multiplicative identities.  This is not ideal :
v_ones = np.ones(md.mesh.numberofvertices)  # rank-zero tensor vertex
e_ones = np.ones(md.mesh.numberofelements)  # rank-zero tensor element
	
md.stressbalance.spcvx = np.nan * v_ones
md.stressbalance.spcvy = np.nan * v_ones
md.stressbalance.spcvz = np.nan * v_ones

# set no-slip basal velocity BC :
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
print_text('::: issm -- solving :::', 'red')

md.cluster = im.generic('name', im.gethostname(), 'np', 1)
md.verbose = im.verbose('convergence', True)
md         = im.solve(md, 'Stressbalance')

# plot the results :
print_text('::: issm -- plotting :::', 'red')

p   = md.results.StressbalanceSolution.Pressure[md.mesh.vertexonbase]
u_x = md.results.StressbalanceSolution.Vx[md.mesh.vertexonsurface] 
u_y = md.results.StressbalanceSolution.Vy[md.mesh.vertexonsurface] 
u_z = md.results.StressbalanceSolution.Vz[md.mesh.vertexonsurface] 
u   = np.array([u_x.flatten(), u_y.flatten(), u_z.flatten()]) 

# save the mesh coordinates and data for interpolation with CSLVR :
np.savetxt(out_dir + 'x.txt',   md.mesh.x2d)
np.savetxt(out_dir + 'y.txt',   md.mesh.y2d)
np.savetxt(out_dir + 'u_x.txt', u[0])
np.savetxt(out_dir + 'u_y.txt', u[1])
np.savetxt(out_dir + 'u_z.txt', u[2])
np.savetxt(out_dir + 'p.txt',   p)

U_mag  = np.sqrt(u[0]**2 + u[1]**2 + u[2]**2 + 1e-16)
U_lvls = np.array([U_mag.min(), 10, 20, 30, 40, 50, 60, 70, 80, U_mag.max()])

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 1.0,
                 'color'          : 'k',
                 'alpha'          : 0.2}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : '0.5',
                 'scale'          : None,
                 'alpha'          : 1.0,
                 'width'          : 0.005,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

plot_variable(u                   = u,
              name                = 'U',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (7,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = U_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = True,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = False,
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
              plot_quiver         = True,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')



