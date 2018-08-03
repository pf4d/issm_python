import numpy as  np
from issm.processmesh import processmesh
from issm.processdata import processdata
from issm.xy2ll import xy2ll
import matplotlib.pyplot as plt
import matplotlib as mpl
try:
    from mpl_toolkits.basemap import Basemap
except ImportError:
    print 'Basemap toolkit not installed'

import os

try:
  from osgeo import gdal
except ImportError:
	print 'osgeo/gdal for python not installed, plot_overlay is disabled'


def plot_overlay(md,data,options,ax):
	'''
	Function for plotting a georeferenced image.  This function is called
	from within the plotmodel code.
	'''

	x,y,z,elements,is2d,isplanet=processmesh(md,[],options)

	if data=='none' or data==None:
		imageonly=1
		data=np.float('nan')*np.ones((md.mesh.numberofvertices,))
		datatype=1
	else:
		imageonly=0
		data,datatype=processdata(md,data,options)

	if not is2d:
		raise StandardError('overlay plot not supported for 3D meshes, project on a 2D layer first')

	if not options.exist('overlay_image'):
		raise StandardError('overlay error: provide overlay_image with path to geotiff file')
	image=options.getfieldvalue('overlay_image')

	xlim=options.getfieldvalue('xlim',[min(md.mesh.x),max(md.mesh.x)])
	ylim=options.getfieldvalue('ylim',[min(md.mesh.y),max(md.mesh.y)])

	gtif=gdal.Open(image)
	trans=gtif.GetGeoTransform()
	xmin=trans[0]
	xmax=trans[0]+gtif.RasterXSize*trans[1]
	ymin=trans[3]+gtif.RasterYSize*trans[5]
	ymax=trans[3]
	
	# allow supplied image to have limits smaller than basemap or model limits
	x0=max(min(xlim),xmin)
	x1=min(max(xlim),xmax)
	y0=max(min(ylim),ymin)
	y1=min(max(ylim),ymax)
	inputname='temp.tif'
	os.system('gdal_translate -quiet -projwin ' + str(x0) + ' ' + str(y1) + ' ' + str(x1) + ' ' + str(y0) + ' ' + image+ ' ' + inputname)
	
	gtif=gdal.Open(inputname)
	arr=gtif.ReadAsArray()
	#os.system('rm -rf ./temp.tif')
	
	if gtif.RasterCount>=3:  # RGB array
		r=gtif.GetRasterBand(1).ReadAsArray()
		g=gtif.GetRasterBand(2).ReadAsArray()
		b=gtif.GetRasterBand(3).ReadAsArray()
		arr=0.299*r+0.587*g+0.114*b

	# normalize array
	arr=arr/np.float(np.max(arr.ravel()))
        arr=1.-arr # somehow the values got flipped

	if options.getfieldvalue('overlayhist',0)==1:
		ax=plt.gca()
		num=2
		while True:
			if not plt.fignum_exists(num):
				break
			else:
				num+=1
		plt.figure(num)
		plt.hist(arr.flatten(),bins=256,range=(0.,1.))
		plt.title('histogram of overlay image, use for setting overlaylims')
                plt.show()
		plt.sca(ax) # return to original axes/figure
		
	# get parameters from cropped geotiff
	trans=gtif.GetGeoTransform()
	xmin=trans[0]
	xmax=trans[0]+gtif.RasterXSize*trans[1]
	ymin=trans[3]+gtif.RasterYSize*trans[5]
	ymax=trans[3]
	dx=trans[1]
	dy=trans[5]	
	
	xarr=np.arange(xmin,xmax,dx)
	yarr=np.arange(ymin,ymax,-dy) # -dy since origin='upper' (not sure how robust this is)
	xg,yg=np.meshgrid(xarr,yarr)
	overlaylims=options.getfieldvalue('overlaylims',[min(arr.ravel()),max(arr.ravel())])
	norm=mpl.colors.Normalize(vmin=overlaylims[0],vmax=overlaylims[1])

	if options.exist('basemap'):
		# create coordinate grid in map projection units (for plotting)
		lat,lon=xy2ll(xlim,ylim,-1,0,71)
                #plt.sca(ax)
                width=xmax-xmin
                height=ymax-ymin
                lat_0,lon_0=xy2ll(xmin+width/2.,ymin+height/2.,-1,0,71)
	        m=Basemap(projection='spstere',
                        llcrnrlon=lon[0],llcrnrlat=lat[0],urcrnrlon=lon[1],urcrnrlat=lat[1],
                        epsg=3031,
                        resolution='c')
                        #width=width,height=height,lon_0=lon_0,lat_0=lat_0,
                        #lat_0=-90,lon_0=0,lat_ts=-71,
                        #llcrnrx=x0,llcrnry=y0,urcrnrx=x1,urcrnry=y1)
                #test
                #m.ax=ax
	        meridians=np.arange(-180.,181.,1.)
	        parallels=np.arange(-80.,80.,1.)
	        m.drawparallels(parallels,labels=[0,0,1,1]) # labels=[left,right,top,bottom]
	        m.drawmeridians(meridians,labels=[1,1,0,0])
                m.drawcoastlines()
	        pc=m.pcolormesh(xg, yg, np.flipud(arr), cmap=mpl.cm.Greys, norm=norm, ax=ax)

	else:
	        pc=ax.pcolormesh(xg, yg, np.flipud(arr), cmap=mpl.cm.Greys, norm=norm)
        
	#rasterization? 
	if options.getfieldvalue('rasterized',0):
		pc.set_rasterized(True)
