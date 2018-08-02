import issm   as im
import numpy  as np
import os

# set the current result number :
rst_num = '05-24-2018-09-44-10-7150'
rst_num = '05-25-2018-14-17-01-21210'

# directories for saving data :
mdl_odr = 'HO'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/'# + rst_num + '/'
out_dir = './results/' + mdl_pfx + '/'

# create the output directory if it does not exist :
d       = os.path.dirname(plt_dir)
if not os.path.exists(d):
  os.makedirs(d)

md = im.loadmodel(out_dir + 'mismip_short.md')

## load the model mesh created by gen_nio_mesh.py :
#md   = im.loadmodel(out_dir + 'mismip_init.md')
#
## get the current output :
#data = '/home/pf4d/software/issm/trunk/execution/MISMIP-%s/MISMIP.outbin'
#
## update the model with current output :
#md   = im.loadresultsfromdisk(md, data % rst_num)

# get the upper and lower surface vertex indicies :
vbed   = md.mesh.vertexonbase
vsrf   = md.mesh.vertexonsurface

# get this solution :
soln_i = md.results.TransientSolution[-1]

# the `plot_variable` function requires the output data be row vectors :
S      = soln_i.Surface.flatten()
B      = soln_i.Base.flatten()
H      = soln_i.Thickness.flatten()
p      = soln_i.Pressure.flatten()
u_x    = soln_i.Vx.flatten()
u_y    = soln_i.Vy.flatten()
u_z    = soln_i.Vz.flatten()

u      = [u_x, u_y, u_z]

im.vtuwrite(u, 'u', md, plt_dir + 'u.vtu')
im.vtuwrite(p, 'p', md, plt_dir + 'p.vtu')
im.vtuwrite(S, 'S', md, plt_dir + 'S.vtu')



