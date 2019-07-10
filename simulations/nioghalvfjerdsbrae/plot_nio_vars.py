import issm       as im
import cslvr      as cs
import numpy      as np
import fenics_viz as fv
import os

mdl_odr   = 'HO'
name      = 'negis'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr

#===============================================================================
# data preparation :
var_dir   = './dump/vars/' + mdl_pfx + '/'
plt_dir   = './dump/images/'

# instantiate a generic model instance :
md                    = im.model()
md.miscellaneous.name = name

# load the state of the model :
var_dict  = {'md.mesh'                       : md.mesh,
             'md.mask.groundedice_levelset'  : md.mask.groundedice_levelset,
             'md.mask.ice_levelset'          : md.mask.ice_levelset,
             'md.initialization.temperature' : md.initialization.temperature,
             'md.geometry.surface'           : md.geometry.surface,
             'md.geometry.base'              : md.geometry.base,
             'md.geometry.thickness'         : md.geometry.thickness,
             'md.inversion.vx_obs'           : md.inversion.vx_obs,
             'md.inversion.vy_obs'           : md.inversion.vy_obs,
             'md.inversion.vel_obs'          : md.inversion.vel_obs,
             'md.friction_coefficient'       : md.friction.coefficient}
load_dict = im.loadvars(var_dir + 'issm_nio.shelve', var_dict)

md.mesh    = load_dict['md.mesh']
u_x        = load_dict['md.inversion.vx_obs']
u_y        = load_dict['md.inversion.vy_obs']
u_mag      = load_dict['md.inversion.vel_obs']
mask       = load_dict['md.mask.groundedice_levelset']
S          = load_dict['md.geometry.surface']
B          = load_dict['md.geometry.base']
H          = load_dict['md.geometry.thickness']
T          = load_dict['md.initialization.temperature']
beta_sia   = load_dict['md.friction_coefficient']


#===============================================================================
# plot the data :
tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 0.1,
                 'color'          : 'k',
                 'alpha'          : 0.8}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : '0.0',
                 'scale'          : 100,
                 'alpha'          : 1.0,
                 'width'          : 0.001,
                 'headwidth'      : 3.0,
                 'headlength'     : 3.0,
                 'headaxislength' : 3.0}

plt_kwargs  =  {'direc'              : plt_dir,
                'coords'             : (md.mesh.x, md.mesh.y),
                'cells'              : md.mesh.elements - 1,
                'figsize'            : (5.6,8),
                'cmap'               : 'viridis',
                'scale'              : 'lin',
                'numLvls'            : 10,
                'levels'             : None,#U_lvls,
                'levels_2'           : None,
                'umin'               : None,
                'umax'               : None,
                'plot_tp'            : False,
                'tp_kwargs'          : tp_kwargs,
                'show'               : False,
                'hide_x_tick_labels' : True,
                'hide_y_tick_labels' : True,
                'xlabel'             : "",#r'$x$',
                'ylabel'             : "",#r'$y$',
                'equal_axes'         : True,
                'title'              : r'$S |^{\mathrm{ISSM}}$',
                'hide_axis'          : True,
                'colorbar_loc'       : 'right',
                'contour_type'       : 'filled',
                'extend'             : 'neither',
                'ext'                : '.pdf',
                'normalize_vec'      : True,
                'plot_quiver'        : False,
                'quiver_kwargs'      : quiver_kwargs,
                'res'                : 150,
                'cb'                 : True,
                'cb_format'          : '%g'}

plt_kwargs['name']   = 'S'
plt_kwargs['title']  =  r'$S |^{\mathrm{ISSM}}$'
fv.plot_variable(u=S, **plt_kwargs)

plt_kwargs['name']   = 'B'
plt_kwargs['title']  =  r'$B |^{\mathrm{ISSM}}$'
fv.plot_variable(u=B, **plt_kwargs)

plt_kwargs['name']   = 'H'
plt_kwargs['title']  =  r'$H |^{\mathrm{ISSM}}$'
fv.plot_variable(u=H, **plt_kwargs)

plt_kwargs['name']    = 'mask'
plt_kwargs['title']   =  ''#r'$\mathrm{mask} |^{\mathrm{ISSM}}$'
plt_kwargs['scale']   = 'bool'
#plt_kwargs['cmap']    = 'RdGy'
plt_kwargs['plot_tp'] = True
fv.plot_variable(u=mask, **plt_kwargs)

