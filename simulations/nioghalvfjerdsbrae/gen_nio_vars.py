import issm       as im
import cslvr      as cs
import numpy      as np
import os

mdl_odr   = 'HO'
name      = 'negis'
mesh_name = 'nioghalvfjerdsbrae'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr

#===============================================================================
# data preparation :
var_dir   = './dump/vars/' + mdl_pfx + '/'
msh_dir   = './dump/meshes/' + mdl_pfx + '/'

# create the output directory if it does not exist :
d       = os.path.dirname(var_dir)
if not os.path.exists(d):
  os.makedirs(d)

# create the output directory if it does not exist :
d       = os.path.dirname(msh_dir)
if not os.path.exists(d):
  os.makedirs(d)

# only a few constants needed :
rhoi = 910.0
rhow = 1028.0
g    = 9.81

#===============================================================================
# use issm to create mesh for 79 N Glacier :
cs.print_text('::: issm -- constructing mesh :::', 'red')

# instantiate a generic model instance :
md                    = im.model()
md.miscellaneous.name = name

# collect the raw data :
searise  = cs.DataFactory.get_searise()
bedmach  = cs.DataFactory.get_bedmachine(thklim=1.0)
mouginot = cs.DataFactory.get_mouginot()

# create data objects to use with cslvr :
dsr      = cs.DataInput(searise)
dbm      = cs.DataInput(bedmach)
dmg      = cs.DataInput(mouginot)

# change the searise projection to that of the other data :
dsr.change_projection(dbm)

#===============================================================================
# generate the contour :
# FIXME: the issm interpolation will result in areas with the surface ~1 km 
#        below sea level on a few nodes next to the ocean.  Thus:
dbm.data['S'][dbm.data['S'] < 1.0] = 1.0

# generate the contour :
m = cs.MeshGenerator(dbm, mesh_name, msh_dir)

#m.create_contour('mask', zero_cntr=0.5, skip_pts=2)
m.create_contour('H', zero_cntr=15, skip_pts=1)  # 50 meter thick. contour
m.eliminate_intersections(dist=10)               # eliminate interscting lines

# get the basin :
gb = cs.GetBasin(dbm, basin='2.1')               # NEGIS basin
gb.remove_skip_points(400)                       # make it crude
gb.extend_edge(10000)                            # extend the border
gb.intersection(m.longest_cont)                  # take the intersection
#gb.plot_xycoords(other=m.longest_cont)          # plot the result
m.set_contour(gb.get_xy_contour())               # replace the full contour

# process the file and extrude :
m.eliminate_intersections(dist=200)              # eliminate interscting lines
m.check_dist()                                   # remove points too close
m.write_argus_contour()                          # create a .exp contour file
m.close_file()                                   # close the files


#===============================================================================
# generate the mesh :
cs.print_text('::: issm -- generating mesh :::', 'red')

dbm.interpolate_from_di(dmg, 'vx',   'vx',     order=1)
dbm.interpolate_from_di(dmg, 'vy',   'vy',     order=1)
dbm.interpolate_from_di(dmg, 'mask', 'U_mask', order=1)

# define the geometry of the simulation :
#md     = im.triangle(md, msh_dir + mesh_name + '.exp', 50000)
md    = im.bamg(md,
                'domain', msh_dir + mesh_name + '.exp',
                'hmax',   500)

# change data type to that required by InterpFromGridToMesh() :
x1    = dbm.x.astype('float64')
y1    = dbm.y.astype('float64')
velx  = dbm.data['vx'].astype('float64')
vely  = dbm.data['vy'].astype('float64')

# get the gradient of the mask :
mask      = dbm.data['mask'].copy()
mask[mask < 2.0] = 0.0
gradm     = np.gradient(mask)
lat_mask  = gradm[0]**2 + gradm[1]**2
lat_mask  = lat_mask > 0.0

# calculate the velocity magnitude :
vel   = np.sqrt(velx**2 + vely**2)

# increase the velocity at the grounding line or ice/ocean interface :
vel[lat_mask] = 1000000.0

# interpolate the data onto the issm mesh :
u_mag = im.InterpFromGridToMesh(x1, y1, vel, md.mesh.x, md.mesh.y, 0)[0]

# interpolate the thickness data onto the issm mesh :
#H     = im.InterpFromGridToMesh(x1, y1, dbm.data['H'],
#                                md.mesh.x, md.mesh.y, 0)[0]
#               'field',        np.vstack([u_mag, H]).T,
#               'err',          np.array([[8,8]]))

# refine mesh using surface velocities as metric :
md    = im.bamg(md,
                'hmax',         10000,
                'hmin',         100,
                'gradation',    1,
                'KeepVertices', 0,
                'tol',          100,
                'field',        u_mag,
                'err',          6)

# rank-zero tensor vertex ones vector :
v_ones = np.ones(md.mesh.numberofvertices)

#===============================================================================
# set grounded/floating ice mask :
cs.print_text('::: issm -- generating input data :::', 'red')

