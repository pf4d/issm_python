from fenics_viz      import *
import issm              as im
import numpy             as np

# directories for saving data :
mdl_odr = 'HO'
name    = 'lateral_slip_restart'
t0      = 20000
dt      = 10.0

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/' + name + '/'
out_dir = './results/' + mdl_pfx + '/'

# load the model mesh created by gen_nio_mesh.py :
md   = im.loadmodel(out_dir + 'mismip_init.md')

# update the model with current output :
md   = im.loadresultsfromdisk(md, './lateral_slip_restart/lateral_slip.outbin')
#md   = im.loadmodel(out_dir + 'lateral_slip_restart.md')

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
tp_kwargs     = {'linestyle'        : '-',
                 'lw'               : 0.5,
                 'color'            : 'k',
                 'alpha'            : 0.5}

# set the vector plot parameters :
quiver_kwargs = {'pivot'            : 'middle',
                 'color'            : 'k',
                 'scale'            : 150,
                 'alpha'            : 0.5,
                 'width'            : 0.001,
                 'headwidth'        : 3.0, 
                 'headlength'       : 3.0, 
                 'headaxislength'   : 3.0}

# the plot parameters will mostly stay the same for each plot :
plot_kwargs = {'direc'              : plt_dir, 
               'coords'             : coords,
               'cells'              : cells,
               'figsize'            : (8, 1.5),
               'cmap'               : 'viridis',
               'scale'              : 'lin',
               'numLvls'            : 8,
               'levels'             : None,
               'levels_2'           : None,
               'umin'               : None,
               'umax'               : None,
               'plot_tp'            : False,
               'tp_kwargs'          : tp_kwargs,
               'show'               : False,
               'hide_x_tick_labels' : False,
               'hide_y_tick_labels' : True,
               'xlabel'             : '',
               'ylabel'             : '',
               'equal_axes'         : True,
               'hide_axis'          : False,
               'colorbar_loc'       : 'right',
               'contour_type'       : 'filled',
               'extend'             : 'neither',
               'ext'                : '.pdf',
               'normalize_vec'      : True,
               'plot_quiver'        : True,
               'quiver_skip'        : 0,
               'quiver_kwargs'      : quiver_kwargs,
               'res'                : 150,
               'cb'                 : True,
               'cb_format'          : '%.1f'}


# loop through all the timesteps and plot them :
for i in range(0,n,10):

  # get this solution :
  soln_i = md.results.TransientSolution[i]

  # the `plot_variable` function requires the output data be row vectors :
  S       = soln_i.Surface[vbed].flatten()
  B       = soln_i.Base[vbed].flatten()
  H       = soln_i.Thickness[vbed].flatten()
  p       = soln_i.Pressure[vbed].flatten()
  u_x_s   = soln_i.Vx[vsrf].flatten()
  u_y_s   = soln_i.Vy[vsrf].flatten()
  u_z_s   = soln_i.Vz[vsrf].flatten()
  u_x_b   = soln_i.Vx[vbed].flatten()
  u_y_b   = soln_i.Vy[vbed].flatten()
  u_z_b   = soln_i.Vz[vbed].flatten()
  ls      = soln_i.MaskGroundediceLevelset[vbed].flatten()

  # form the velocity vectors :
  u_s    = np.array([u_x_s, u_y_s, u_z_s])
  u_b    = np.array([u_x_b, u_y_b, u_z_b])

  # calculate the grounded/floating mask :
  mask   = (ls > 0).astype('int')

  # the simulation time :
  time = t0 + (i + 1)*dt

  # plot the upper-surface height :
  plot_kwargs['title']       = r'$S$'
  plot_kwargs['u']           = S
  plot_kwargs['name']        = 'S_%i' % time
  plot_kwargs['scale']       = 'lin'
  plot_kwargs['cmap']        = 'viridis'
  plot_kwargs['cb_format']   = '%.1f'
  plot_kwargs['plot_tp']     = False
  plot_variable(**plot_kwargs)

  # plot the lower-surface height :
  plot_kwargs['title']       = r'$B$'
  plot_kwargs['u']           = B
  plot_kwargs['name']        = 'B_%i' % time
  plot_kwargs['scale']       = 'lin'
  plot_kwargs['cmap']        = 'viridis'
  plot_kwargs['cb_format']   = '%.1f'
  plot_kwargs['plot_tp']     = False
  plot_variable(**plot_kwargs)

  # plot the ice thickness :
  plot_kwargs['title']       = r'$H$'
  plot_kwargs['u']           = H
  plot_kwargs['name']        = 'H_%i' % time
  plot_kwargs['scale']       = 'lin'
  plot_kwargs['cmap']        = 'viridis'
  plot_kwargs['cb_format']   = '%.1f'
  plot_kwargs['plot_tp']     = False
  plot_variable(**plot_kwargs)

  # plot the vertical component of the upper-surface velocity :
  plot_kwargs['title']       = r'$u_z |_S$'
  plot_kwargs['u']           = u_z_s
  plot_kwargs['name']        = 'u_z_s_%i' % time
  plot_kwargs['scale']       = 'lin'
  plot_kwargs['cmap']        = 'viridis'
  plot_kwargs['cb_format']   = '%.1e'
  plot_kwargs['plot_tp']     = False
  plot_variable(**plot_kwargs)

  # plot the vertical component of the lower-surface velocity :
  plot_kwargs['title']       = r'$u_z |_B$'
  plot_kwargs['u']           = u_z_b
  plot_kwargs['name']        = 'u_z_b_%i' % time
  plot_kwargs['scale']       = 'lin'
  plot_kwargs['cmap']        = 'viridis'
  plot_kwargs['cb_format']   = '%.1e'
  plot_kwargs['plot_tp']     = False
  plot_variable(**plot_kwargs)

  # plot the upper-surface velocity :
  plot_kwargs['title']       = r'$\underline{u} |_S$'
  plot_kwargs['u']           = u_s
  plot_kwargs['name']        = 'U_s_%i' % time
  plot_kwargs['scale']       = 'log'
  plot_kwargs['cmap']        = 'viridis'
  plot_kwargs['cb_format']   = '%.1e'
  plot_kwargs['plot_tp']     = False
  plot_variable(**plot_kwargs)

  # plot the lower-surface velocity :
  plot_kwargs['title']       = r'$\underline{u} |_B$'
  plot_kwargs['u']           = u_b
  plot_kwargs['name']        = 'U_b_%i' % time
  plot_kwargs['scale']       = 'log'
  plot_kwargs['cmap']        = 'viridis'
  plot_kwargs['cb_format']   = '%.1e'
  plot_kwargs['plot_tp']     = False
  plot_variable(**plot_kwargs)

  # plot the floating-ice mask :
  plot_kwargs['title']       = r'mask'
  plot_kwargs['u']           = mask
  plot_kwargs['name']        = 'mask_%i' % time
  plot_kwargs['scale']       = 'bool'
  plot_kwargs['cmap']        = 'gist_yarg'
  plot_kwargs['cb_format']   = '%g'
  plot_kwargs['plot_tp']     = True
  plot_variable(**plot_kwargs)
  


