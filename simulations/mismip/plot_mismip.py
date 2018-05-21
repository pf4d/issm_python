from fenics_viz      import *
from netCDF4         import Dataset
import issm              as im
import numpy             as np
import os

# directories for saving data :
mdl_odr = 'HO'
tf      = 100

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/'
out_dir = './results/' + mdl_pfx + '/'

# load the model mesh created by gen_nio_mesh.py :
md = im.loadmodel(out_dir + 'mismip_%i_years.md' % int(tf))

#===============================================================================
# plot the results :
print_text('::: issm -- plotting :::', 'red')

vbed = md.mesh.vertexonbase
vsrf = md.mesh.vertexonsurface
S    = md.results.TransientSolution[-1].Surface[vbed].flatten()
B    = md.results.TransientSolution[-1].Base[vbed].flatten()
H    = md.results.TransientSolution[-1].Thickness[vbed].flatten()
p    = md.results.TransientSolution[-1].Pressure[vbed].flatten()
u_x  = md.results.TransientSolution[-1].Vx[vsrf].flatten()
u_y  = md.results.TransientSolution[-1].Vy[vsrf].flatten()
u_z  = md.results.TransientSolution[-1].Vz[vsrf].flatten()
u    = np.array([u_x, u_y, u_z]) 

ls   = md.results.TransientSolution[-1].MaskGroundediceLevelset[vbed].flatten()
mask = (ls > 0).astype('int')

## save the mesh coordinates and data for interpolation with CSLVR :
#np.savetxt(out_dir + 'x.txt',   md.mesh.x2d)
#np.savetxt(out_dir + 'y.txt',   md.mesh.y2d)
#np.savetxt(out_dir + 'u_x.txt', u[0])
#np.savetxt(out_dir + 'u_y.txt', u[1])
#np.savetxt(out_dir + 'u_z.txt', u[2])
#np.savetxt(out_dir + 'p.txt',   p)

U_mag  = np.sqrt(u[0]**2 + u[1]**2 + u[2]**2 + 1e-16)
U_lvls = np.array([U_mag.min(), 10, 20, 30, 40, 50, 60, 70, 80, U_mag.max()])

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 0.5,
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
              figsize             = (8,2),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,#U_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = True,
              xlabel              = '',
              ylabel              = '',
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

plot_variable(u                   = mask,
              name                = 'mask',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (8,2),
              cmap                = 'gist_yarg',
              scale               = 'bool',
              numLvls             = 10,
              levels              = None,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = True,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = True,
              xlabel              = '',
              ylabel              = '',
              equal_axes          = True,
              title               = r'mask',
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

plot_variable(u                   = S,
              name                = 'S',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (8,2),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = True,
              xlabel              = '',
              ylabel              = '',
              equal_axes          = True,
              title               = r'$S$',
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

plot_variable(u                   = B,
              name                = 'B',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (8,2),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = True,
              xlabel              = '',
              ylabel              = '',
              equal_axes          = True,
              title               = r'$B$',
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

plot_variable(u                   = H,
              name                = 'H',
              direc               = plt_dir, 
              coords              = (md.mesh.x2d, md.mesh.y2d),
              cells               = md.mesh.elements2d - 1,
              figsize             = (8,2),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = True,
              xlabel              = '',
              ylabel              = '',
              equal_axes          = True,
              title               = r'$H$',
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



