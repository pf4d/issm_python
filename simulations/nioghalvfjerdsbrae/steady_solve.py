from fenics_viz      import *
import issm              as im
import cslvr             as cs
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.tri    as tri
import os, sys

# directories for saving data :
mdl_odr = 'HO'
tmc     = True

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
var_dir = './dump/vars/'
plt_dir = './dump/images/' + mdl_pfx + '/'
out_dir = './dump/results/' + mdl_pfx + '/'
vtu_dir = plt_dir + 'vtu/'

# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
  os.makedirs(d)

# create the output directory if it does not exist :
d       = os.path.dirname(vtu_dir)
if not os.path.exists(d):
  os.makedirs(d)

# load the model mesh created by gen_nio_mesh.py :
md                    = im.model()
md.miscellaneous.name = 'Nioghalvfjerdsbrae'

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
rhow   =  1028.0      # [kg m^-3] density of seawater
rhoi   =  910.0       # [kg m^-3] density of glacier ice
g      =  9.81        # [m s^2] gravitational acceleration
spy    =  31556926.0  # [s a^-1] seconds per year
Hini   =  100.0       # [m] initial ice thickness
Tm     =  273.15      # [K] melting temperature of ice
n      =  3.0         # [--] Glen's exponent
A      =  1e-16       # [Pa^{-n} s^{-1}] flow 
p      =  1.0         # [--] Paterson friction exponent one
q      =  0.0         # [--] Paterson friction exponent two
adot   =  0.3         # [m a^{-a}] surface-mass balance
tf     =  2.0         # [a] final time
dt     =  1.0         # [a] time step
dt_sav =  10.0        # [a] time interval to save data
cfl    =  0.5         # [--] CFL coefficient
q_geo  =  0.0#0.042   # [W m^-2] geothermal heat flux
a_T_l  =  3.985e-13   # [s^-1 Pa^-3] lower bound of flow-rate constant
a_T_u  =  1.916e3     # [s^-1 Pa^-3] upper bound of flow-rate constant
Q_T_l  =  6e4         # [J mol^-1] lower bound of creep activation energy
Q_T_u  =  13.9e4      # [J mol^-1] upper bound of creep activation energy
R      =  8.3144621   # [J mol^-1] universal gas constant
num_p  =  2           # [--] number of processors to use

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
# ISMIP_HOM experiment :
md.materials.rho_ice         = rhoi
md.materials.rho_water       = rhow
md.constants.g               = g
md.constants.yts             = spy

md.friction.p                = p * e_ones
md.friction.q                = q * e_ones

md.materials.rheology_n      =  n * e_ones
md.materials.rheology_B      = Bf
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
#md.initialization.pressure   = 0.0 * v_ones

# boundary conditions :
md.basalforcings.groundedice_melting_rate = 0.0 * v_ones
md.basalforcings.floatingice_melting_rate = 0.0 * v_ones
md.basalforcings.geothermalflux           = q_geo * v_ones

# thermal model :
#md.initialization.temperature = Tm * v_ones
md.initialization.waterfraction           = 0.0 * v_ones
md.initialization.watercolumn             = 0.0 * v_ones
md.thermal.spctemperature                 = md.initialization.temperature.copy()
md.thermal.stabilization                  = 2 # SUPG
md.thermal.isenthalpy                     = 1

# FIXME: ``SteadyState`` throws an error if this is not zero :
md.timestepping.time_step                 = 0.0

#===============================================================================
# boundary conditions :
print_text('::: issm -- set boundary conditions :::', 'red')

# set the default boundary conditions for an ice-sheet :
md = im.SetMarineIceSheetBC(md)  # create placeholder arrays for indicies 

md.stressbalance.spcvx      = np.nan * v_ones
md.stressbalance.spcvy      = np.nan * v_ones
md.stressbalance.spcvz      = np.nan * v_ones

# extrude the mesh so that there are 5 cells in height :
md.extrude(20, 1.0)

# set the flow equation of type `mdl_odr` defined above :
md = im.setflowequation(md, mdl_odr, 'all')
md.flowequation.fe_HO = 'P1'


#===============================================================================
# solve :
print_text('::: issm -- solving :::', 'red')

md.cluster = im.generic('name', im.gethostname(), 'np', num_p)
md.verbose = im.verbose('convergence', True)
if tmc: md = im.solve(md, 'SteadyState')
else:   md = im.solve(md, 'StressBalance')

#md = im.solve(md, 'StressBalance')

#md.initialization.vx       = md.results.StressbalanceSolution.Vx
#md.initialization.vy       = md.results.StressbalanceSolution.Vy
#md.initialization.vz       = md.results.StressbalanceSolution.Vz
#md.initialization.vel      = md.results.StressbalanceSolution.Vel
#md.initialization.pressure = md.results.StressbalanceSolution.Pressure

