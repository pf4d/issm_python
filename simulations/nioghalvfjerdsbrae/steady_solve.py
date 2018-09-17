import issm              as im
import cslvr             as cs
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.tri    as tri
import os, sys

# directories for saving data :
mdl_odr  = 'HO'
tmc      = True
computer = 'not_local'
name     = 'negis'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
var_dir = './dump/vars/' + mdl_pfx + '/'

# load the model mesh created by gen_nio_mesh.py :
md                    = im.model()
md.miscellaneous.name = name

var_dict  = {'md.mesh'                       : md.mesh,
             'md.inversion.vx_obs'           : md.inversion.vx_obs,
             'md.inversion.vy_obs'           : md.inversion.vy_obs,
             'md.inversion.vel_obs'          : md.inversion.vel_obs,
             'md.mask.groundedice_levelset'  : md.mask.groundedice_levelset,
             'md.mask.ice_levelset'          : md.mask.ice_levelset,
             'md.geometry.surface'           : md.geometry.surface,
             'md.geometry.base'              : md.geometry.base,
             'md.geometry.thickness'         : md.geometry.thickness,
             'md.initialization.temperature' : md.initialization.temperature,
             'md.friction_coefficient'       : md.friction.coefficient}
load_dict = im.loadvars(var_dir + 'issm_nio.shelve', var_dict)

md.mesh                       = load_dict['md.mesh']
md.inversion.vx_obs           = load_dict['md.inversion.vx_obs']
md.inversion.vy_obs           = load_dict['md.inversion.vy_obs']
md.inversion.vel_obs          = load_dict['md.inversion.vel_obs']
md.mask.groundedice_levelset  = load_dict['md.mask.groundedice_levelset']
md.mask.ice_levelset          = load_dict['md.mask.ice_levelset']
md.geometry.surface           = load_dict['md.geometry.surface']
md.geometry.base              = load_dict['md.geometry.base']
md.geometry.thickness         = load_dict['md.geometry.thickness']
md.initialization.temperature = load_dict['md.initialization.temperature']
md.friction.coefficient       = load_dict['md.friction_coefficient']


#===============================================================================
# define constant values :
rhow   =  1028.0        # [kg m^-3] density of seawater
rhoi   =  910.0         # [kg m^-3] density of glacier ice
g      =  9.81          # [m s^2] gravitational acceleration
spy    =  31556926.0    # [s a^-1] seconds per year
Hini   =  100.0         # [m] initial ice thickness
Tm     =  273.15        # [K] melting temperature of ice
n      =  3.0           # [--] Glen's exponent
A      =  2e-17         # [Pa^{-n} s^{-1}] flow 
p      =  1.0           # [--] Paterson friction exponent one
q      =  0.0           # [--] Paterson friction exponent two
adot   =  0.3           # [m a^{-a}] surface-mass balance
tf     =  2.0           # [a] final time
dt     =  1.0           # [a] time step
dt_sav =  10.0          # [a] time interval to save data
cfl    =  0.5           # [--] CFL coefficient
q_geo  =  0.0#0.042     # [W m^-2] geothermal heat flux
a_T_l  =  3.985e-13     # [s^-1 Pa^-3] lower bound of flow-rate constant
a_T_u  =  1.916e3       # [s^-1 Pa^-3] upper bound of flow-rate constant
Q_T_l  =  6e4           # [J mol^-1] lower bound of creep activation energy
Q_T_u  =  13.9e4        # [J mol^-1] upper bound of creep activation energy
R      =  8.3144621     # [J mol^-1] universal gas constant
nodes  =  1             # [--] number of nodes to use
ntpn   =  36            # [--] number of tasks per node
ntasks =  nodes*ntpn    # [--] number of processor cores to use
time   =  24*60         # [m] time to complete
part   = 'smp'          # [--] partition of ``ollie`` to use

#===============================================================================
# set up element-wise multiplicative identities :

# rank-zero tensor vertex ones vector :
v_ones = np.ones(md.mesh.numberofvertices)

# rank-zero tensor element ones vector :
e_ones = np.ones(md.mesh.numberofelements)

# rank-two tensor ones vector :
A_ones = np.ones((md.mesh.numberofvertices, 6))

# rank-one tensor ones vector :
b_ones = np.ones((md.mesh.numberofvertices, 3))

# indicies where ice is floating :
flt    = np.where(md.mask.groundedice_levelset < 0)[0]

