import issm         as im
import numpy        as np
import os

# directories for saving data :
mdl_odr  = 'HO'
lat_slip = True
name     = 'lateral_slip_restart'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/' + name + '/'
out_dir = './results/' + mdl_pfx + '/'

# load the model mesh created by gen_nio_mesh.py :
md   = im.loadmodel(out_dir + 'mismip_restart.md')

#===============================================================================
# define new simulation parameters :
beta   =  2e3             # [Pa m^{-1/n} a^{-1/n}] friction coefficient
t0     =  13200.0         # [a] starting time
tf     =  20000.0         # [a] final time
dt     =  0.5             # [a] time step
dt_sav =  10.0            # [a] time interval to save data
cfl    =  0.5             # [--] CFL coefficient
nodes  =  1               # [--] number of nodes to use
ntpn   =  36              # [--] number of tasks per node
ntasks =  ntpn*nodes      # [--] number of processor cores to use
time   =  48*60           # [m] time to complete

# rank-zero tensor vertex ones vector :
v_ones = np.ones(md.mesh.numberofvertices)

# change the friction (to make the grounding line begin at around 450 km :
#md.friction.coefficient      = beta * v_ones

#===============================================================================
# tansient settings :

md.transient.isstressbalance      = 1
md.transient.isgroundingline      = 1
md.transient.ismasstransport      = 1
md.transient.issmb                = 1
md.transient.isthermal            = 0
md.timestepping.time_adapt        = 0
md.timestepping.cfl_coefficient   = cfl
md.timestepping.start_time        = t0
md.timestepping.final_time        = tf
md.timestepping.time_step         = dt
md.settings.output_frequency      = int(dt_sav/dt)

md.transient.requested_outputs    = ['default',
                                     'GroundedArea',
                                     'FloatingArea',
                                     'IceVolume',
                                     'IceVolumeAboveFloatation']

#===============================================================================
# solve :

# solve the transient :
#md.cluster = im.generic('name', im.gethostname(), 'np', ntasks)
md.cluster = im.ollie('name',            name,
                      'ntasks',          ntasks,
                      'nodes',           nodes,
                      'time',            time,
                      'login',           'ecumming')
md.verbose = im.verbose('solution', True, 'control', True, 'convergence', True)
md         = im.solve(md, 'Transient')

#===============================================================================
# save the state of the model :
# FIXME: the savevars method will work for small problems, but fails without 
#        error for large ones.
im.savevars(out_dir + name + '.md', 'md', md)



