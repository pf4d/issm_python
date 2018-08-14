import issm       as im
import cslvr      as cs
import numpy      as np
import fenics_viz as fv
import os, sys

out_dir   = '../dump/vars/'
plt_dir   = '../dump/images/issm/'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# load the model mesh created by gen_nio_mesh.py :
md                    = im.model()
md.miscellaneous.name = 'Nioghalvfjerdsbrae'

var_dict  = {'md.mesh'              : md.mesh,
             'md.inversion.vx_obs'  : md.inversion.vx_obs,
             'md.inversion.vy_obs'  : md.inversion.vy_obs,
             'md.inversion.vel_obs' : md.inversion.vel_obs}
load_dict = im.loadvars(out_dir + 'issm_nio.shelve', var_dict)

md.mesh                = load_dict['md.mesh']
md.inversion.vx_obs    = load_dict['md.inversion.vx_obs']
md.inversion.vy_obs    = load_dict['md.inversion.vy_obs']
md.inversion.vel_obs   = load_dict['md.inversion.vel_obs']

#===============================================================================
# collect the raw data :
searise  = cs.DataFactory.get_searise()
bedmach  = cs.DataFactory.get_bedmachine(thklim=1.0)
mouginot = cs.DataFactory.get_mouginot()

# create data objects to use with varglas :
dsr     = cs.DataInput(searise)
dbm     = cs.DataInput(bedmach)
dmg     = cs.DataInput(mouginot)

# change the projection of all data to be the same as the mesh :
#dbm.interpolate_from_di(dsr, 'T', 'T', order=3)


#===============================================================================
# set grounded/floating ice mask :
cs.print_text('::: issm -- setting mask :::', 'red')

mask = im.InterpFromGridToMesh(dbm.x, dbm.y, dbm.data['mask'],
                               md.mesh.x, md.mesh.y, 0)[0]

# issm specifies floating ice as -1 :
mask            = np.round(mask).astype('int')
mask[mask == 0] =  1
mask[mask == 2] = -1

# ice is grounded for mask equal one
md.mask.groundedice_levelset = mask

# ice is present when negative :
md.mask.ice_levelset         = -1 * np.ones(md.mesh.numberofvertices)

#===============================================================================
# calculate input data :

T    = im.InterpFromGridToMesh(dsr.x, dsr.y, dsr.data['T'].astype('float64'),
                               md.mesh.x, md.mesh.y, 0)[0]

# geometry :
cs.print_text('::: issm -- constructing geometry :::', 'red')

# interpolate the data onto the refined mesh created by ``gen_nio_mesh.py`` :
S    = im.InterpFromGridToMesh(dbm.x, dbm.y, dbm.data['S'],
                               md.mesh.x, md.mesh.y, 0)[0]
B    = im.InterpFromGridToMesh(dbm.x, dbm.y, dbm.data['B'],
                               md.mesh.x, md.mesh.y, 0)[0]

# FIXME: the issm interpolation will result in areas with the surface ~1 km 
#        below sea level on a few nodes next to the ocean.  Thus:
S[S < 1.0] = 1.0
S    = S.astype('float64')    # upper surface
B    = B.astype('float64')    # lower surface
H    = S - B                  # thickness

# surface velocity observations :
# NOTE: the issm::InterpFromGridToMesh method needs type ``float64`` :
x1    = dmg.x.astype('float64')
y1    = dmg.y.astype('float64')
velx  = dmg.data['vx'].astype('float64')
vely  = dmg.data['vy'].astype('float64')
vel   = np.sqrt(velx**2 + vely**2 + 1e-16)

# interpolate the velocities onto the mesh for data assimilation :
u_x     = im.InterpFromGridToMesh(x1, y1, velx, md.mesh.x, md.mesh.y, 0)[0]
u_y     = im.InterpFromGridToMesh(x1, y1, vely, md.mesh.x, md.mesh.y, 0)[0]
u_mag   = im.InterpFromGridToMesh(x1, y1, vel,  md.mesh.x, md.mesh.y, 0)[0]

# calculate initial friction based on the SIA :
grad_S    = np.gradient(S)
gS_mag    = np.sqrt(grad_S[0]**2 + grad_S[1]**2 + 1e-16)
rhoi      = 910.0
g         = 9.81
u_0       = 1e-2
u_mag_c   = u_mag.copy()
u_mag_c[u_mag_c < u_0] = u_0
beta_sia  = np.sqrt( rhoi * g * H * gS_mag / u_mag_c )

# set the issm model variables :
md.geometry.surface           = S
md.geometry.base              = B
md.geometry.thickness         = H
md.inversion.vx_obs           = u_x
md.inversion.vy_obs           = u_y
md.inversion.vel_obs          = u_mag
md.friction.coefficient       = beta_sia
md.initialization.temperature = T


#===============================================================================
# save the state of the model :
var_dict  = {'md.mask.groundedice_levelset'  : md.mask.groundedice_levelset,
             'md.mask.ice_levelset'          : md.mask.ice_levelset,
             'md.initialization.temperature' : md.initialization.temperature,
             'md.geometry.surface'           : md.geometry.surface,
             'md.geometry.base'              : md.geometry.base,
             'md.geometry.thickness'         : md.geometry.thickness,
             'md.inversion.vx_obs'           : md.inversion.vx_obs,
             'md.inversion.vy_obs'           : md.inversion.vy_obs,
             'md.inversion.vel_obs'          : md.inversion.vel_obs,
             'md.friction_coefficient'       : md.friction.coefficient}
im.savevars(out_dir + 'issm_nio.shelve', var_dict)


#===============================================================================
# plot the data :
tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 0.1,
                 'color'          : 'k',
                 'alpha'          : 0.5}

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

plt_kwargs['name']   = 'T'
plt_kwargs['title']  =  r'$T |_S^{\mathrm{ISSM}}$'
fv.plot_variable(u=T, **plt_kwargs)

plt_kwargs['name']   = 'mask'
plt_kwargs['title']  =  ''#r'$\mathrm{mask} |^{\mathrm{ISSM}}$'
plt_kwargs['scale']  = 'bool'
plt_kwargs['cmap']   = 'gist_gray'
fv.plot_variable(u=mask, **plt_kwargs)

U_lvls = np.array([u_mag.min(), 1e0, 5e0, 1e1, 5e1, 1e2, 5e2, 1e3, u_mag.max()])
plt_kwargs['name']        = 'U_ob'
plt_kwargs['title']       = r'$\underline{u}_{\mathrm{ob}} |_S^{\mathrm{ISSM}}$'
plt_kwargs['levels']      = U_lvls
plt_kwargs['scale']       = 'lin'
plt_kwargs['cmap']        = 'viridis'
plt_kwargs['plot_quiver'] = True
fv.plot_variable(u=np.array([u_x.flatten(), u_y.flatten()]), **plt_kwargs)

beta_lvls = np.array([beta_sia.min()**2, 1e7, 1e8, 1e9, 5e9, 1e10, 5e10,
                      beta_sia.max()**2])
plt_kwargs['name']        = 'beta_sia'
plt_kwargs['title']       = r'$\beta_{\mathrm{SIA}}^2 |^{\mathrm{ISSM}}$'
plt_kwargs['levels']      = beta_lvls
plt_kwargs['scale']       = 'lin'
plt_kwargs['cmap']        = 'viridis'
plt_kwargs['plot_quiver'] = False
fv.plot_variable(u=beta_sia**2, **plt_kwargs)



