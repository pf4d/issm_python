from fenics_viz      import *
from netCDF4         import Dataset
from copy            import copy
import issm              as im
import numpy             as np

mdl_odr   = 'HO'
dt        = 10
dx        = 2000
structure = 'unstructured'

if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr

var_dir = './dump/vars/' + mdl_pfx + '/'
out_dir = './dump/results/dx_%i/%s/gnd_line_eval/' % (dx, structure)
# create the output directory if it does not exist :
d       = os.path.dirname(out_dir)
if not os.path.exists(d):
	os.makedirs(d)

# load the data :
try:
	beta_a      = np.load(out_dir + 'beta.npy').tolist()
	time_a      = np.load(out_dir + 'time.npy').tolist()
	S_min_a     = np.load(out_dir + 'S_min.npy').tolist()
	S_max_a     = np.load(out_dir + 'S_max.npy').tolist()
	B_min_a     = np.load(out_dir + 'B_min.npy').tolist()
	B_max_a     = np.load(out_dir + 'B_max.npy').tolist()
	H_min_a     = np.load(out_dir + 'H_min.npy').tolist()
	H_max_a     = np.load(out_dir + 'H_max.npy').tolist()
	p_min_a     = np.load(out_dir + 'p_min.npy').tolist()
	p_max_a     = np.load(out_dir + 'p_max.npy').tolist()
	U_mag_min_a = np.load(out_dir + 'U_mag_min.npy').tolist()
	U_mag_max_a = np.load(out_dir + 'U_mag_max.npy').tolist()
	gnd_min_a   = np.load(out_dir + 'gnd_min.npy').tolist()
	gnd_max_a   = np.load(out_dir + 'gnd_max.npy').tolist()
except IOError:
	beta_a      = []
	time_a      = []
	S_min_a     = []
	S_max_a     = []
	B_min_a     = []
	B_max_a     = []
	H_min_a     = []
	H_max_a     = []
	p_min_a     = []
	p_max_a     = []
	U_mag_min_a = []
	U_mag_max_a = []
	gnd_min_a   = []
	gnd_max_a   = []

# friction directories to search :
beta_a_n = [20000]#range(16000, 20000, 1000)

for j in beta_a_n:
	# directories for saving data :
	name    = '%s_mismip_beta_%i' % (structure, j)
	print "extracting", name
	inp_dir = './dump/results/dx_%i/%s/%s/%s.outbin' % (dx,structure,name,name)

	# load the model mesh created by gen_nio_mesh.py :
	md    = im.loadmodel(var_dir + 'init_%s_mismip_dx_%i' % (structure,dx))

	# update the model with current output :
	try:
		md    = im.loadresultsfromdisk(md, inp_dir)
	except OSError:
		print "no outbin found for beta=%s" % j
		continue

	#=============================================================================
	# plot the results :

	# get number of timesteps :
	n      = len(md.results.TransientSolution)

	# get the upper and lower surface vertex indicies :
	vbed   = md.mesh.vertexonbase
	vsrf   = md.mesh.vertexonsurface

	time_a_i      = []
	S_min_a_i     = []
	S_max_a_i     = []
	B_min_a_i     = []
	B_max_a_i     = []
	H_min_a_i     = []
	H_max_a_i     = []
	p_min_a_i     = []
	p_max_a_i     = []
	U_mag_min_a_i = []
	U_mag_max_a_i = []
	gnd_min_a_i   = []
	gnd_max_a_i   = []

	# loop through all the timesteps and plot them :
	for i in range(0,n):

		# get this solution :
		soln_i = md.results.TransientSolution[i]

		# the `plot_variable` function requires the output data be row vectors :
		S       = soln_i.Surface[vbed].flatten()
		B       = soln_i.Base[vbed].flatten()
		H       = soln_i.Thickness[vbed].flatten()
		p       = soln_i.Pressure[vbed].flatten()
		U_mag   = soln_i.Vel[vbed].flatten()
		ls      = soln_i.MaskGroundediceLevelset[vbed].flatten()

		# calculate the grounded/floating mask :
		mask   = (ls > 0).astype('int')

		# the simulation time :
		time = i*dt

		# calculate the gournding line extents :
		gnd_max = md.mesh.x2d[mask == 1].max()
		gnd_min = md.mesh.x2d[mask == 0].min()

		time_a_i.append(time)
		S_min_a_i.append(S.min())
		S_max_a_i.append(S.max())
		B_min_a_i.append(B.min())
		B_max_a_i.append(B.max())
		H_min_a_i.append(H.min())
		H_max_a_i.append(H.max())
		p_min_a_i.append(p.min())
		p_max_a_i.append(p.max())
		U_mag_min_a_i.append(U_mag.min())
		U_mag_max_a_i.append(U_mag.max())
		gnd_min_a_i.append(gnd_min)
		gnd_max_a_i.append(gnd_max)

	beta_a.append(j)
	time_a.append(np.array(time_a_i))
	S_min_a.append(np.array(S_min_a_i))
	S_max_a.append(np.array(S_max_a_i))
	B_min_a.append(np.array(B_min_a_i))
	B_max_a.append(np.array(B_max_a_i))
	H_min_a.append(np.array(H_min_a_i))
	H_max_a.append(np.array(H_max_a_i))
	p_min_a.append(np.array(p_min_a_i))
	p_max_a.append(np.array(p_max_a_i))
	U_mag_min_a.append(np.array(U_mag_min_a_i))
	U_mag_max_a.append(np.array(U_mag_max_a_i))
	gnd_min_a.append(np.array(gnd_min_a_i))
	gnd_max_a.append(np.array(gnd_max_a_i))

beta_a      = np.array(beta_a)
time_a      = np.array(time_a)
S_min_a     = np.array(S_min_a)
S_max_a     = np.array(S_max_a)
B_min_a     = np.array(B_min_a)
B_max_a     = np.array(B_max_a)
H_min_a     = np.array(H_min_a)
H_max_a     = np.array(H_max_a)
p_min_a     = np.array(p_min_a)
p_max_a     = np.array(p_max_a)
U_mag_min_a = np.array(U_mag_min_a)
U_mag_max_a = np.array(U_mag_max_a)
gnd_min_a   = np.array(gnd_min_a)
gnd_max_a   = np.array(gnd_max_a)

np.save(out_dir + 'beta.npy',      beta_a)
np.save(out_dir + 'time.npy',      time_a)
np.save(out_dir + 'S_min.npy',     S_min_a)
np.save(out_dir + 'S_max.npy',     S_max_a)
np.save(out_dir + 'B_min.npy',     B_min_a)
np.save(out_dir + 'B_max.npy',     B_max_a)
np.save(out_dir + 'H_min.npy',     H_min_a)
np.save(out_dir + 'H_max.npy',     H_max_a)
np.save(out_dir + 'p_min.npy',     p_min_a)
np.save(out_dir + 'p_max.npy',     p_max_a)
np.save(out_dir + 'U_mag_min.npy', U_mag_min_a)
np.save(out_dir + 'U_mag_max.npy', U_mag_max_a)
np.save(out_dir + 'gnd_min.npy',   gnd_min_a)
np.save(out_dir + 'gnd_max.npy',   gnd_max_a)



