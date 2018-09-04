import issm       as im
import cslvr      as cs
import numpy      as np
import fenics_viz as fv
import os

#===============================================================================
# data preparation :
out_dir   = './dump/vars/'
msh_dir   = './dump/meshes/'
mesh_name = 'nioghalvfjerdsbrae'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

#===============================================================================
# use issm to create mesh for 79 N Glacier :
cs.print_text('::: issm -- constructing mesh :::', 'red')

# instantiate a generic model instance :
md                    = im.model()
md.miscellaneous.name = 'Nioghalvfjerdsbrae'

# use cslvr to get the velocity data from which to refine :
mouginot = cs.DataFactory.get_mouginot()
dmg      = cs.DataInput(mouginot)

# get the togography data :
bedmachine = cs.DataFactory.get_bedmachine()
dbm        = cs.DataInput(bedmachine)

dbm.interpolate_from_di(dmg, 'vx', 'vx', order=1)
dbm.interpolate_from_di(dmg, 'vy', 'vy', order=1)

# define the geometry of the simulation :
#md     = im.triangle(md, out_dir + mesh_name + '.exp', 50000)
md    = im.bamg(md,
                'domain', msh_dir + mesh_name + '.exp',
                'hmax',   5000)

# change data type to that required by InterpFromGridToMesh() :
x1    = dbm.x.astype('float64')
y1    = dbm.y.astype('float64')
velx  = dbm.data['vx'].astype('float64')
vely  = dbm.data['vy'].astype('float64')

# get the gradient of the mask :
mask      = dbm.data['mask'].copy()
mask[mask < 2.0] = 0.0
gradm     = np.gradient(mask)
lat_mask  = gradm[0]**2 + gradm[1]**2
lat_mask  = lat_mask > 0.0

# calculate the velocity magnitude :
vel   = np.sqrt(velx**2 + vely**2)

# increase the velocity at the grounding line or ice/ocean interface :
vel[lat_mask] = 100000.0

# interpolate the data onto the issm mesh :
u_mag = im.InterpFromGridToMesh(x1, y1, vel, md.mesh.x, md.mesh.y, 0)[0]

# refine mesh using surface velocities as metric :
md    = im.bamg(md,
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
im.savevars(out_dir + 'issm_nio.shelve', 'md.mesh', md.mesh)


