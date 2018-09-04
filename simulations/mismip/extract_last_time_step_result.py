import issm         as im
import numpy        as np
import os

# directories for saving data :
mdl_odr  = 'HO'
lat_slip = True
name     = 'lateral_slip'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/' + name + '/'
out_dir = './results/' + mdl_pfx + '/'

# load the model mesh created by gen_nio_mesh.py :
md   = im.loadmodel(out_dir + 'mismip_init.md')

# save the initial thickness and bed for the initial mesh :
Hini = md.geometry.thickness
Bini = md.geometry.base

# update the model with current output :
md   = im.loadresultsfromdisk(md, './lateral_slip/lateral_slip.outbin')

# get the last timestep :
res  = md.results.TransientSolution[-1]

# fix the mesh z coordinate first :
B         = res.Base.flatten()
H         = res.Thickness.flatten()
md.mesh.z = B + H / Hini * (md.mesh.z - Bini)

# initialize the model with data from the last timestep :
md.initialization.vx          = res.Vx
md.initialization.vy          = res.Vy
md.initialization.vz          = res.Vz
md.initialization.vel         = res.Vel
md.initialization.pressure    = res.Pressure
md.geometry.surface           = res.Surface
md.geometry.base              = res.Base
md.geometry.thickness         = res.Thickness
md.mask.groundedice_levelset  = res.MaskGroundediceLevelset

# get rid of the other data :
md.results = im.results()

# save the current state of the model as a new model :
im.savevars(out_dir + 'mismip_restart.md', 'md', md)



