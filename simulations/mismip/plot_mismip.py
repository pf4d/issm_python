from fenics_viz      import *
from netCDF4         import Dataset
import issm              as im
import numpy             as np
import os

# directories for saving data :
mdl_odr = 'HO'
#name    = 'zero_stress'
#name    = 'no_slip'
#name    = 'zero_velocity'
#name    = 'marine_bc'
#name    = 'marine_bc_dt_1_y'
#name    = 'marine_bc_subelement'
#name    = 'shelf_bc_subelement'
#name    = 'shelf_bc_subelement_slip'
#name    = 'shelf_bc_subelement_slip_low_fric'
name    = 'shelf_bc_subelement_slip_fric_1e2'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/' + name + '/'
out_dir = './results/' + mdl_pfx + '/'

# load the model mesh created by gen_nio_mesh.py :
md = im.loadmodel(out_dir + name + '.md')

#===============================================================================
# load the model mesh created by gen_nio_mesh.py :

## set the current result number :
#rst_num = '07-11-2018-16-48-15-18062'
#rst_num = '07-12-2018-15-27-02-31448'
#
#md   = im.loadmodel(out_dir + 'mismip_init.md')
#
## get the current output :
#data = '/home/pf4d/software/issm/trunk/execution/%s-%s/%s.outbin'
#
## update the model with current output :
#md   = im.loadresultsfromdisk(md, data % (name,rst_num,name))

#===============================================================================
# plot the results :
print_text('::: issm -- plotting :::', 'red')

# get number of timesteps :
n      = len(md.results.TransientSolution)

# get the upper and lower surface vertex indicies :
vbed   = md.mesh.vertexonbase
vsrf   = md.mesh.vertexonsurface

# get mesh data :
coords = (md.mesh.x2d, md.mesh.y2d)
cells  = md.mesh.elements2d - 1

# set the mesh plot parameters :  
tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 0.5,
                 'color'          : 'k',
                 'alpha'          : 0.5}

# set the vector plot parameters :
quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : '0.5',
                 'scale'          : 100,
                 'alpha'          : 1.0,
                 'width'          : 0.001,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

numlvls = 8        # number of contour levels to plot
figsize = (8,1.5)  # figure size

# loop through all the timesteps and plot them :
for i in range(0,n,1):

  # get this solution :
  soln_i = md.results.TransientSolution[i]

  # the `plot_variable` function requires the output data be row vectors :
  S      = soln_i.Surface[vbed].flatten()
  B      = soln_i.Base[vbed].flatten()
  H      = soln_i.Thickness[vbed].flatten()
  p      = soln_i.Pressure[vbed].flatten()
  u_x    = soln_i.Vx[vsrf].flatten()
  u_y    = soln_i.Vy[vsrf].flatten()
  u_z    = soln_i.Vz[vsrf].flatten()
  ls     = soln_i.MaskGroundediceLevelset[vbed].flatten()

  # form the velocity vector :
  u      = np.array([u_x, u_y, u_z]) 

  # calculate the grounded/floating mask :
  mask   = (ls > 0).astype('int')
 
  # plot each of the variables of interest :
  plot_variable(u                   = u,
                name                = 'U_%i' % i,
                direc               = plt_dir,
                coords              = coords,
                cells               = cells,
                figsize             = figsize,
                cmap                = 'viridis',
                scale               = 'lin',
                numLvls             = numlvls,
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
                title               = r'$\underline{u} |_S$',
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
                cb_format           = '%.2f')
  
  plot_variable(u                   = mask,
                name                = 'mask_%i' % i,
                direc               = plt_dir, 
                coords              = coords,
                cells               = cells,
                figsize             = figsize,
                cmap                = 'gist_yarg',
                scale               = 'bool',
                numLvls             = numlvls,
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
                name                = 'S_%i' % i,
                direc               = plt_dir, 
                coords              = coords,
                cells               = cells,
                figsize             = figsize,
                cmap                = 'viridis',
                scale               = 'lin',
                numLvls             = numlvls,
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
                cb_format           = '%.1f')
  
  #plot_variable(u                   = B,
  #              name                = 'B_%i' % i,
  #              direc               = plt_dir, 
  #              coords              = coords,
  #              cells               = cells,
  #              figsize             = figsize,
  #              cmap                = 'viridis',
  #              scale               = 'lin',
  #              numLvls             = numlvls,
  #              levels              = None,
  #              levels_2            = None,
  #              umin                = None,
  #              umax                = None,
  #              plot_tp             = False,
  #              tp_kwargs           = tp_kwargs,
  #              show                = False,
  #              hide_x_tick_labels  = False,
  #              hide_y_tick_labels  = True,
  #              xlabel              = '',
  #              ylabel              = '',
  #              equal_axes          = True,
  #              title               = r'$B$',
  #              hide_axis           = False,
  #              colorbar_loc        = 'right',
  #              contour_type        = 'filled',
  #              extend              = 'neither',
  #              ext                 = '.pdf',
  #              normalize_vec       = True,
  #              plot_quiver         = False,
  #              quiver_kwargs       = quiver_kwargs,
  #              res                 = 150,
  #              cb                  = True,
  #              cb_format           = '%.1f')
  
  plot_variable(u                   = H,
                name                = 'H_%i' % i,
                direc               = plt_dir, 
                coords              = coords,
                cells               = cells,
                figsize             = figsize,
                cmap                = 'viridis',
                scale               = 'lin',
                numLvls             = numlvls,
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
                cb_format           = '%.1f')