# determine floatation from density :
S    = dbm.data['S']
B    = dbm.data['B']
mask = dbm.data['mask']
gnd  = rhoi * (S - B) > rhow * B

# get the mask and set interior ice-free regions to grounded :
interior = np.logical_and(mask == 1, gnd)
mask[interior]  =  1

# issm specifies floating ice as -1 :
mask[mask == 0] =  1
mask[mask == 2] = -1

# interpolate the mask onto the grid :
mask = im.InterpFromGridToMesh(dbm.x, dbm.y, mask,
                               md.mesh.x, md.mesh.y, 0)[0]

# convert to integer :
mask[mask > 0] =  1
mask[mask < 0] = -1
mask           = mask.astype('int')

# ice is grounded for mask equal one
md.mask.groundedice_levelset = mask

# ice is present when negative :
md.mask.ice_levelset  = -1 * np.ones(md.mesh.numberofvertices)

# get an expression which we can evaluate per coordinate of the mesh :
T_e  = dsr.get_expression('T')
T    = 0.0 * v_ones
for i, (x_i, y_i) in enumerate(zip(md.mesh.x, md.mesh.y)):
  T[i] = T_e(x_i, y_i)

# interpolate the data onto the refined mesh :
S    = im.InterpFromGridToMesh(dbm.x, dbm.y, dbm.data['S'],
                               md.mesh.x, md.mesh.y, 0)[0]
B    = im.InterpFromGridToMesh(dbm.x, dbm.y, dbm.data['B'],
                               md.mesh.x, md.mesh.y, 0)[0]

# FIXME: the issm interpolation will result in areas with the surface ~1 km 
#        below sea level on a few nodes next to the ocean.  Thus:
S[S < 1.0] = 1.0
S    = S.astype('float64')    # upper surface
B    = B.astype('float64')    # lower surface
H    = S - B                  # thickness

# surface velocity observations :
# NOTE: the issm::InterpFromGridToMesh method needs type ``float64`` :
x1    = dmg.x.astype('float64')
y1    = dmg.y.astype('float64')
velx  = dmg.data['vx'].astype('float64')
vely  = dmg.data['vy'].astype('float64')
vel   = np.sqrt(velx**2 + vely**2 + 1e-16)

# interpolate the velocities onto the mesh for data assimilation :
u_x     = im.InterpFromGridToMesh(x1, y1, velx, md.mesh.x, md.mesh.y, 0)[0]
u_y     = im.InterpFromGridToMesh(x1, y1, vely, md.mesh.x, md.mesh.y, 0)[0]
u_mag   = im.InterpFromGridToMesh(x1, y1, vel,  md.mesh.x, md.mesh.y, 0)[0]

# calculate initial friction based on the SIA :
U_mask             = dbm.data['U_mask']
U_mask[U_mask > 0] = 1

# calculate surface gradient magnitude :
grad_S    = np.gradient(dbm.data['S'], dbm.dx)
gS_mag    = np.sqrt(grad_S[0]**2 + grad_S[1]**2 + 1e-16)

# calculate surface velocity magnitude and impose minimum velocity :
u_mag_c   = np.sqrt(dbm.data['vx']**2 + dbm.data['vy']**2 + 1e-16)
u_0       = 1e-2
u_mag_c[u_mag_c < u_0] = u_0
u_mag_c[U_mask == 0]   = 1e4

# calculate initial friction based on the SIA :
beta_sia  = rhoi * g * dbm.data['H'] * gS_mag / u_mag_c
beta_sia  = im.InterpFromGridToMesh(dbm.x, dbm.y, beta_sia,
                                    md.mesh.x, md.mesh.y, 0)[0]

# set the issm model variables :
md.geometry.surface           = S
md.geometry.base              = B
md.geometry.thickness         = H
md.inversion.vx_obs           = u_x
md.inversion.vy_obs           = u_y
md.inversion.vel_obs          = u_mag
md.friction.coefficient       = beta_sia
md.initialization.temperature = T

#===============================================================================
# save the state of the model :
cs.print_text('::: issm -- saving the initialization :::', 'red')

var_dict  = {'md.mesh'                       : md.mesh,
             'md.mask.groundedice_levelset'  : md.mask.groundedice_levelset,
             'md.mask.ice_levelset'          : md.mask.ice_levelset,
             'md.initialization.temperature' : md.initialization.temperature,
             'md.geometry.surface'           : md.geometry.surface,
             'md.geometry.base'              : md.geometry.base,
             'md.geometry.thickness'         : md.geometry.thickness,
             'md.inversion.vx_obs'           : md.inversion.vx_obs,
             'md.inversion.vy_obs'           : md.inversion.vy_obs,
             'md.inversion.vel_obs'          : md.inversion.vel_obs,
             'md.friction_coefficient'       : md.friction.coefficient}
im.savevars(var_dir + 'issm_nio.shelve', var_dict)



