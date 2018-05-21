from netCDF4    import Dataset
from fenics_viz import *
import issm         as im
import numpy        as np
import os

# directories for saving data :
mdl_odr = 'HO'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/'
out_dir = './results/' + mdl_pfx + '/'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# ISMIP HOM A experiment :
md = im.model()
md.miscellaneous.name = 'MISMIP'

#===============================================================================
print_text('::: issm -- initializing model :::', 'red')

# define the geometry of the simulation :
Lx     =  640000.0    # [m] domain length (along ice flow)
Ly     =  80000.0     # [m] domain width (across ice flow)
B0     = -150.0       # [m] bedrock topography at x = 0
B2     = -728.8       # [m] second bedrock topography coefficient
B4     =  343.91      # [m] third bedrock topography coefficient
B6     = -50.57       # [m] second bedrock topography coefficient
xbar   =  300000.0    # [m] characteristic along-flow length scale of bedrock
fc     =  4000.0      # [m] characteristic width of channel walls
dc     =  500.0       # [m] depth of the trough compared to its walls
wc     =  24000.0     # [m] half width of the trough
zd     = -720.0       # [m] maximum depth of the bedrock topography
thklim =  10.0        # [m] thickness limit
rhow   =  1028.0      # [kg m^-3] density of seawater
rhoi   =  910.0       # [kg m^-3] density of glacier ice
g      =  9.81        # [m s^2] gravitational acceleration
spy    =  31556926.0  # [s a^-1] seconds per year
Hini   =  thklim      # [m] initial ice thickness
Tm     =  273.15      # [K] melting temperature of ice
n      =  3.0         # [--] Glen's exponent
A      =  2e-17       # [Pa^{-n} s^{-1}] flow 
beta   =  1e4         # [Pa m^{-1/n} a^{-1/n}] friction coefficient
p      =  3.0         # [--] Paterson flow exponent one
q      =  0.0         # [--] Paterson flow exponent two
adot   =  0.3         # [m a^{-a}] surface-mass balance
tf     =  35000.0     # [a] final time
dt     =  10.0        # [a] time step
cfl    =  0.5         # [--] CFL coefficient

# create an empty rectangular mesh :
#md     = triangle(md, './exp/MismipDomain.exp', 10000)
md     = im.squaremesh(md, Lx, Ly, nx=64, ny=20)
md     = im.setmask(md, 'all', '')

# the vertex ones vector (element-wise multiplicative identity) :
v_ones = np.ones(md.mesh.numberofvertices)

# the element ones vector (element-wise multiplicative identity) :
e_ones = np.ones(md.mesh.numberofelements)

# interpolate the thickness data onto the mesh :
#data   = Dataset('data/weertman-A2.2e-17-ssa.nc', mode = 'r')
#xd     = np.array(data.variables['x'][:])
#yd     = np.array(data.variables['y'][:])
#Hd     = np.array(data.variables['thickness'][:])
#H      = im.InterpFromGridToMesh(xd, yd, Hd, md.mesh.x, md.mesh.y, thklim)[0]
H      = Hini * v_ones

# eq'n (3)
xt     = md.mesh.x / xbar

# eq'n (2) :
Bx     = B0 + B2*xt**2 + B4*xt**4 + B6*xt**6

# eq'n (4) :
By     = + dc / (1 + np.exp(-2*(md.mesh.y - Ly/2 - wc) / fc)) \
         + dc / (1 + np.exp( 2*(md.mesh.y - Ly/2 + wc) / fc))

# lower topography (eq'n 1) :
zb = np.maximum(Bx + By, zd*v_ones)

# upper surface which does not take into account floatation :
S  = zb + H

# grounded ice level-set floatation :
ls = H + rhow / rhoi * zb

# get indicies of grounded (gnd) and floating (flt) ice :
gnd = ls >  0
flt = ls <= 0

# ice is grounded where == 1 :
mask = gnd.astype('int')

# correct upper surface to be in equilibrium with the floatation height :
S[flt] = H[flt] * (1 - rhoi / rhow)

# lower surface :
B = S - H;

# specify rheology parameters :
Bf  =  (A / spy)**(-1/n)

