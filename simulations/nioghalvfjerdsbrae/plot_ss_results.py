import issm       as im
import cslvr      as cs
import numpy      as np
import fenics_viz as fv
import os

# directories for saving data :
mdl_odr = 'HO'
tmc     = True
name    = 'negis'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
var_dir = './dump/vars/' + mdl_pfx + '/'
plt_dir = './dump/images/' + mdl_pfx + '/'
out_dir = './dump/results/' + mdl_pfx + '/'
vtu_dir = plt_dir + 'vtu/'

# create the output directory if it does not exist :
d       = os.path.dirname(vtu_dir)
if not os.path.exists(d):
  os.makedirs(d)

# load the model mesh created by gen_nio_mesh.py :
md                    = im.model()
md.miscellaneous.name = name

# load the model mesh created by gen_nio_mesh.py :
md   = im.loadmodel(var_dir + 'negis_init.md')

# load the steady-state results :
md   = im.loadresultsfromdisk(md, './negis/negis.outbin')

#===============================================================================
# save .vtu files :
if tmc:  res = md.results.SteadystateSolution
else:    res = md.results.StressbalanceSolution

#===============================================================================
# plot the results :

p      = res.Pressure.flatten()
u_x    = res.Vx.flatten()
u_y    = res.Vy.flatten()
u_z    = res.Vz.flatten()

u      = [u_x, u_y, u_z]

#im.vtuwrite(u, 'u', md, vtu_dir + 'u.vtu')
#im.vtuwrite(p, 'p', md, vtu_dir + 'p.vtu')

p_b   = p[md.mesh.vertexonbase]
u_x_s = u_x[md.mesh.vertexonsurface]
u_y_s = u_y[md.mesh.vertexonsurface] 
u_z_s = u_z[md.mesh.vertexonsurface] 
u_s   = np.array([u_x_s, u_y_s, u_z_s])

# save the mesh coordinates and data for interpolation with CSLVR :
np.savetxt(out_dir + 'x.txt',   md.mesh.x2d)
np.savetxt(out_dir + 'y.txt',   md.mesh.y2d)
np.savetxt(out_dir + 'u_x.txt', u[0])
np.savetxt(out_dir + 'u_y.txt', u[1])
np.savetxt(out_dir + 'u_z.txt', u[2])
np.savetxt(out_dir + 'p.txt',   p)

u_mag     = np.sqrt(u_x_s**2 + u_y_s**2 + u_z_s**2 + 1e-16)
U_lvls    = np.array([u_mag.min(), 1e0, 5e0, 1e1, 5e1, 1e2, 5e2, 1e3,
                      u_mag.max()])

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

# the plot parameters will mostly stay the same for each plot :
plot_kwargs = {'direc'              : plt_dir, 
               'coords'             : (md.mesh.x2d, md.mesh.y2d),
               'cells'              : md.mesh.elements2d - 1,
               'figsize'            : (5,7.5),
               'cmap'               : 'viridis',
               'scale'              : 'lin',
               'numLvls'            : 10,
               'levels'             : None,
               'levels_2'           : None,
               'umin'               : None,
               'umax'               : None,
               'plot_tp'            : False,
               'tp_kwargs'          : tp_kwargs,
               'show'               : False,
               'hide_x_tick_labels' : True,
               'hide_y_tick_labels' : True,
               'xlabel'             : '',
               'ylabel'             : '',
               'equal_axes'         : True,
               'hide_axis'          : True,
               'colorbar_loc'       : 'right',
               'contour_type'       : 'filled',
               'extend'             : 'neither',
               'ext'                : '.pdf',
               'normalize_vec'      : True,
               'plot_quiver'        : False,
               'quiver_skip'        : 0,
               'quiver_kwargs'      : quiver_kwargs,
               'res'                : 150,
               'cb'                 : True,
               'cb_format'          : '%g'}

