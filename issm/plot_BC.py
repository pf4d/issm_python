try:
	import pylab as p
except ImportError:
	print "could not import pylab, matplotlib has not been installed, no plotting capabilities enabled"

import numpy as  np
from issm.processmesh import processmesh
from issm.applyoptions import applyoptions
from issm.plot_icefront import plot_icefront
from mpl_toolkits.mplot3d import Axes3D

def plot_BC(md,options,fig,axgrid,gridindex):
	'''
	PLOT_BC - plot model boundary conditions

		Usage:
			plot_BC(md,options,fig,axes)

		See also: PLOTMODEL
	'''
	x,y,z,elements,is2d,isplanet=processmesh(md,[],options)
	
	ax=axgrid[gridindex]
	fig.delaxes(axgrid.cbar_axes[gridindex])

	if not is2d:
		ax=inset_locator.inset_axes(axgrid[gridindex],width='100%',height='100%',loc=3,borderpad=0,axes_class=Axes3D)

	#plot neuman
	plot_icefront(md,options,fig,ax)

	XLims=[np.min(x),np.max(x)]
	YLims=[np.min(y),np.max(y)]
	#plot dirichlets
	dirichleton=options.getfieldvalue('dirichlet','on')
	if dirichleton=='on':
		ax.scatter(x[np.where(~np.isnan(md.stressbalance.spcvx))],
							 y[np.where(~np.isnan(md.stressbalance.spcvx))],
							 marker='o',c='r',s=240,label='vx Dirichlet',linewidth=0)
		ax.scatter(x[np.where(~np.isnan(md.stressbalance.spcvy))],
							 y[np.where(~np.isnan(md.stressbalance.spcvy))],
							 marker='o',c='b',s=160,label='vy Dirichlet',linewidth=0)
		ax.scatter(x[np.where(~np.isnan(md.stressbalance.spcvz))],
							 y[np.where(~np.isnan(md.stressbalance.spcvz))],
							 marker='o',c='y',s=80,label='vz Dirichlet',linewidth=0)
		try:
			ax.scatter(x[np.where(~np.isnan(md.hydrology.spcepl_head))],
								 y[np.where(~np.isnan(md.hydrology.spcepl_head))],
								 marker='v',c='r',s=240,label='EPL Head',linewidth=0)
			ax.scatter(x[np.where(~np.isnan(md.hydrology.spcsediment_head))],
								 y[np.where(~np.isnan(md.hydrology.spcsediment_head))],
								 marker='^',c='b',s=240,label='IDS head',linewidth=0)
		except AttributeError:
			print ('Not treating Hydrologydc, skipping these boundaries')
		ax.set_xlim(XLims)
		ax.set_ylim(YLims)
	ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
						ncol=3, mode="expand", borderaxespad=0.)
	#apply options
	options.addfielddefault('title','Boundary conditions')
	options.addfielddefault('colorbar','off')
	applyoptions(md,[],options,fig,axgrid,gridindex)
	