#md.initialization.vx       = md.inversion.vx_obs
#md.initialization.vy       = md.inversion.vy_obs
#md.initialization.vz       = 0.0 * md.results.StressbalanceSolution.Vz
#md.initialization.vel      = md.inversion.vel_obs
#md.initialization.pressure = md.results.StressbalanceSolution.Pressure

#md = im.solve(md, 'Thermal')

#===============================================================================
# save .vtu files :
p      = md.results.StressbalanceSolution.Pressure.flatten()
u_x    = md.results.StressbalanceSolution.Vx.flatten()
u_y    = md.results.StressbalanceSolution.Vy.flatten()
u_z    = md.results.StressbalanceSolution.Vz.flatten()
T      = md.results.ThermalSolution.Temperature.flatten()

u      = [u_x, u_y, u_z]

im.vtuwrite(u, 'u', md, vtu_dir + 'u.vtu')
im.vtuwrite(p, 'p', md, vtu_dir + 'p.vtu')
im.vtuwrite(T, 'T', md, vtu_dir + 'T.vtu')

#===============================================================================
# plot the results :
print_text('::: issm -- plotting :::', 'red')

p_b   = p[md.mesh.vertexonbase]
u_x_s = u_x[md.mesh.vertexonsurface]
u_y_s = u_y[md.mesh.vertexonsurface] 
u_z_s = u_z[md.mesh.vertexonsurface] 
u_s   = np.array([u_x_s, u_y_s, u_z_s])
T_b   = T[md.mesh.vertexonbase]

# save the mesh coordinates and data for interpolation with CSLVR :
np.savetxt(out_dir + 'x.txt',   md.mesh.x2d)
np.savetxt(out_dir + 'y.txt',   md.mesh.y2d)
np.savetxt(out_dir + 'u_x.txt', u[0])
np.savetxt(out_dir + 'u_y.txt', u[1])
np.savetxt(out_dir + 'u_z.txt', u[2])
np.savetxt(out_dir + 'p.txt',   p)

u_mag     = np.sqrt(u_x_s**2 + u_y_s**2 + u_z_s**2 + 1e-16)
U_lvls    = np.array([u_mag.min(), 1e0, 5e0, 1e1, 5e1, 1e2, 5e2, 1e3,
                      u_mag.max()])
T_lvls    = np.array([T_b.min(), 260.0, 265.0, 270.0, 271.0, 272.0, T_b.max()])

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 1.0,
                 'color'          : 'k',
                 'alpha'          : 0.5}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : 'k',
                 'scale'          : 100,
                 'alpha'          : 0.5,
                 'width'          : 0.001,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

# the plot parameters will mostly stay the same for each plot :
plot_kwargs = {'direc'              : plt_dir, 
               'coords'             : (md.mesh.x2d, md.mesh.y2d),
               'cells'              : md.mesh.elements2d - 1,
               'figsize'            : (5,7.5),
               'cmap'               : 'viridis',
               'scale'              : 'lin',
               'numLvls'            : 10,
               'levels'             : None,
               'levels_2'           : None,
               'umin'               : None,
               'umax'               : None,
               'plot_tp'            : False,
               'tp_kwargs'          : tp_kwargs,
               'show'               : False,
               'hide_x_tick_labels' : True,
               'hide_y_tick_labels' : True,
               'xlabel'             : '',
               'ylabel'             : '',
               'equal_axes'         : True,
               'hide_axis'          : True,
               'colorbar_loc'       : 'right',
               'contour_type'       : 'filled',
               'extend'             : 'neither',
               'ext'                : '.pdf',
               'normalize_vec'      : True,
               'plot_quiver'        : False,
               'quiver_skip'        : 0,
               'quiver_kwargs'      : quiver_kwargs,
               'res'                : 150,
               'cb'                 : True,
               'cb_format'          : '%g'}

plot_kwargs['u']      = u_s
plot_kwargs['scale']  = 'lin'
plot_kwargs['name']   = 'U_S'
plot_kwargs['levels'] = U_lvls
plot_kwargs['title']  = r'$\underline{u} |_S^{\mathrm{ISSM}}$'
plot_variable(**plot_kwargs)

plot_kwargs['u']      = T_b
plot_kwargs['scale']  = 'lin'
plot_kwargs['name']   = 'T_B'
plot_kwargs['levels'] = T_lvls
plot_kwargs['title']  = r'$T |_B^{\mathrm{ISSM}}$'
plot_variable(**plot_kwargs)



