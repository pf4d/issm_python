import numpy as np
import os
from collections import OrderedDict
from issm.expwrite import expwrite
from issm.triangle import triangle

def roundmesh(md,radius,resolution):
	"""
	ROUNDMESH - create an unstructured round mesh 

	   This script will generate a structured round mesh
	   - radius     : specifies the radius of the circle in meters
	   - resolution : specifies the resolution in meters

	   Usage:
	      md=roundmesh(md,radius,resolution)
	"""

	#First we have to create the domain outline 

	#Get number of points on the circle
	pointsonedge=np.floor((2.*np.pi*radius) / resolution)

	#Calculate the cartesians coordinates of the points
	x_list=np.ones(pointsonedge)
	y_list=np.ones(pointsonedge)
	theta=np.linspace(0.,2.*np.pi,num=pointsonedge,endpoint=False)
	x_list=roundsigfig(radius*x_list*np.cos(theta),12)
	y_list=roundsigfig(radius*y_list*np.sin(theta),12)
	A=OrderedDict()
	A['x']=[x_list]
	A['y']=[y_list]
	A['density']=1.
	expwrite(A,'RoundDomainOutline.exp')

	#Call Bamg
	md=triangle(md,'RoundDomainOutline.exp',resolution)
	#md=bamg(md,'domain','RoundDomainOutline.exp','hmin',resolution)

	#move the closest node to the center
	pos=np.argmin(md.mesh.x**2+md.mesh.y**2)
	md.mesh.x[pos]=0.
	md.mesh.y[pos]=0.

	#delete domain
	os.remove('RoundDomainOutline.exp')

	return md

def roundsigfig(x,n):

	digits=np.ceil(np.log10(np.abs(x)))
	x=x/10.**digits
	x=np.round(x,decimals=n)
	x=x*10.**digits

	pos=np.nonzero(np.isnan(x))
	x[pos]=0.

	return x

