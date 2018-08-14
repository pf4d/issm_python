from   fenics_viz import print_text
import issm           as im
import numpy          as np
import os, sys

# directories for saving data :
mdl_odr = 'HO'
opt_met = 'm1qn3'#'brent'#
cst_met = 'morlighem'#'log''l2'#'cummings'#

name    = mdl_odr + '_' + cst_met + '_cost_' + opt_met

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
var_dir = '../dump/vars/'
plt_dir = '../dump/images/issm/' + mdl_pfx + '/' + opt_met + '/'
out_dir = '../dump/results/issm/' + mdl_pfx + '/' + opt_met + '/'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# load the model mesh created by gen_nio_mesh.py :
md                    = im.model()
md.miscellaneous.name = name

var_dict  = {'md.mesh'                      : md.mesh,
             'md.inversion.vx_obs'          : md.inversion.vx_obs,
             'md.inversion.vy_obs'          : md.inversion.vy_obs,
             'md.inversion.vel_obs'         : md.inversion.vel_obs,
             'md.mask.groundedice_levelset' : md.mask.groundedice_levelset,
             'md.mask.ice_levelset'         : md.mask.ice_levelset,
             'md.geometry.surface'          : md.geometry.surface,
             'md.geometry.base'             : md.geometry.base,
             'md.geometry.thickness'        : md.geometry.thickness,
             'md.friction_coefficient'      : md.friction.coefficient}
load_dict = im.loadvars(var_dir + 'issm_nio.shelve', var_dict)

md.mesh                      = load_dict['md.mesh']
md.inversion.vx_obs          = load_dict['md.inversion.vx_obs']
md.inversion.vy_obs          = load_dict['md.inversion.vy_obs']
md.inversion.vel_obs         = load_dict['md.inversion.vel_obs']
md.mask.groundedice_levelset = load_dict['md.mask.groundedice_levelset']
md.mask.ice_levelset         = load_dict['md.mask.ice_levelset']
md.geometry.surface          = load_dict['md.geometry.surface']
md.geometry.base             = load_dict['md.geometry.base']
md.geometry.thickness        = load_dict['md.geometry.thickness']
md.friction.coefficient      = load_dict['md.friction_coefficient']


#===============================================================================
# define constant values :
rhow   =  1028.0      # [kg m^-3] density of seawater
rhoi   =  910.0       # [kg m^-3] density of glacier ice
g      =  9.81        # [m s^2] gravitational acceleration
spy    =  31556926.0  # [s a^-1] seconds per year
Hini   =  100.0       # [m] initial ice thickness
Tm     =  273.15      # [K] melting temperature of ice
n      =  3.0         # [--] Glen's exponent
A      =  1e-16       # [Pa^{-n} s^{-1}] flow 
beta   =  1e4         # [Pa m^{-1/n} a^{-1/n}] friction coefficient
p      =  1.0         # [--] Paterson friction exponent one
q      =  0.0         # [--] Paterson friction exponent two
adot   =  0.3         # [m a^{-a}] surface-mass balance
tf     =  2.0         # [a] final time
dt     =  1.0         # [a] time step
dt_sav =  10.0        # [a] time interval to save data
cfl    =  0.5         # [--] CFL coefficient
q_geo  =  0.0         # [W m^-2] geothermal heat flux


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
Bf  =  (A / spy)**(-1/n)

#===============================================================================
# ISMIP_HOM experiment :
md.materials.rho_ice         = rhoi
md.materials.rho_water       = rhow
md.constants.g               = g
md.constants.yts             = spy
md.friction.p                = p * e_ones
md.friction.q                = q * e_ones
md.materials.rheology_B      = Bf * v_ones
md.materials.rheology_n      =  n * e_ones
#md.materials.rheology_B      = im.paterson((Tm - 20.0) * v_ones)
md.materials.rheology_law    = "None"

md.basalforcings.groundedice_melting_rate = 0.0 * v_ones
md.basalforcings.floatingice_melting_rate = 0.0 * v_ones
md.basalforcings.geothermalflux           = q_geo * v_ones
md.stressbalance.referential              = np.nan * A_ones
md.stressbalance.loadingforce             = np.nan * b_ones
md.thermal.spctemperature                 = md.initialization.temperature
md.smb.mass_balance                       = adot * v_ones
md.masstransport.spcthickness             = np.nan * v_ones


#===============================================================================
# boundary conditions :
print_text('::: issm -- set boundary conditions :::', 'red')

# set the default boundary conditions for an ice-sheet :
md = im.SetMarineIceSheetBC(md)  # create placeholder arrays for indicies 

# extrude the mesh so that there are 5 cells in height :
md.extrude(6, 1.0)

# set the flow equation of type `mdl_odr` defined above :
md = im.setflowequation(md, mdl_odr, 'all')
md.flowequation.fe_HO = 'P1'


