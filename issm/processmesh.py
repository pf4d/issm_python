from math import isnan
import numpy as  np

def processmesh(md,data,options):
	"""
	PROCESSMESH - process the mesh for plotting
	
	Usage:
	x,y,z,elements,is2d=processmech(md,data,options)
	
	See also: PLOTMODEL, PROCESSDATA
	"""
	
	# {{{ check mesh size parameters
	if md.mesh.numberofvertices==0:
		raise ValueError('processmesh error: mesh is empty')
	if md.mesh.numberofvertices==md.mesh.numberofelements:
		raise ValueError('processmesh error: the number of elements is the same as the number of nodes')
	# }}}
  # {{{ treating coordinates

	try:
		z=md.mesh.z
	except AttributeError:
		z=np.zeros(np.shape(md.mesh.x))
	elements=md.mesh.elements-1
	
	if options.getfieldvalue('layer',0)>=1:
		x=md.mesh.x2d
		y=md.mesh.y2d
		z=np.zeros(np.shape(x))
		elements=md.mesh.elements2d-1
	elif 'latlon' in options.getfieldvalue('coord','xy'):
		x=md.mesh.long
		y=md.mesh.lat
	else:
		x=md.mesh.x
		y=md.mesh.y

	#is it a 2D plot?
	if md.mesh.dimension()==2 or options.getfieldvalue('layer',0)>=1:
		is2d=1
	else:
		is2d=0
		
	#units
	if options.exist('unit'):
		unit=options.getfieldvalue('unit')
		x=x*unit
		y=y*unit
		z=z*unit

	#is model a member of planet class? (workaround until planet class defined)
	if md.__class__.__name__!='model':
		isplanet=1
	else:
		isplanet=0

	return x,y,z,elements,is2d,isplanet
