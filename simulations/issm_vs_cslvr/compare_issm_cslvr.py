import numpy               as np
from fenics_viz        import plot_variable
from scipy.interpolate import RectBivariateSpline, interp2d

def get_index_map(coord_to, coord_from, tol=1e-2): 
  idx = []
  for c in coord_from:
    xm = np.where(np.abs(coord_to[:,0] - c[0]) < tol)[0]
    ym = np.where(np.abs(coord_to[:,1] - c[1]) < tol)[0]
    idx.append(np.intersect1d(xm, ym)[0]) 
  return np.array(idx)

# momentum approximation data directories :
mdl_odr = 'BP'
plt_dir = './images/compare/'  + mdl_odr + '/'
issm_dir  = './results/issm/'  + mdl_odr + '/'
cslvr_dir = './results/cslvr/' + mdl_odr + '/'

# ISSM :
issm_x = np.loadtxt(issm_dir + 'x.txt')
issm_y = np.loadtxt(issm_dir + 'y.txt')
issm_u = np.loadtxt(issm_dir + 'u_x.txt')
issm_v = np.loadtxt(issm_dir + 'u_y.txt')
issm_w = np.loadtxt(issm_dir + 'u_z.txt')
issm_p = np.loadtxt(issm_dir + 'p.txt')

# CSLVR :
cslvr_x = np.loadtxt(cslvr_dir + 'x.txt')
cslvr_y = np.loadtxt(cslvr_dir + 'y.txt')
cslvr_u = np.loadtxt(cslvr_dir + 'u_x.txt')
cslvr_v = np.loadtxt(cslvr_dir + 'u_y.txt')
cslvr_w = np.loadtxt(cslvr_dir + 'u_z.txt')
cslvr_p = np.loadtxt(cslvr_dir + 'p.txt')
cells   = np.loadtxt(cslvr_dir + 'cells.txt')

# NOTE: interpolation is not required because the grids match.
# use the cslvr grid as basis, so form issm interpolation :
#f_w = interp2d(issm_x, issm_y, issm_w, kind='linear')
#issm_w_n = []
#for x,y in zip(cslvr_x, cslvr_y):
#  issm_w_n.append(f_w(x,y)[0])
#issm_u_n = np.array(issm_u_n)

# find map between nodal indicies :
issm_coords  = np.array([issm_x,  issm_y]).T
cslvr_coords = np.array([cslvr_x, cslvr_y]).T
idx          = get_index_map(issm_coords, cslvr_coords) 

# convert :
issm_u = issm_u[idx]
issm_v = issm_v[idx]
issm_w = issm_w[idx]
issm_p = issm_p[idx]

# calculate the difference :
issm_U_mag  = np.sqrt(issm_u**2 + issm_v**2)# + issm_w**2 + 1e-16)
cslvr_U_mag = np.sqrt(cslvr_u**2 + cslvr_v**2)# + cslvr_w**2 + 1e-16)
issm_U      = np.array([issm_u, issm_v])#, issm_w])
cslvr_U     = np.array([cslvr_u,  cslvr_v])#,  cslvr_w])
diff        = issm_U - cslvr_U

tp_kwargs     = {'linestyle'      : '-',
                 'lw'             : 1.0,
                 'color'          : 'k',
                 'alpha'          : 0.5}

quiver_kwargs = {'pivot'          : 'middle',
                 'color'          : 'k',
                 'scale'          : None,
                 'alpha'          : 0.8,
                 'width'          : 0.003,
                 'headwidth'      : 3.0, 
                 'headlength'     : 3.0, 
                 'headaxislength' : 3.0}

d_tit = r'$\underline{u}_{\Vert} |_S^{\mathrm{ISSM}} ' \
        + '- \underline{u}_{\Vert} |_S^{\mathrm{CSLVR}}$'

plot_variable(u                   = diff,
              name                = 'd',
              direc               = plt_dir, 
              coords              = (cslvr_x, cslvr_y),
              cells               = cells,
              figsize             = (8,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = False,
              xlabel              = r'$x$',
              ylabel              = r'$y$',
              equal_axes          = True,
              title               = d_tit,
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',
              extend              = 'neither',
              ext                 = '.pdf',
              normalize_vec       = False,
              plot_quiver         = True,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')

d_w_tit  = r'$w |_S^{\mathrm{ISSM}} - w |_S^{\mathrm{CSLVR}}$'
d_w      = issm_w - cslvr_w
d_w_lvls = np.array([d_w.min(), -0.08, -0.04, -0.02, -0.002,
                                 0.002, 0.02, 0.04, 0.08, d_w.max()])

plot_variable(u                   = d_w,
              name                = 'd_w',
              direc               = plt_dir, 
              coords              = (cslvr_x, cslvr_y),
              cells               = cells,
              figsize             = (8,7),
              cmap                = 'RdGy',
              scale               = 'lin',
              numLvls             = 10,
              levels              = d_w_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = False,
              xlabel              = r'$x$',
              ylabel              = r'$y$',
              equal_axes          = True,
              title               = d_w_tit,
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',#'lines',
              extend              = 'neither',
              ext                 = '.pdf',
              normalize_vec       = False,
              plot_quiver         = True,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')

d_p_tit  = r'$p |_B^{\mathrm{ISSM}} - p |_B^{\mathrm{CSLVR}}$'
d_p      = issm_p - cslvr_p
d_p_lvls = np.array([d_p.min(), d_p.max()])

plot_variable(u                   = d_p,
              name                = 'd_p',
              direc               = plt_dir, 
              coords              = (cslvr_x, cslvr_y),
              cells               = cells,
              figsize             = (8,7),
              cmap                = 'viridis',
              scale               = 'lin',
              numLvls             = 10,
              levels              = None,#d_p_lvls,
              levels_2            = None,
              umin                = None,
              umax                = None,
              plot_tp             = False,
              tp_kwargs           = tp_kwargs,
              show                = False,
              hide_x_tick_labels  = False,
              hide_y_tick_labels  = False,
              xlabel              = r'$x$',
              ylabel              = r'$y$',
              equal_axes          = True,
              title               = d_p_tit,
              hide_axis           = False,
              colorbar_loc        = 'right',
              contour_type        = 'filled',#'lines',
              extend              = 'neither',
              ext                 = '.pdf',
              normalize_vec       = False,
              plot_quiver         = True,
              quiver_kwargs       = quiver_kwargs,
              res                 = 150,
              cb                  = True,
              cb_format           = '%g')


