from cslvr       import *
from fenics_viz  import *
from time        import time

t0    = time()             # start the timer

a     = 0.5 * pi / 180     # surface slope in radians
L     = 80000.0            # width of domain (also 8000, 10000, 14000)

# create a genreic box mesh, we'll fit it to geometry below :
p1    = Point(0.0, 0.0, 0.0)          # origin
p2    = Point(L,   L,   1)            # x, y, z corner 
#mesh  = BoxMesh(p1, p2, 19, 19, 5)    # a box to fill the void 
mesh  = BoxMesh(p1, p2, 49, 49, 5)    # a box to fill the void 

# output directiories :
mdl_odr = 'BP'
out_dir = './results/cslvr/' + mdl_odr + '/'
plt_dir = './images/cslvr/' + mdl_odr + '/'

# we have a three-dimensional problem here, with periodic lateral boundaries :
model = D3Model(mesh, out_dir = out_dir, use_periodic = True)

# the ISMIP-HOM experiment A geometry :
surface = Expression('- x[0] * tan(a)', a=a,
                     element=model.Q.ufl_element())
bed     = Expression(  '- x[0] * tan(a) - 1000.0 + 500.0 * ' \
                     + ' sin(2*pi*x[0]/L) * sin(2*pi*x[1]/L)',
                     a=a, L=L, element=model.Q.ufl_element())

# mark the exterior facets and interior cells appropriately :
model.calculate_boundaries()

# deform the mesh to match our desired geometry :
model.deform_mesh_to_geometry(surface, bed)

# initialize all the pertinent variables :
model.init_beta(1e16)             # friction coefficient for no-slip bed
model.init_A(1e-16)               # isothermal flow-rate factor

# we can choose any of these to solve our 3D-momentum problem :
if mdl_odr == 'BP':
  mom = MomentumBP(model)
elif mdl_odr == 'BP_duk':
  mom = MomentumDukowiczBP(model)
elif mdl_odr == 'RS':
  mom = MomentumDukowiczStokesReduced(model)
elif mdl_odr == 'FS_duk':
  mom = MomentumDukowiczStokes(model)
elif mdl_odr == 'FS_stab':
  mom = MomentumNitscheStokes(model, stabilized=True)
elif mdl_odr == 'FS_th':
  mom = MomentumNitscheStokes(model, stabilized=False)
mom.solve_params['solver']['newton_solver']['relative_tolerance'] = 5e-15
mom.solve_params['solver']['newton_solver']['maximum_iterations'] = 60
mom.solve()

print_text("total time to compute: %g seconds" % (time() - t0), 'red', 1)

# let's investigate the velocity divergence :
divU = project(div(model.U3))

# the purpose for everything below this line is data visualization :
#===============================================================================

# save these files with a name that makes sense for use with paraview :
model.save_xdmf(model.p,  'p')
model.save_xdmf(model.U3, 'U')
model.save_xdmf(divU,     'divU')

# create the bed and surface meshes :
model.form_bed_mesh()
model.form_srf_mesh()

# create 2D models :
bedmodel = D2Model(model.bedmesh, out_dir)
srfmodel = D2Model(model.srfmesh, out_dir)

# we don't have a function for this included in the `model' instance, 
# so we have to make one ourselves :
divU_b   = Function(bedmodel.Q, name='divU')

# function allows Lagrange interpolation between different meshes :
bedmodel.assign_submesh_variable(divU_b, divU)
srfmodel.assign_submesh_variable(srfmodel.U3, model.U3)
srfmodel.init_U_mag(srfmodel.U3)  # calculates the velocity magnitude 
bedmodel.assign_submesh_variable(bedmodel.p,  model.p)

# save the mesh coordinates and data for interpolation with ISSM :
x     = srfmodel.mesh.coordinates()[:,0]
y     = srfmodel.mesh.coordinates()[:,1]
u,v,w = srfmodel.U3.split(True)
u     = u.compute_vertex_values(srfmodel.mesh)
v     = v.compute_vertex_values(srfmodel.mesh)
w     = w.compute_vertex_values(srfmodel.mesh)
p     = bedmodel.p.compute_vertex_values(bedmodel.mesh)
np.savetxt(out_dir + 'x.txt',     x)
np.savetxt(out_dir + 'y.txt',     y)
np.savetxt(out_dir + 'u_x.txt',   u)
np.savetxt(out_dir + 'u_y.txt',   v)
np.savetxt(out_dir + 'u_z.txt',   w)
np.savetxt(out_dir + 'p.txt',     p)
np.savetxt(out_dir + 'cells.txt', srfmodel.mesh.cells())

# figure out some nice-looking contour levels :
U_min  = srfmodel.U_mag.vector().min()
U_max  = srfmodel.U_mag.vector().max()
U_lvls = array([U_min, 10, 20, 30, 40, 50, 60, 70, 80, U_max])

p_min  = bedmodel.p.vector().min()
p_max  = bedmodel.p.vector().max()
#p_lvls = array([4e6, 5e6, 6e6, 7e6, 8e6, 9e6, 1e7, 1.1e7, 1.2e7, p_max])
p_lvls = array([4e6, 5e6, 6e6, 7e6, 8e6, p_max])

d_min  = divU_b.vector().min()
d_max  = divU_b.vector().max()
d_lvls = array([d_min, -5e-3, -2.5e-3, -1e-3, 
                1e-3, 2.5e-3, 5e-3, d_max])

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 1.0,
                 'color'          : 'k',
                 'alpha'          : 0.5}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : 'k',
                 'scale'          : None,
                 'alpha'          : 0.8,
                 'width'          : 0.005,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

# these functions allow the plotting of an arbitrary FEniCS function or 
# vector that reside on a two-dimensional mesh (hence the D2Model
# instantiations above.
plot_variable(u                   = srfmodel.U3,
              name                = 'U',
              coords              = None,
              cells               = None,
              direc               = plt_dir, 
              figsize             = (8,8),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = U_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = True,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = False,
              xlabel              = r'$x$',
              ylabel              = r'$y$',
              equal_axes          = True,
              title               = r'$\underline{u} |_S^{\mathrm{CSLVR}}$',
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',
              extend              = 'neither',
              ext                 = '.pdf',
              normalize_vec       = True,
              plot_quiver         = False,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')

plot_variable(u = bedmodel.p, name = 'p', direc = plt_dir,
              ext                 = '.pdf',
              title               = r'$p |_B$',
              levels              = p_lvls,
              cmap                = 'viridis',
              plot_tp             = True,
              show                = False,
              extend              = 'min',
              cb_format           = '%.1e')

plot_variable(u = divU_b, name = 'divU', direc = plt_dir,
              ext                 = '.pdf',
              title               = r'$\nabla \cdot \underline{u} |_B$',
              cmap                = 'RdGy',
              levels              = None,#d_lvls,
              plot_tp             = True,
              show                = False,
              extend              = 'neither',
              cb_format           = '%.1e')



