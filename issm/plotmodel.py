import numpy as  np
from issm.plotoptions import plotoptions
from issm.plotdoc import plotdoc
from issm.plot_manager import plot_manager
from math import ceil, sqrt

try:
	import pylab as p
	import matplotlib.pyplot as plt
	from mpl_toolkits.axes_grid1 import ImageGrid, AxesGrid
	from mpl_toolkits.mplot3d import Axes3D
except ImportError:
	print "could not import pylab, matplotlib has not been installed, no plotting capabilities enabled"

def plotmodel(md,*args):
	'''	at command prompt, type 'plotdoc()' for additional documentation
	'''

	#First process options
	options=plotoptions(*args)

	#get number of subplots
	subplotwidth=ceil(sqrt(options.numberofplots))
	#Get figure number and number of plots
	figurenumber=options.figurenumber
	numberofplots=options.numberofplots

	#get hold
	hold=options.list[0].getfieldvalue('hold',False)

	#if nrows and ncols specified, then bypass
	if options.list[0].exist('nrows'):
		nrows=options.list[0].getfieldvalue('nrows')
		nr=True
	else:
		nrows=np.ceil(numberofplots/subplotwidth)
		nr=False

	if options.list[0].exist('ncols'):
		ncols=options.list[0].getfieldvalue('ncols')
		nc=True
	else:
		ncols=int(subplotwidth)
		nc=False
	ncols=int(ncols)
	nrows=int(nrows)

	#check that nrows and ncols were given at the same time!
	if not nr==nc:
		raise StandardError('error: nrows and ncols need to be specified together, or not at all')

	#Go through plots
	if numberofplots:
		#if plt.fignum_exists(figurenumber): 
		#	plt.cla()

		#if figsize specified
		if options.list[0].exist('figsize'):
			figsize=options.list[0].getfieldvalue('figsize')
			fig=plt.figure(figurenumber,figsize=(figsize[0],figsize[1]))#,tight_layout=True)
		else:
			fig=plt.figure(figurenumber)#,tight_layout=True)
		fig.clf()

		backgroundcolor=options.list[0].getfieldvalue('backgroundcolor',(0.7,0.7,0.7))
		fig.set_facecolor(backgroundcolor)


		translator={'on':'each',
								'off':'None',
								'one':'single'}
		# options needed to define plot grid
		plotnum=options.numberofplots
		direction=options.list[0].getfieldvalue('direction','row') # row,column
		axes_pad=options.list[0].getfieldvalue('axes_pad',0.25)
		add_all=options.list[0].getfieldvalue('add_all',True) # True,False
		share_all=options.list[0].getfieldvalue('share_all',True) # True,False
		label_mode=options.list[0].getfieldvalue('label_mode','L') # 1,L,all
		colorbar=options.list[0].getfieldvalue('colorbar','on') # on, off (single)
		cbar_mode=translator[colorbar]
		cbar_location=options.list[0].getfieldvalue('colorbarpos','right') # right,top
		cbar_size=options.list[0].getfieldvalue('colorbarsize','5%')
		cbar_pad=options.list[0].getfieldvalue('colorbarpad','2.5%') # None or %

		axgrid=ImageGrid(fig,111,
				nrows_ncols=(nrows,ncols),
				ngrids=plotnum,
				direction=direction,
				axes_pad=axes_pad,
				add_all=add_all,
				share_all=share_all,
				label_mode=label_mode,
				cbar_mode=cbar_mode,
				cbar_location=cbar_location,
				cbar_size=cbar_size,
				cbar_pad=cbar_pad)

		if cbar_mode=='None':
			for ax in axgrid.cbar_axes: 
				fig._axstack.remove(ax)

		for i,ax in enumerate(axgrid.axes_all):
			plot_manager(options.list[i].getfieldvalue('model',md),options.list[i],fig,axgrid,i)
		fig.show()
	else:
		raise StandardError('plotmodel error message: no output data found.')
