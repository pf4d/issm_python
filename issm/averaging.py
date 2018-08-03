import numpy as  np
from GetAreas import GetAreas
import MatlabFuncs as m
try:
	from scipy.sparse import csc_matrix
except ImportError:
	print "could not import scipy, no averaging capabilities enabled"

def averaging(md,data,iterations,layer=0):
	'''
	AVERAGING - smooths the input over the mesh
	
	   This routine takes a list over the elements or the nodes in input
	   and return a list over the nodes.
	   For each iterations it computes the average over each element (average 
	   of the vertices values) and then computes the average over each node
	   by taking the average of the element around a node weighted by the
	   elements volume
	   For 3d mesh, a last argument can be added to specify the layer to be averaged on.
	
	   Usage:
	      smoothdata=averaging(md,data,iterations)
	      smoothdata=averaging(md,data,iterations,layer)
	
	   Examples:
	      velsmoothed=averaging(md,md.initialization.vel,4)
	      pressure=averaging(md,md.initialization.pressure,0)
	      temperature=averaging(md,md.initialization.temperature,1,1)
	'''

	if len(data)!=md.mesh.numberofelements and len(data)!=md.mesh.numberofvertices:
		raise StandardError('averaging error message: data not supported yet')
	if md.mesh.dimension()==3 and layer!=0:
		if layer<=0 or layer>md.mesh.numberoflayers:
			raise ValueError('layer should be between 1 and md.mesh.numberoflayers')
	else:
		layer=0
	
	#initialization
	if layer==0:
		weights=np.zeros(md.mesh.numberofvertices,)
		data=data.flatten(1)
	else:
		weights=np.zeros(md.mesh.numberofvertices2d,)
		data=data[(layer-1)*md.mesh.numberofvertices2d+1:layer*md.mesh.numberofvertices2d,:]
	
	#load some variables (it is much faster if the variabes are loaded from md once for all)
	if layer==0:
		index=md.mesh.elements
		numberofnodes=md.mesh.numberofvertices
		numberofelements=md.mesh.numberofelements
	else:
		index=md.mesh.elements2d
		numberofnodes=md.mesh.numberofvertices2d
		numberofelements=md.mesh.numberofelements2d

	
	#build some variables
	if md.mesh.dimension()==3 and layer==0:
		rep=6
		areas=GetAreas(index,md.mesh.x,md.mesh.y,md.mesh.z)
	elif md.mesh.dimension()==2:
		rep=3
		areas=GetAreas(index,md.mesh.x,md.mesh.y)
	else:
		rep=3
		areas=GetAreas(index,md.mesh.x2d,md.mesh.y2d)

	index=index-1 # since python indexes starting from zero
	line=index.flatten(1)
	areas=np.vstack(areas).reshape(-1,)
	summation=1./rep*np.ones(rep,)
	linesize=rep*numberofelements
	
	#update weights that holds the volume of all the element holding the node i
	weights=csc_matrix( (np.tile(areas,(rep,1)).reshape(-1,),(line,np.zeros(linesize,))), shape=(numberofnodes,1))
	
	#initialization
	if len(data)==numberofelements:
		average_node=csc_matrix( (np.tile(areas*data,(rep,1)).reshape(-1,),(line,np.zeros(linesize,))), shape=(numberofnodes,1))
		average_node=average_node/weights
		average_node = csc_matrix(average_node)
	else:
		average_node=csc_matrix(data.reshape(-1,1))

	#loop over iteration
	for i in np.arange(1,iterations+1):
		average_el=np.asarray(np.dot(average_node.todense()[index].reshape(numberofelements,rep),np.vstack(summation))).reshape(-1,)
		average_node=csc_matrix( (np.tile(areas*average_el.reshape(-1),(rep,1)).reshape(-1,),(line,np.zeros(linesize,))), shape=(numberofnodes,1))
		average_node=average_node/weights
		average_node=csc_matrix(average_node)
	
	#return output as a full matrix (C code do not like sparse matrices)
	average=np.asarray(average_node.todense()).reshape(-1,)

	return average
