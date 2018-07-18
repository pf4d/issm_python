from netCDF4    import Dataset
from fenics_viz import *
import issm         as im
import numpy        as np
import os

# directories for saving data :
mdl_odr = 'HO'
#name    = 'zero_stress'
#name    = 'no_slip'
#name    = 'zero_velocity'
#name    = 'marine_bc'
#name    = 'marine_bc_dt_1_y'
#name    = 'marine_bc_subelement'
#name    = 'shelf_bc_subelement'
#name    = 'shelf_bc_subelement_slip'
name    = 'shelf_bc_subelement_slip_fric_1e3'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
plt_dir = './images/' + mdl_pfx + '/' + name + '/'
out_dir = './results/' + mdl_pfx + '/'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# ISMIP HOM A experiment :
md = im.model()
md.miscellaneous.name = name

#===============================================================================
print_text('::: issm -- initializing model :::', 'red')

# define the geometry of the simulation :
Lx     =  640000.0    # [m] domain length (along ice flow)
Ly     =  80000.0     # [m] domain width (across ice flow)
nx     =  64          # [--] number of x-coordinate divisions
ny     =  20          # [--] number of y-coordinate divisions
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
Hini   =  100.0       # [m] initial ice thickness
Tm     =  273.15      # [K] melting temperature of ice
n      =  3.0         # [--] Glen's exponent
A      =  2e-17       # [Pa^{-n} s^{-1}] flow 
beta   =  1e3         # [Pa m^{-1/n} a^{-1/n}] friction coefficient
p      =  1.0         # [--] Paterson friction exponent one
q      =  0.0         # [--] Paterson friction exponent two
adot   =  0.3         # [m a^{-a}] surface-mass balance
tf     =  2000.0      # [a] final time
dt     =  1.0         # [a] time step
dt_sav =  10.0        # [a] time interval to save data
cfl    =  0.5         # [--] CFL coefficient

# create an empty rectangular mesh :
#md     = triangle(md, './exp/MismipDomain.exp', 10000)
md     = im.squaremesh(md, Lx, Ly, nx=nx, ny=ny)
md     = im.setmask(md, 'all', '')

# set up element-wise multiplicative identities :

# rank-zero tensor vertex ones vector :
v_ones = np.ones(md.mesh.numberofvertices)

# rank-zero tensor element ones vector :
e_ones = np.ones(md.mesh.numberofelements)

# rank-two tensor ones vector :
A_ones = np.ones((md.mesh.numberofvertices, 6))

# rank-one tensor ones vector :
b_ones = np.ones((md.mesh.numberofvertices, 3))

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
print_text('::: issm -- set boundary conditions :::', 'red')

md.materials.rho_ice         = rhoi
md.materials.rho_water       = rhow
md.constants.g               = g
md.constants.yts             = spy
md.transient.isthermal       = 0.0
md.geometry.surface          = S
md.geometry.base             = B
md.geometry.thickness        = H
md.geometry.bed              = zb
md.mask.groundedice_levelset = mask              # ice is grounded where == 1
md.mask.ice_levelset         = -1 * v_ones       # ice is present when negative

md.friction.coefficient      = beta * v_ones
floating_v = np.where(md.mask.groundedice_levelset < 0)[0]
md.friction.coefficient[floating_v] = 0
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

md.basalforcings.groundedice_melting_rate = 0.0 * v_ones
md.basalforcings.floatingice_melting_rate = 0.0 * v_ones
md.stressbalance.referential              = np.nan * A_ones
md.stressbalance.loadingforce             = np.nan * b_ones

# Set the default boundary conditions for an ice-sheet :
md = im.SetMarineIceSheetBC(md)
#md = im.SetIceShelfBC(md)

## upper side wall :
#pos_u  = np.where(md.mesh.y > np.max(md.mesh.y) - 0.1)[0]
#md.stressbalance.spcvx[pos_u] = 0.0
#md.stressbalance.spcvy[pos_u] = 0.0
#md.stressbalance.spcvz[pos_u] = 0.0
#
## lower side wall :
#pos_l  = np.where(md.mesh.y < 0.1)[0]
#md.stressbalance.spcvx[pos_l] = 0.0
#md.stressbalance.spcvy[pos_l] = 0.0
#md.stressbalance.spcvz[pos_l] = 0.0
#
## inflow boundary condition :
#pos2  = np.where(md.mesh.x < 0.1)[0]
#md.stressbalance.spcvx[pos2] = 0.0
#md.stressbalance.spcvy[pos2] = 0.0
#md.stressbalance.spcvz[pos2] = 0.0

md.smb.mass_balance          = adot * v_ones
md.thermal.spctemperature    = np.nan * v_ones

#md.groundingline.migration              = 'SoftMigration'
md.groundingline.migration              = 'SubelementMigration'
#md.groundingline.migration              = 'SubelementMigration2'
#md.groundingline.migration              = 'AggressiveMigration'
#md.groundingline.migration              = 'None'
md.masstransport.hydrostatic_adjustment = 'Incremental'
md.masstransport.spcthickness           = np.nan * v_ones

# initialization :
md.initialization.vx          = 0.0 * v_ones
md.initialization.vy          = 0.0 * v_ones
md.initialization.vz          = 0.0 * v_ones
md.initialization.vel         = 0.0 * v_ones
md.initialization.pressure    = rhoi * g * H
md.initialization.temperature = Tm * v_ones

# tansient settings :
md.transient.isstressbalance      = 1
md.transient.isgroundingline      = 1
md.transient.ismasstransport      = 1
md.transient.issmb                = 1
md.timestepping.time_adapt        = 0
md.timestepping.cfl_coefficient   = cfl
md.timestepping.time_step         = dt
md.timestepping.final_time        = tf
md.settings.output_frequency      = int(dt_sav/dt)
md.balancethickness.stabilization = 0 # 2
md.masstransport.stabilization    = 1

md.transient.requested_outputs    = ['default',
                                     'GroundedArea',
                                     'FloatingArea',
                                     'IceVolume',
                                     'IceVolumeAboveFloatation']

# now, extrude and set the basal boundary conditions :
md.extrude(6, 1.0)

# specifiy the flow equation and FE basis :
md = im.setflowequation(md, mdl_odr, 'all')
md.flowequation.fe_HO = 'P1'

# set no-slip basal velocity BC :
# FIXME: if you do not call ``md.extrude()`` before, ``md.mesh.vertexonbase``
#        does not exist.
#basal_v                         = md.mesh.vertexonbase
#md.stressbalance.spcvx[basal_v] = 0.0
#md.stressbalance.spcvy[basal_v] = 0.0
#md.stressbalance.spcvz[basal_v] = 0.0


#===============================================================================
# save the state of the model :
#im.savevars(out_dir + 'mismip_init.md', 'md', md)

#===============================================================================
# solve :
print_text('::: issm -- solving :::', 'red')
    
md.cluster = im.generic('name', im.gethostname(), 'np', 2)
md.verbose = im.verbose('solution', True, 'control', True, 'convergence', True)
md         = im.solve(md, 'Transient')

#===============================================================================
# save the state of the model :
im.savevars(out_dir + name + '.md', 'md', md)



