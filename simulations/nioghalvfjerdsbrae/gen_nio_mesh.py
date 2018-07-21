import issm       as im
import cslvr      as cs
import numpy      as np
import fenics_viz as fv

#===============================================================================
# data preparation :
out_dir   = 'dump/meshes/'
plt_dir   = 'dump/images/'
mesh_name = 'nioghalvfjerdsbrae_3D'

#===============================================================================
# use issm to create mesh for 79 N Glacier :
cs.print_text('::: issm -- constructing mesh :::', 'red')

# instantiate a generic model instance :
md                    = im.model()
md.miscellaneous.name = 'Nioghalvfjerdsbrae'

# use cslvr to get the velocity data from which to refine :
mouginot = cs.DataFactory.get_mouginot()
dmg      = cs.DataInput(mouginot)

# define the geometry of the simulation :
#md     = im.triangle(md, out_dir + mesh_name + '.exp', 50000)
md     = im.bamg(md,
                 'domain', out_dir + mesh_name + '.exp',
                 'hmax', 10000)

# change data type to that required by InterpFromGridToMesh() :
x1     = dmg.x.astype('float64')
y1     = dmg.y.astype('float64')
velx   = dmg.data['vx'].astype('float64')
vely   = dmg.data['vy'].astype('float64')

# calculate the velocity magnitude :
vel   = np.sqrt(velx**2 + vely**2)

# interpolate the data onto the issm mesh :
vx    = im.InterpFromGridToMesh(x1, y1, velx, md.mesh.x, md.mesh.y, 0)[0]
vy    = im.InterpFromGridToMesh(x1, y1, vely, md.mesh.x, md.mesh.y, 0)[0]
u_mag = im.InterpFromGridToMesh(x1, y1, vel,  md.mesh.x, md.mesh.y, 0)[0]

# while we have the velocity observations, save them to the model now for 
# inversion later :
md.inversion.vx_obs  = velx
md.inversion.vy_obs  = vely
md.inversion.vel_obs = u_mag

# refine mesh using surface velocities as metric :
md = im.bamg(md,
             'hmax',      100000,
             'hmin',      500,
             'gradation', 100,
             'field',     u_mag,
             'err',       8)

# FIXME: doesn't work :
# plot the mesh to be sure :
#im.plotmodel(md, 'data', 'mesh')

#===============================================================================
# save the state of the model :
# FIXME: the savevars method will work for small problems, but fails without 
#        error for large ones.  Thus this doesn't work :
#
#          im.savevars(out_dir + 'issm_refined_mesh.md', 'md', md)
#
#        and instead we do this :
out_file = open(out_dir + 'issm_refined_mesh.md', 'w')
im.save(out_file, md)


#===============================================================================
# plot the velocity overlaid on the mesh :
vx     = im.InterpFromGridToMesh(x1, y1, velx, md.mesh.x, md.mesh.y, 0)[0]
vy     = im.InterpFromGridToMesh(x1, y1, vely, md.mesh.x, md.mesh.y, 0)[0]
u      = np.array([vx.flatten(), vy.flatten()]) 
U_mag  = np.sqrt(u[0]**2 + u[1]**2 + 1e-16)
U_lvls = np.array([U_mag.min(), 1e0, 5e0, 1e1, 5e1, 1e2, 5e2, 1e3, U_mag.max()])

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 0.5,
                 'color'          : 'k',
                 'alpha'          : 0.5}

# set the vector plot parameters :
quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : '0.0',
                 'scale'          : 100,
                 'alpha'          : 1.0,
                 'width'          : 0.001,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

fv.plot_variable(u                   = u,
                 name                = 'U',
                 direc               = plt_dir, 
                 coords              = (md.mesh.x, md.mesh.y),
                 cells               = md.mesh.elements - 1,
                 figsize             = (5.7,8),
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
                 hide_x_tick_labels  = True,
                 hide_y_tick_labels  = True,
                 xlabel              = "",#r'$x$',
                 ylabel              = "",#r'$y$',
                 equal_axes          = True,
                 title               = r'$\underline{u}_{\mathrm{ob}} |_S^{\mathrm{ISSM}}$',
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



