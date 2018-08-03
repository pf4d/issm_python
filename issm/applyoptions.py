import numpy as  np
from issm.cmaptools import truncate_colormap
from issm.plot_contour import plot_contour
from issm.plot_streamlines import plot_streamlines
from issm.expdisp import expdisp

try:
	from matplotlib.ticker import MaxNLocator
	from mpl_toolkits.axes_grid1 import make_axes_locatable
	from mpl_toolkits.mplot3d import Axes3D
	import matplotlib as mpl
	import matplotlib.pyplot as plt
except ImportError:
	print "could not import pylab, matplotlib has not been installed, no plotting capabilities enabled"

def applyoptions(md,data,options,fig,axgrid,gridindex):
	'''
	APPLYOPTIONS - apply options to current plot

	'plotobj' is the object returned by the specific plot call used to
	render the data.  This object is used for adding a colorbar.

		Usage:
			applyoptions(md,data,options)

		See also: PLOTMODEL, PARSE_OPTIONS
	'''

	# get handle to current figure and axes instance
	#fig = p.gcf()
	ax=	axgrid[gridindex]

	# {{{ font
	fontsize=options.getfieldvalue('fontsize',8)
	fontweight=options.getfieldvalue('fontweight','normal')
	fontfamily=options.getfieldvalue('fontfamily','sans-serif')
	font={'fontsize'		:fontsize,
				'fontweight'	:fontweight,
				'family'			:fontfamily}
	# }}}
	# {{{ title
	if options.exist('title'):
		title=options.getfieldvalue('title')
		if options.exist('titlefontsize'):
			titlefontsize=options.getfieldvalue('titlefontsize')
		else:
			titlefontsize=fontsize
		if options.exist('titlefontweight'):
			titlefontweight=options.getfieldvalue('titlefontweight')
		else:
			titlefontweight=fontweight
		#title font
		titlefont=font.copy()
		titlefont['size']=titlefontsize
		titlefont['weight']=titlefontweight
		ax.set_title(title,**titlefont)
	# }}}
	# {{{ xlabel, ylabel, zlabel
	if options.exist('labelfontsize'):
		labelfontsize=options.getfieldvalue('labelfontsize')
	else:
		labelfontsize=fontsize
	if options.exist('labelfontweight'):
		labelfontweight=options.getfieldvalue('labelfontweight')
	else:
		labelfontweight=fontweight

	#font dict for labels
	labelfont=font.copy()
	labelfont['fontsize']=labelfontsize
	labelfont['fontweight']=labelfontweight

	if options.exist('xlabel'):
		ax.set_xlabel(options.getfieldvalue('xlabel'),**labelfont)
	if options.exist('ylabel'):
		ax.set_ylabel(options.getfieldvalue('ylabel'),**labelfont)
	if options.exist('zlabel'):
		ax.set_zlabel(options.getfieldvalue('zlabel'),**labelfont)
	# }}}
	# {{{ xticks, yticks, zticks (tick locations)
	if options.exist('xticks'):
		if options.exist('xticklabels'):
			xticklabels=options.getfieldvalue('xticklabels')
			ax.set_xticks(options.getfieldvalue('xticks'),xticklabels)
		else:
			ax.set_xticks(options.getfieldvalue('xticks'))
	if options.exist('yticks'):
		if options.exist('yticklabels'):
			yticklabels=options.getfieldvalue('yticklabels')
			ax.set_yticks(options.getfieldvalue('yticks'),yticklabels)
		else:
			ax.set_yticks(options.getfieldvalue('yticks'))
	if options.exist('zticks'):
		if options.exist('zticklabels'):
			zticklabels=options.getfieldvalue('zticklabels')
			ax.set_zticks(options.getfieldvalue('zticks'),zticklabels)
		else:
			ax.set_zticks(options.getfieldvalue('zticks'))
	# }}}
	# {{{ xticklabels,yticklabels,zticklabels
	if options.getfieldvalue('ticklabels','off')=='off' or options.getfieldvalue('ticklabels',0)==0:
		options.addfielddefault('xticklabels',[])
		options.addfielddefault('yticklabels',[])
		# TODO check if ax has a z-axis (e.g. is 3D)
	if options.exist('xticklabels'):
		xticklabels=options.getfieldvalue('xticklabels')
		ax.set_xticklabels(xticklabels)
	if options.exist('yticklabels'):
		yticklabels=options.getfieldvalue('yticklabels')
		ax.set_yticklabels(yticklabels)
	if options.exist('zticklabels'):
		zticklabels=options.getfieldvalue('zticklabels')
		ax.set_zticklabels(zticklabels)
	# }}}
	# {{{ ticklabel notation
	#ax.ticklabel_format(style='sci',scilimits=(0,0))
	# }}}
	# {{{ ticklabelfontsize
	if options.exist('ticklabelfontsize'):
		for label in ax.get_xticklabels() + ax.get_yticklabels():
			label.set_fontsize(options.getfieldvalue('ticklabelfontsize'))
		if int(md.mesh.dimension)==3: 
			for label in ax.get_zticklabels():
				label.set_fontsize(options.getfieldvalue('ticklabelfontsize'))
	# }}}
	# {{{ view TOFIX
	#if int(md.mesh.dimension) == 3 and options.exist('layer'):
	#	#options.getfieldvalue('view') ?
	#	ax=fig.gca(projection='3d')
	#plt.show()
	# }}}
	# {{{ axis
	if options.exist('axis'):
		if options.getfieldvalue('axis',True)=='off':
			ax.ticklabel_format(style='plain')
			p.setp(ax.get_xticklabels(), visible=False)
			p.setp(ax.get_yticklabels(), visible=False)
	# }}}
	# {{{ box
	if options.exist('box'):
		eval(options.getfieldvalue('box'))
	# }}}
	# {{{ xlim, ylim, zlim
	if options.exist('xlim'):
		ax.set_xlim(options.getfieldvalue('xlim'))
	if options.exist('ylim'):
		ax.set_ylim(options.getfieldvalue('ylim'))
	if options.exist('zlim'):
		ax.set_zlim(options.getfieldvalue('zlim'))
	# }}}
	# {{{ latlon TODO
	# }}}
	# {{{ Basinzoom TODO
	# }}}
	# {{{ ShowBasins TODO
	# }}}
	# {{{ clim
	if options.exist('clim'):
		lims=options.getfieldvalue('clim')
		assert len(lims)==2, 'error, clim should be passed as a list of length 2'
	elif options.exist('caxis'):
		lims=options.getfieldvalue('caxis')
		assert len(lims)==2, 'error, caxis should be passed as a list of length 2'
		options.addfielddefault('clim',lims)
	else:
		if len(data)>0: 
			lims=[data.min(),data.max()]
		else: 
			lims=[0,1]
	# }}}
	# {{{ shading TODO
	#if options.exist('shading'):
	# }}}
	# {{{ grid
	if options.exist('grid'):
		if 'on' in options.getfieldvalue('grid','on'):
			ax.grid()
	# }}}
	# {{{ colormap
	if options.exist('colornorm'):
		norm=options.getfieldvalue('colornorm')
	if options.exist('colormap'):
		cmap=options.getfieldvalue('colormap')
	cbar_extend=0
	if options.exist('cmap_set_over'):
		cbar_extend+=1
	if options.exist('cmap_set_under'):
		cbar_extend+=2
	# }}}
	# {{{ contours
	if options.exist('contourlevels'):
		plot_contour(md,data,options,ax)
	# }}}
	# {{{ wrapping TODO
	# }}}
	# {{{ colorbar
	if options.getfieldvalue('colorbar',1)==1:
		if cbar_extend==0:
			extend='neither'
		elif cbar_extend==1:
			extend='max'
		elif cbar_extend==2:
			extend='min'
		elif cbar_extend==3:
			extend='both'
		cb = mpl.colorbar.ColorbarBase(ax.cax,cmap=cmap, norm=norm, extend=extend)
		if options.exist('alpha'):
			cb.set_alpha(options.getfieldvalue('alpha'))
		if options.exist('colorbarnumticks'):
			cb.locator=MaxNLocator(nbins=options.getfieldvalue('colorbarnumticks',5))
		else:
			cb.locator=MaxNLocator(nbins=5) # default 5 ticks
		if options.exist('colorbartickspacing'):
			locs=np.arange(lims[0],lims[1]+1,options.getfieldvalue('colorbartickspacing'))
			cb.set_ticks(locs)
		if options.exist('colorbarlines'):
			locs=np.arange(lims[0],lims[1]+1,options.getfieldvalue('colorbarlines'))
			cb.add_lines(locs,['k' for i in range(len(locs))],np.ones_like(locs))
		if options.exist('colorbarlineatvalue'):
			locs=options.getfieldvalue('colorbarlineatvalue')
			colors=options.getfieldvalue('colorbarlineatvaluecolor',['k' for i in range (len(locs))])
			widths=options.getfieldvalue('colorbarlineatvaluewidth',np.ones_like(locs))
			cb.add_lines(locs,colors,widths)
		if options.exist('colorbartitle'):
			if options.exist('colorbartitlepad'):
				cb.set_label(options.getfieldvalue('colorbartitle'),
										 labelpad=options.getfieldvalue('colorbartitlepad'),fontsize=fontsize)
			else:
				cb.set_label(options.getfieldvalue('colorbartitle'),fontsize=fontsize)
		cb.ax.tick_params(labelsize=fontsize)
		cb.solids.set_rasterized(True)
		cb.update_ticks()
		cb.set_alpha(1)
		cb.draw_all()
                if options.exist('colorbarfontsize'):
                        colorbarfontsize=options.getfieldvalue('colorbarfontsize')
                        cb.ax.tick_params(labelsize=colorbarfontsize)
                        # cb.set_ticks([0,-10])
                        # cb.set_ticklabels([-10,0,10])
                if options.exist('colorbarticks'):
                        colorbarticks=options.getfieldvalue('colorbarticks')
                        cb.set_ticks(colorbarticks)
		plt.sca(ax) # return to original axes control
	# }}}
	# {{{ expdisp 
	if options.exist('expdisp'):
	 	expdisp(ax,options)
	# }}}
	# {{{ area TODO
	# }}}
	# {{{ text
	if options.exist('text'):
		text=options.getfieldvalue('text')
		textx=options.getfieldvalue('textx')
		texty=options.getfieldvalue('texty')
		textcolor=options.getfieldvalue('textcolor')
		textweight=options.getfieldvalue('textweight')
		textrotation=options.getfieldvalue('textrotation')
		textfontsize=options.getfieldvalue('textfontsize')
		for label,x,y,size,color,weight,rotation in zip(text,textx,texty,textfontsize,textcolor,textweight,textrotation):
			ax.text(x,y,label,transform=ax.transAxes,fontsize=size,color=color,weight=weight,rotation=rotation)
	# }}}
	# {{{ north arrow TODO
	# }}}
	# {{{ scale ruler TODO
	# }}}
	# {{{ streamlines TOFIX
	if options.exist('streamlines'):
		plot_streamlines(md,options,ax)
	# }}}
	# {{{ axis positions TODO
	# }}}
	# {{{ figure position TODO
	# }}}
	# {{{ axes position TODO
	# }}}
	# {{{ showregion TODO
	# }}}
	# {{{ flat edges of a partition TODO
	# }}}
	# {{{ scatter TODO
	# }}}
	# {{{ backgroundcolor TODO
	# }}}
	# {{{ figurebackgroundcolor TODO
	# }}}
	# {{{ lighting TODO
	# }}}
	# {{{ point cloud TODO
	# }}}
	# {{{ inset TODO
	# }}}
	
