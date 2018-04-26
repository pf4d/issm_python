import issm     as im
import cslvr    as cs
import numpy    as np
import os, sys

var_dir  = './dump/vars/'
mesh_dir = './dump/meshes/'

# create the output directory if it does not exist :
d       = os.path.dirname(var_dir)
if not os.path.exists(d):
  os.makedirs(d)

# load the model mesh created by gen_nio_mesh.py :
md = im.loadmodel(mesh_dir + 'issm_refined_mesh.md')

#===============================================================================
# collect the raw data :
#searise  = cs.DataFactory.get_searise()
bedmach  = cs.DataFactory.get_bedmachine(thklim=1.0)
#mouginot = cs.DataFactory.get_mouginot()

# create data objects to use with varglas :
#dsr     = cs.DataInput(searise)
dbm     = cs.DataInput(bedmach)
#dmg     = cs.DataInput(mouginot)

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
# geometry :
cs.print_text('::: issm -- constructing geometry :::', 'red')

S    = im.InterpFromGridToMesh(dbm.x, dbm.y, dbm.data['S'],
                               md.mesh.x, md.mesh.y, 0)[0]
B    = im.InterpFromGridToMesh(dbm.x, dbm.y, dbm.data['B'],
                               md.mesh.x, md.mesh.y, 0)[0]
S    = S.astype('float64')
B    = B.astype('float64')

# upper surface :
md.geometry.surface = S

# lower surface :
md.geometry.base    = B

#thickness is the difference between surface and base :
md.geometry.thickness = md.geometry.surface - md.geometry.base

# save the state of the model :
im.savevars(var_dir + 'issm_vars.md', 'md', md)



