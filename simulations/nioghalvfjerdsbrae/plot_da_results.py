from fenics_viz   import *
import issm           as im
import numpy          as np
import os, sys

# directories for saving data :
mdl_odr = 'HO'
opt_met = 'm1qn3'#'brent'#
cst_met = 'log'#'cummings'#'l2'#'morlighem'#

name    = mdl_odr + '_' + cst_met + '_cost_' + opt_met

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
var_dir = './dump/vars/' + mdl_pfx + '/'
plt_dir = './dump/images/' + mdl_pfx + '/' + opt_met + '/'
out_dir = './dump/results/' + mdl_pfx + '/' + opt_met + '/'

# load the model mesh created by gen_nio_mesh.py :
md                    = im.model()
md.miscellaneous.name = name

# load the model mesh created by gen_nio_mesh.py :
md   = im.loadmodel(var_dir + 'negis_init.md')

# load the steady-state results :
md   = im.loadresultsfromdisk(md, './' + name + '/' + name + '.outbin')

#===============================================================================
# plot the results :
print_text('::: issm -- plotting :::', 'red')

p    = md.results.StressbalanceSolution.Pressure[md.mesh.vertexonbase]
u_x  = md.results.StressbalanceSolution.Vx[md.mesh.vertexonsurface]
u_y  = md.results.StressbalanceSolution.Vy[md.mesh.vertexonsurface]
u_z  = md.results.StressbalanceSolution.Vz[md.mesh.vertexonsurface]
u    = np.array([u_x.flatten(), u_y.flatten(), u_z.flatten()])

u_mag  = np.sqrt(u[0]**2 + u[1]**2 + u[2]**2 + 1e-16)
U_lvls = np.array([u_mag.min(), 1e0, 5e0, 1e1, 5e1, 1e2, 5e2, 1e3, u_mag.max()])

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 1.0,
                 'color'          : 'k',
                 'alpha'          : 0.5}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : 'k',
                 'scale'          : 100,
                 'alpha'          : 0.5,
                 'width'          : 0.001,
                 'headwidth'      : 3.0,
                 'headlength'     : 3.0,
                 'headaxislength' : 3.0}

plot_variable(u                   = u,
              name                = 'U_opt_%s' % name,
              direc               = plt_dir,
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (5,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = U_lvls,
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
              title               = r'$\underline{u}^* |_S^{\mathrm{ISSM}}$',
              hide_axis           = True,
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



