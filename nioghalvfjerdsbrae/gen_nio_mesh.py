import issm  as im
import cslvr as cs
import numpy as np

#===============================================================================
# data preparation :
out_dir   = 'dump/meshes/'
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
md     = im.triangle(md, out_dir + mesh_name + '.exp', 50000)

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
md.inversion.vel_obs = vel

# refine mesh using surface velocities as metric :
md = im.bamg(md,
             'hmin',      5000,
             'hmax',      500000,
             'gradation', 3,
             'field',     u_mag,
             'err',       8)

# plot the mesh to be sure :
#im.plotmodel(md, 'data', 'mesh')

#===============================================================================
# save the state of the model :
im.savevars(out_dir + 'issm_refined_mesh.md', 'md', md)