#===============================================================================
# solve :
print_text('::: issm -- solving initial velocity :::', 'red')

md.cluster = im.generic('name', im.gethostname(), 'np', 1)
md.verbose = im.verbose('convergence', True)
md         = im.solve(md, 'Stressbalance')


#===============================================================================
# FIXME: since the model was extruded, we have to re-define the element-wise 
#        multiplicative identities.  This is not ideal :

# rank-zero tensor vertex ones vector :
v_ones = np.ones(md.mesh.numberofvertices)

# rank-zero tensor element ones vector :
e_ones = np.ones(md.mesh.numberofelements)

# rank-two tensor ones vector :
A_ones = np.ones((md.mesh.numberofvertices, 6))

# rank-one tensor ones vector :
b_ones = np.ones((md.mesh.numberofvertices, 3))


#===============================================================================
# data assimilation using L_BFGS_B method (otherwise issm uses Brent search) :
# FIXME: not obvious that you have to send the old issm::inversion instantiation
#        in order to keep all the old variables (vx_obs, etc.) :
if opt_met == 'm1qn3':
  md.inversion = im.m1qn3inversion(md.inversion)

# common parameters to both ``miqn3`` and ``brent`` :
md.inversion.iscontrol          = 1 # Do inversion? 1 = yes; 0 = no
md.inversion.incomplete_adjoint = 1 # 1 = linear viscosity; 0 = non-linear visc
md.inversion.control_parameters = ['FrictionCoefficient']
md.inversion.nsteps             = 3000 # number of inversion steps
md.inversion.min_parameters     = 1e-16 * v_ones
md.inversion.max_parameters     = 1e6   * v_ones

# form cost functions :
"""
   Available cost functions:
   101: SurfaceAbsVelMisfit
   102: SurfaceRelVelMisfit
   103: SurfaceLogVelMisfit
   104: SurfaceLogVxVyMisfit
   105: SurfaceAverageVelMisfit
   201: ThicknessAbsMisfit
   501: DragCoefficientAbsGradient
   502: RheologyBbarAbsGradient
   503: ThicknessAbsGradient
"""
if cst_met == 'cummings':
  md.inversion.cost_functions                   = [101, 103]#, 501]
  md.inversion.cost_functions_coefficients      = np.vstack([v_ones]*2).T
  md.inversion.cost_functions_coefficients[:,0] = 1e0
  md.inversion.cost_functions_coefficients[:,1] = 1e5
  #md.inversion.cost_functions_coefficients[:,2] = 1e0

elif cst_met == 'morlighem':
  md.inversion.cost_functions                   = [101, 103]#, 501]
  md.inversion.cost_functions_coefficients      = np.vstack([v_ones]*2).T
  md.inversion.cost_functions_coefficients[:,0] = 1e0
  md.inversion.cost_functions_coefficients[:,1] = 1e2
  #md.inversion.cost_functions_coefficients[:,2] = 1e-7

elif cst_met == 'log':
  md.inversion.cost_functions                   = [103]
  md.inversion.cost_functions_coefficients      = v_ones

elif cst_met == 'l2':
  md.inversion.cost_functions                   = [101]
  md.inversion.cost_functions_coefficients      = v_ones

# issm::m1qn3inversion-specific parameters :
if opt_met == 'm1qn3':
  md.inversion.maxsteps           = 3000  # max gradient evaluations
  md.inversion.maxiter            = 3000  # max objective evaluations
  md.inversion.dxmin              = 1e-16 # convergence criterion 1
  md.inversion.gttol              = 1e-16 # convergence criterion 2 :
                                          # ||g(X)|| / ||g(X0)||   where
                                          # g(X0): gradient at initial guess X0

# brent search specific parameters :
elif opt_met == 'brent':
  md.inversion.step_threshold          = 0.7 * np.ones(md.inversion.nsteps)
  md.inversion.maxiter_per_step        = 20  * np.ones(md.inversion.nsteps)
  md.inversion.gradient_scaling        = 50  * np.ones(md.inversion.nsteps)
  md.inversion.cost_function_threshold = np.nan 

## FIXME: it is not obvious that the velocity observations have to be extruded :
#md.inversion.vx_obs   = im.project3d(md,'vector',
#                                     md.inversion.vx_obs,'type','node')
#md.inversion.vy_obs   = im.project3d(md,'vector',
#                                     md.inversion.vy_obs,'type','node')
#md.inversion.vel_obs  = im.project3d(md,'vector',
#                                     md.inversion.vel_obs,'type','node')
#print md.inversion.vx_obs
#print md.inversion.vy_obs
#print md.inversion.vel_obs


#===============================================================================
# assimilate the velocity data :
md.cluster = im.generic('name', im.gethostname(), 'np', 2)
md.verbose = im.verbose('solution', True, 'control', True)
md         = im.solve(md, 'Stressbalance')

im.savevars(out_dir + name + '.md', 'md', md)



