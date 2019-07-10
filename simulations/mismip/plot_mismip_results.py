import numpy             as np
import matplotlib.pyplot as plt
import matplotlib        as mpl

mpl.rcParams['font.family']          = 'serif'
mpl.rcParams['text.usetex']          = True
mpl.rcParams['text.latex.preamble']  = ['\usepackage[mathscr]{euscript}']

mdl_odr    = 'HO'
resolution = [8000, 4000, 2000]

# set the directories :
if mdl_odr == 'HO': mdl_pfx = 'BP'
else:               mdl_pfx = mdl_odr
var_dir = './dump/vars/' + mdl_pfx + '/'
plt_dir = './dump/images/' + mdl_pfx + '/'

cmap   = plt.get_cmap('inferno')
colors = [ cmap(x) for x in np.linspace(0, 0.8, len(resolution)) ]

gnd_fig = plt.figure(1)
u_fig   = plt.figure(2)

# iterate through the resolutions :
for dx,c in zip(resolution,colors):

	for s in ['structured', 'unstructured']:
		out_dir = './dump/results/dx_%i/%s/gnd_line_eval/' % (dx, s)

		# load the data :
		try:
			beta_a      = np.load(out_dir + 'beta.npy')
		except IOError:
			break
		time_a      = np.load(out_dir + 'time.npy')
		S_min_a     = np.load(out_dir + 'S_min.npy')
		S_max_a     = np.load(out_dir + 'S_max.npy')
		B_min_a     = np.load(out_dir + 'B_min.npy')
		B_max_a     = np.load(out_dir + 'B_max.npy')
		H_min_a     = np.load(out_dir + 'H_min.npy')
		H_max_a     = np.load(out_dir + 'H_max.npy')
		p_min_a     = np.load(out_dir + 'p_min.npy')
		p_max_a     = np.load(out_dir + 'p_max.npy')
		u_mag_min_a = np.load(out_dir + 'U_mag_min.npy')
		u_mag_max_a = np.load(out_dir + 'U_mag_max.npy')
		gnd_min_a   = np.load(out_dir + 'gnd_min.npy')
		gnd_max_a   = np.load(out_dir + 'gnd_max.npy')

		# get the grounding line equilibrium (non-equal time steps) :
		gnd_min_eq = []
		for gnd in gnd_min_a: gnd_min_eq.append(gnd[-1])
		gnd_min_eq = np.array(gnd_min_eq) / 1000 # convert to km

		# get the maximum velocity :
		u_max_eq = []
		for u_mag_max in u_mag_max_a: u_max_eq.append(u_mag_max[-1])
		u_max_eq = np.array(u_max_eq)

		# eliminate low-friction areas :
		if dx == 8000:
			friction_h = beta_a >= 2000
			friction_l = beta_a <= 5000
			friction   = np.logical_and(friction_h, friction_l)
			beta_a     = beta_a[friction]
			gnd_min_eq = gnd_min_eq[friction]
			u_max_eq   = u_max_eq[friction]

		# plot the history :
		if s == 'structured':
			ls = '.'
			label = r'$\Delta x = %i$ km' % (dx/1000)
		else:
			ls = '2'
			label = None
		plt.figure(1)
		plt.scatter(beta_a, gnd_min_eq, marker=ls, c=c, label=label)
		plt.figure(2)
		plt.scatter(beta_a, u_max_eq, marker=ls, c=c, label=label)

		# plot the run with grounding line closest to 450 km :
		#idx = np.argmin(np.abs(gnd_min_eq - 450))
		#plt.plot(beta_a[idx], gnd_min_eq[idx], 'o', c='r')

# make things fancy :
plt.figure(1)
plt.xlabel(r'friction coefficient $\beta$')
plt.ylabel(r'grounding line position (km)')
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig(plt_dir + 'friction_convergence.pdf')
plt.close()

plt.figure(2)
plt.xlabel(r'friction coefficient $\beta$')
plt.ylabel(r'maximum speed (m a$^{-1}$)')
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig(plt_dir + 'velocity_convergence.pdf')
plt.close()