T_lvls = np.array([T.min(), 242, 244, 246, 248, 250, 252, 254, 256, T.max()])
plt_kwargs['levels']  = T_lvls
plt_kwargs['scale']   = 'lin'
plt_kwargs['plot_tp'] = False
plt_kwargs['name']    = 'T'
plt_kwargs['title']   =  r'$T |_S^{\mathrm{ISSM}}$'
fv.plot_variable(u=T, **plt_kwargs)

U_lvls = np.array([u_mag.min(), 1e0, 5e0, 1e1, 5e1, 1e2, 5e2, 1e3, u_mag.max()])
plt_kwargs['name']        = 'U_ob'
plt_kwargs['title']       = r'$\underline{u}_{\mathrm{ob}} |_S^{\mathrm{ISSM}}$'
plt_kwargs['levels']      = U_lvls
plt_kwargs['scale']       = 'lin'
plt_kwargs['cmap']        = 'viridis'
#plt_kwargs['plot_quiver'] = True
plt_kwargs['plot_tp']     = False
fv.plot_variable(u=np.array([u_x.flatten(), u_y.flatten()]), **plt_kwargs)

beta_lvls = np.array([beta_sia.min(), 2e1, 1e2, 5e2, 1e3, 5e3, 1e4, 2e4,
                      beta_sia.max()])
plt_kwargs['name']        = 'beta_sia'
plt_kwargs['title']       = r'$\beta_{\mathrm{SIA}} |^{\mathrm{ISSM}}$'
plt_kwargs['levels']      = beta_lvls
plt_kwargs['scale']       = 'lin'
plt_kwargs['cmap']        = 'viridis'
plt_kwargs['plot_quiver'] = False
fv.plot_variable(u=beta_sia, **plt_kwargs)

bedmach  = cs.DataFactory.get_bedmachine(thklim=1.0)

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
              'coords'           : (md.mesh.x, md.mesh.y),
              'cells'            : md.mesh.elements - 1,
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

S_lvls = np.array([S.min(), 10, 50, 100, 200, 400, 600, 800, 1000, S.max()])
cs.plotIce(bedmach,
           u      = S,
           name   = 'S_nio',
           levels = S_lvls,
           title  = r'$S |^{\mathrm{ISSM}}$',
           **plt_params)

B_lvls = np.array([B.min(), -500, -250, -100, 0, 100, 250, 500, 750, 1000,
                   B.max()])
cs.plotIce(bedmach,
           u      = B,
           name   = 'B_nio',
           levels = B_lvls,
           title  = r'$B |^{\mathrm{ISSM}}$',
           **plt_params)

H_lvls = np.array([H.min(), 50, 100, 250, 500, 750, 1000, 1250,  H.max()])
cs.plotIce(bedmach,
           u      = H,
           name   = 'H_nio',
           levels = H_lvls,
           title  = r'$H |^{\mathrm{ISSM}}$',
           **plt_params)


T_lvls = np.array([T.min(), 251, 252, 253, 254, 255, T.max()])
cs.plotIce(bedmach,
           u      = T,
           name   = 'T_nio',
           levels = T_lvls,
           title  = r'$T |_S^{\mathrm{ISSM}}$',
           **plt_params)

U_lvls = np.array([u_mag.min(), 1e1, 1e2, 2.5e2, 4e2, 5e2, 7.5e2, 1e3, 1.2e3,
                   2e3, u_mag.max()])
cs.plotIce(bedmach,
           u      = np.array([u_x.flatten(), u_y.flatten()]),
           name   = 'U_ob_nio',
           levels = U_lvls,
           title  = r'$\underline{u}_{\mathrm{ob}} |_S^{\mathrm{ISSM}}$',
           **plt_params)

beta_lvls = np.array([beta_sia.min(), 2e1, 1e2, 5e2, 1e3, 5e3, 1e4,
                      beta_sia.max()])
cs.plotIce(bedmach,
           u      = beta_sia,
           name   = 'beta_sia_nio',
           levels = beta_lvls,
           title  = r'$\beta_{\mathrm{SIA}} |^{\mathrm{ISSM}}$',
           **plt_params)

plt_params['scale']   = 'bool'
plt_params['tp']      = True
cs.plotIce(bedmach,
           u      = mask,
           name   = 'mask_nio',
           levels = None,
           title  = r'',
           **plt_params)