# specify rheology parameters :
T         = md.initialization.temperature
warm      = T >= Tm - 10.0
a_T       = a_T_l * v_ones
a_T[warm] = a_T_u
Q_T       = Q_T_l * v_ones
Q_T[warm] = Q_T_u
A         = a_T * np.exp( - Q_T / (R * T) )
Bf        = A**(-1/n)

#===============================================================================
# define constants :
md.materials.rho_ice         = rhoi
md.materials.rho_water       = rhow
md.constants.g               = g
md.constants.yts             = spy

md.friction.p                = p * e_ones
md.friction.q                = q * e_ones
md.friction.coefficient      = 5e5 * v_ones
md.friction.coefficient[flt] = 0.0  # zero friction over shelves

md.materials.rheology_n      =  n * e_ones
#md.materials.rheology_B      =  (2e-17 / spy)**(-1/n) * v_ones
md.materials.rheology_B      =  Bf
md.materials.rheology_law    = "Arrhenius"

# initialization FIXME: must be done or ``SteadyState`` solve will throw a fit :
md.initialization.vx          = 0.0 * v_ones
md.initialization.vy          = 0.0 * v_ones
md.initialization.vz          = 0.0 * v_ones
md.initialization.vel         = 0.0 * v_ones
md.initialization.pressure    = 0.0 * v_ones

#md.initialization.vx         = md.inversion.vx_obs
#md.initialization.vy         = md.inversion.vy_obs
#md.initialization.vz         = 0.0 * v_ones
#md.initialization.vel        = md.inversion.vel_obs
#md.initialization.pressure   = rhoi * g * md.geometry.thickness

# boundary conditions :
md.basalforcings.groundedice_melting_rate = 0.0 * v_ones
md.basalforcings.floatingice_melting_rate = 0.0 * v_ones
md.basalforcings.geothermalflux           = q_geo * v_ones

# thermal model :
#md.initialization.temperature = Tm * v_ones
md.initialization.waterfraction           = 0.0 * v_ones
md.initialization.watercolumn             = 0.0 * v_ones
md.thermal.stabilization                  = 2 # 1 == art'f'ial diff', 2 == SUPG
md.thermal.isenthalpy                     = 1
md.steadystate.maxiter                    = 25

# FIXME: ``SteadyState`` throws an error if this is not zero :
md.timestepping.time_step                 = 0.0

#===============================================================================
# boundary conditions :

# set the default boundary conditions for an ice-sheet :
md = im.SetMarineIceSheetBC(md)

# ensure Neumann conditions are imposed on lateral faces :
md.stressbalance.spcvx        = np.nan * v_ones
md.stressbalance.spcvy        = np.nan * v_ones
md.stressbalance.spcvz        = np.nan * v_ones
md.stressbalance.referential  = np.nan * A_ones
md.stressbalance.loadingforce =    0.0 * b_ones

lat                           = md.mesh.vertexonboundary
md.stressbalance.spcvx[lat]   = md.inversion.vx_obs[lat]
md.stressbalance.spcvy[lat]   = md.inversion.vy_obs[lat]

# extrude the mesh so that there are 5 cells in height :
md.extrude(20, 1.0)

# get the floating base :
flt = np.logical_and(md.mask.groundedice_levelset == -1, md.mesh.vertexonbase)

# calculate the hydrostatic-pressure-melting point :
H   = md.geometry.surface - md.geometry.base
Tpm = Tm - md.materials.beta * rhoi * g * H

# FIXME: this has to be done post-extrude, unlike the momentum ``spc`` stuff :
md.thermal.spctemperature      = md.initialization.temperature.copy()

# set the basal boundary condition to Neumann :
md.thermal.spctemperature[md.mesh.vertexonbase] = np.nan
#md.thermal.spctemperature[flt]                  = Tpm[flt]

# set the flow equation of type `mdl_odr` defined above :
md = im.setflowequation(md, mdl_odr, 'all')
md.flowequation.fe_HO = 'P1'


#===============================================================================
# save the state of the model :
im.savevars(var_dir + 'negis_init.md', 'md', md)


#===============================================================================
# solve :

if computer is not "local":
  md.cluster = im.ollie('name',            name,
                        'partition',       part,
                        'ntasks',          ntasks,
                        'nodes',           nodes,
                        'time',            time,
                        'login',           'ecumming')
else:
  md.cluster = im.generic('name', im.gethostname(), 'np', 2)
md.verbose = im.verbose('solution', True, 'control', True, 'convergence', True)
if tmc: md = im.solve(md, 'SteadyState')
else:   md = im.solve(md, 'StressBalance')



