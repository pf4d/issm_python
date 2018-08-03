try:
	import pylab as p
except ImportError:
	print "could not import pylab, matplotlib has not been installed, no plotting capabilities enabled"
import numpy as  np
from issm.processmesh import processmesh
from issm.applyoptions import applyoptions

def plot_icefront(md,options,fig,ax):
	#PLOT_ICEFRONT - plot segment on neumann BC
	#
	#   Usage:
	#      plot_icefront(md,options,width,i)
	#
	#   See also: PLOTMODEL
#process mesh and data
	x,y,z,elements,is2d,isplanet=processmesh(md,[],options)

	#icefront check
	icefront=np.where(np.abs(np.sum(md.mask.ice_levelset[elements],1))!=3) 
	onlyice=np.where(np.sum(md.mask.ice_levelset[elements],1)==-3)
	noice=np.where(np.sum(md.mask.ice_levelset[elements],1)==3)

	#plot mesh
	ax.triplot(x,y,elements)

	#highlight elements on neumann
	if len(icefront[0])>0:
		colors=np.asarray([0.5 for element in elements[icefront]])
		ax.tripcolor(x,y,elements[icefront],facecolors=colors,alpha=0.5,label='elements on ice front')

	#apply options
	options.addfielddefault('title','Neumann boundary conditions')
	options.addfielddefault('colorbar','off')