plot_kwargs['u']      = u_s
plot_kwargs['scale']  = 'lin'
plot_kwargs['name']   = 'U_S'
plot_kwargs['levels'] = U_lvls
plot_kwargs['title']  = r'$\underline{u} |_S^{\mathrm{ISSM}}$'
fv.plot_variable(**plot_kwargs)

if tmc:
  T      = res.Temperature.flatten()
  
  #im.vtuwrite(T, 'T', md, vtu_dir + 'T.vtu')
 
  T_b      = T[md.mesh.vertexonbase]
  T_s      = T[md.mesh.vertexonsurface]
  T_mid    = np.arange(242, 262, 2)
  T_b_mid  = np.arange(262, 274, 2) 
  T_b_lvls = np.hstack([T_b.min(), T_mid, T_b_mid, T_b.max()])
  T_s_lvls = np.hstack([T_s.min(), T_mid, T_s.max()])
  
  plot_kwargs['u']      = T_b
  plot_kwargs['scale']  = 'lin'
  plot_kwargs['name']   = 'T_B'
  plot_kwargs['levels'] = T_b_lvls
  plot_kwargs['title']  = r'$T |_B^{\mathrm{ISSM}}$'
  fv.plot_variable(**plot_kwargs)
  
  plot_kwargs['u']      = T_s
  plot_kwargs['scale']  = 'lin'
  plot_kwargs['name']   = 'T_S'
  plot_kwargs['levels'] = T_s_lvls
  plot_kwargs['title']  = r'$T |_S^{\mathrm{ISSM}}$'
  fv.plot_variable(**plot_kwargs)

bedmach  = cs.DataFactory.get_bedmachine(thklim=1.0)
dbm      = cs.DataInput(bedmach)

nio_params = {'llcrnrlat'    :  78.5,
              'llcrnrlon'    : -27.0,
              'urcrnrlat'    :  79.6,
              'urcrnrlon'    : -17.0,
              'scale_color'  : 'k',
              'scale_length' : 40.0,
              'scale_loc'    : 3,
              'figsize'      : (8,8),
              'lat_interval' : 0.5,
              'lon_interval' : 5,
              'plot_grid'    : True,
              'plot_scale'   : True,
              'axes_color'   : 'k'}

plt_params = {'direc'            : plt_dir,
              'coords'           : (md.mesh.x2d, md.mesh.y2d),
              'cells'            : md.mesh.elements2d - 1,
              'u2'               : None,
              'u2_levels'        : None,
              'u2_color'         : 'k',
              'u2_linewidth'     : 1.0,
              'cmap'             : 'viridis',
              'scale'            : 'lin',
              'umin'             : None,
              'umax'             : None,
              'numLvls'          : 12,
              'drawGridLabels'   : True,
              'levels_2'         : None,
              'tp'               : True,
              'tpAlpha'          : 0.5,
              'contour_type'     : 'filled',
              'params'           : nio_params,
              'extend'           : 'neither',
              'show'             : False,
              'ext'              : '.pdf',
              'res'              : 150,
              'cb'               : True,
              'cb_format'        : '%g',
              'zoom_box'         : False,
              'zoom_box_kwargs'  : None,
              'plot_pts'         : None,
              'plot_texts'       : None,
              'plot_continent'   : False,
              'cont_plot_params' : None,
              'drawcoastlines'   : True,
              'box_params'       : None}

T_b_lvls = np.hstack([T_b.min(), 258, 260, 262, 264, 268, 270, 272, 273, T_b.max()])
U_lvls   = np.array([u_mag.min(), 1e0, 5e0, 1e1, 5e1, 1e2, 5e2, 1e3, 2e3, 3e3,
                      u_mag.max()])

cs.plotIce(dbm,
           u      = T_b, 
           name   = 'T_B_nio',
           levels = T_b_lvls,
           title  = r'$T |_B^{\mathrm{ISSM}}$',
           **plt_params)

cs.plotIce(dbm,
           u      = u_s, 
           name   = 'U_S_nio',
           levels = U_lvls,
           title  = r'$\underline{u} |_S^{\mathrm{ISSM}}$',
           **plt_params)



