from fenics_viz      import *
import issm              as im
import cslvr             as cs
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.tri    as tri
import os, sys

# directories for saving data :
mdl_odr = 'HO'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
var_dir = './dump/vars/'
plt_dir = './dump/images/issm/' + mdl_pfx + '/'
out_dir = './dump/results/issm/' + mdl_pfx + '/'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# load the model mesh and vars created by gen_nio_vars.py :
md = im.loadmodel(var_dir + 'issm_vars.md')

# ISMIP_HOM experiment :
md.materials.rho_ice   = 910.0
md.materials.rho_water = 1028.0
md.constants.g         = 9.80665
md.constants.yts       = 31556926.0

#===============================================================================
# one friciton coefficient per node :
print_text('::: issm -- defining friction parameters :::', 'red')

md.friction.coefficient = 10 * np.ones(md.mesh.numberofvertices)
floating_v              = np.where(md.mask.groundedice_levelset < 0)[0]
grounded_v              = np.where(md.mask.groundedice_levelset > 0)[0]
md.friction.coefficient[floating_v] = 0       # no friction on shelves
md.friction.coefficient[grounded_v] = 100     # high friction where grounded

# one friction exponent (p,q) per element :
md.friction.p = np.ones(md.mesh.numberofelements)
md.friction.q = np.zeros(md.mesh.numberofelements)

#===============================================================================
# boundary conditions :
print_text('::: issm -- set boundary conditions :::', 'red')

# set the default boundary conditions for an ice-sheet :
md = im.SetMarineIceSheetBC(md)  # create placeholder arrays for indicies 

# extrude the mesh so that there are 5 cells in height :
md.extrude(6, 1.0)

# TODO: no geothermal flux for now :
md.basalforcings.geothermalflux = np.zeros(md.mesh.numberofvertices)

# set the lower-surface melting rate (lower surface-mass balance) :
md.basalforcings.floatingice_melting_rate = np.zeros(md.mesh.numberofvertices)
md.basalforcings.groundedice_melting_rate = np.zeros(md.mesh.numberofvertices)

# temerature :
md.thermal.spctemperature       = md.initialization.temperature

# spcthickness ?  dunno, but it needs to be set apparently :
md.masstransport.spcthickness   = np.nan * np.ones(md.mesh.numberofvertices)

# TODO: get real upper surface-mass balance :
md.smb.mass_balance = np.zeros(md.mesh.numberofvertices)

# set the flow equation of type `mdl_odr` defined above :
md = im.setflowequation(md, mdl_odr, 'all')
	
md.stressbalance.spcvx = np.nan * np.ones(md.mesh.numberofvertices)
md.stressbalance.spcvy = np.nan * np.ones(md.mesh.numberofvertices)
md.stressbalance.spcvz = np.nan * np.ones(md.mesh.numberofvertices)

## set for no-slip basal velocity BC (replaced with high friction above) :
#basal_v                         = md.mesh.vertexonbase
#md.stressbalance.spcvx[basal_v] = 0.0
#md.stressbalance.spcvy[basal_v] = 0.0
#md.stressbalance.spcvz[basal_v] = 0.0

#===============================================================================
# rheology :
print_text('::: issm -- construct ice rheological properties :::', 'red')

# `B` has one value per vertex :
n                       = 3.0                # Glen's exponent
spy                     = md.constants.yts   # s a^{-1}
A                       = 1e-16              # Pa^{-n} s^{-1}
B                       = (A / spy)**(-1/n)  # rate factor
md.materials.rheology_B = B * np.ones(md.mesh.numberofvertices)

# n has one value per element :
md.materials.rheology_n = n * np.ones(md.mesh.numberofelements)

#===============================================================================
# solve :
print_text('::: issm -- solving :::', 'red')

md.cluster = im.generic('name', im.gethostname(), 'np', 1)
md.verbose = im.verbose('convergence', True)
md         = im.solve(md, 'Stressbalance')

#===============================================================================
# plot the results :
print_text('::: issm -- plotting :::', 'red')

p    = md.results.StressbalanceSolution.Pressure[md.mesh.vertexonbase]
u_x  = md.results.StressbalanceSolution.Vx[md.mesh.vertexonsurface] 
u_y  = md.results.StressbalanceSolution.Vy[md.mesh.vertexonsurface] 
u_z  = md.results.StressbalanceSolution.Vz[md.mesh.vertexonsurface] 
u    = np.array([u_x.flatten(), u_y.flatten(), u_z.flatten()])
H    = md.geometry.thickness[md.mesh.vertexonsurface]
M    = md.mask.groundedice_levelset[md.mesh.vertexonbase] 

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
                 'alpha'          : 0.5}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : 'k',
                 'scale'          : 100,
                 'alpha'          : 0.8,
                 'width'          : 0.001,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

plot_variable(u                   = u,
              name                = 'U',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (5,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,#U_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,#True,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = True,#False,
              hide_y_tick_labels  = True,#False,
              xlabel              = '',#r'$x$',
              ylabel              = '',#r'$y$',
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

plot_variable(u                   = H,
              name                = 'H',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (5,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,#U_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,#True,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = True,#False,
              hide_y_tick_labels  = True,#False,
              xlabel              = '',#r'$x$',
              ylabel              = '',#r'$y$',
              equal_axes          = True,
              title               = r'$H^{\mathrm{ISSM}}$',
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',
              extend              = 'neither',
              ext                 = '.pdf',
              normalize_vec       = True,
              plot_quiver         = False,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')

plot_variable(u                   = M,
              name                = 'mask',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (5,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,#U_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,#True,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = True,#False,
              hide_y_tick_labels  = True,#False,
              xlabel              = '',#r'$x$',
              ylabel              = '',#r'$y$',
              equal_axes          = True,
              title               = r'$M^{\mathrm{ISSM}}$',
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',
              extend              = 'neither',
              ext                 = '.pdf',
              normalize_vec       = True,
              plot_quiver         = False,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')




