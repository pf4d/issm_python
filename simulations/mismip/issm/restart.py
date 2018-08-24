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

# update the model with current output :
md   = im.loadresultsfromdisk(md, './lateral_slip/lateral_slip.outbin')

#===============================================================================

# define the geometry of the simulation :
tf     =  2.0         # [a] final time
dt     =  1           # [a] time step
dt_sav =  1.0         # [a] time interval to save data
cfl    =  0.5         # [--] CFL coefficient
nodes  =  4           # [--] number of nodes to use
ntpn   =  1           # [--] number of tasks per node
ntasks =  ntpn*nodes  # [--] number of processor cores to use
time   = '00:05:00'   # [s] time to complete

#===============================================================================
# tansient settings :
md.transient.isstressbalance      = 1
md.transient.isgroundingline      = 1
md.transient.ismasstransport      = 1
md.transient.issmb                = 1
md.transient.isthermal            = 0
md.timestepping.time_adapt        = 0
md.timestepping.cfl_coefficient   = cfl
md.timestepping.time_step         = dt
md.timestepping.final_time        = tf
md.settings.output_frequency      = int(dt_sav/dt)

md.transient.requested_outputs    = ['default',
                                     'GroundedArea',
                                     'FloatingArea',
                                     'IceVolume',
                                     'IceVolumeAboveFloatation']

#===============================================================================
# load the state of the model :
md = im.loadmodel(out_dir + 'mismip_init.md')

#===============================================================================
# solve :

# solve the transient :
#md.cluster = im.ollie('name', im.gethostname(), 'np', num_p)
md.cluster = im.ollie('name',            name,
                      'ntasks',          ntasks,
                      'nodes',           nodes,
                      'ntasks_per_node', ntpn,
                      'time',            time,
                      'login',           'ecumming')
md.verbose = im.verbose('solution', True, 'control', True, 'convergence', True)
md         = im.solve(md, 'Transient')

#===============================================================================
# save the state of the model :
# FIXME: the savevars method will work for small problems, but fails without 
#        error for large ones.
im.savevars(out_dir + name + '.md', 'md', md)

var_dict  = {'md.results.TransientSolution' : md.results.TransientSolution}
im.savevars(out_dir + name + '.shelve', var_dict)