#===============================================================================
# specify constants and varaibles used by MISMIP experiment :
md.materials.rho_ice         = rhoi
md.materials.rho_water       = rhow
md.constants.g               = g
md.constants.yts             = spy
md.transient.isthermal       = 0.0
md.geometry.surface          = S
md.geometry.base             = B
md.geometry.thickness        = H
md.geometry.bed              = zb
md.mask.groundedice_levelset = ls
md.mask.groundedice_levelset = mask              # ice is grounded where == 1
md.mask.ice_levelset         = -1 * v_ones       # ice is present when negative
md.friction.coefficient      = beta * v_ones
#floating_v = numpy.where(md.mask.groundedice_levelset < 0)[0]
#md.friction.coefficient[floating_v] = 0
md.friction.p                =  p * e_ones
md.friction.q                =  q * e_ones
md.materials.rheology_B      = Bf * v_ones
md.materials.rheology_n      =  n * e_ones
#md.materials.rheology_B      = im.paterson((Tm - 20.0) * v_ones)
md.materials.rheology_law    = "None"

# create placeholders :
md.stressbalance.spcvx       = np.nan * v_ones
md.stressbalance.spcvy       = np.nan * v_ones
md.stressbalance.spcvz       = np.nan * v_ones

## upper side wall :
#pos_u  = np.where(md.mesh.y > np.max(md.mesh.y) - 0.1)[0]
#md.stressbalance.spcvy[pos_u] = 0.0
#md.stressbalance.spcvz[pos_u] = 0.0
#
## lower side wall :
#pos_l  = np.where(md.mesh.y < 0.1)[0]
#md.stressbalance.spcvy[pos_l] = 0.0
#md.stressbalance.spcvz[pos_l] = 0.0
#
## inflow boundary condition :
#pos2  = np.where(md.mesh.x < 0.1)[0]
#md.stressbalance.spcvx[pos2] = 0.0
#md.stressbalance.spcvy[pos2] = 0.0
#md.stressbalance.spcvz[pos2] = 0.0

## set no-slip basal velocity BC :
#basal_v                         = md.mesh.vertexonbase
#md.stressbalance.spcvx[basal_v] = 0.0
#md.stressbalance.spcvy[basal_v] = 0.0
#md.stressbalance.spcvz[basal_v] = 0.0

md.smb.mass_balance          = adot * v_ones
md.thermal.spctemperature    = np.nan * v_ones

md.groundingline.migration              = 'SoftMigration'
#md.groundingline.migration              = 'AggressiveMigration'
#md.groundingline.migration              = 'SubelementMigration2'
#md.groundingline.migration              = 'None'
md.masstransport.hydrostatic_adjustment = 'Incremental'

# initialization :
md.initialization.vx          = 0.0 * v_ones
md.initialization.vy          = 0.0 * v_ones
md.initialization.vz          = 0.0 * v_ones
md.initialization.vel         = 0.0 * v_ones
md.initialization.pressure    = rhoi * g * H
md.initialization.temperature = Tm * v_ones

# tansient settings :
md.transient.isgroundingline      = 1
md.transient.ismasstransport      = 1
md.transient.issmb                = 1
md.timestepping.time_adapt        = 0
md.timestepping.cfl_coefficient   = cfl
md.timestepping.time_step         = dt
md.timestepping.final_time        = tf
md.settings.output_frequency      = 1
md.balancethickness.stabilization = 0 # 2
md.masstransport.stabilization    = 1

md.transient.requested_outputs    = ['default',
                                     'GroundedArea',
                                     'FloatingArea',
                                     'IceVolume',
                                     'IceVolumeAboveFloatation']

#===============================================================================
print_text('::: issm -- set boundary conditions :::', 'red')

# Set the default boundary conditions for an ice-sheet :
md = im.SetMarineIceSheetBC(md)  # create placeholder arrays for indicies 
md.extrude(6, 1.0)
md = im.setflowequation(md, mdl_odr, 'all')
md.flowequation.fe_HO = 'P1bubble'

#===============================================================================
# solve :
print_text('::: issm -- solving :::', 'red')
    
md.cluster = im.generic('name', im.gethostname(), 'np', 4)
md.verbose = im.verbose('solution', True, 'control', True, 'convergence', True)
md         = im.solve(md, 'Transient')

#===============================================================================
# save the state of the model :
im.savevars(out_dir + 'mismip.md', 'md', md)



