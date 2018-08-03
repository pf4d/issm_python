import os.path
import numpy as np
from mesh2d import mesh2d
from TriMesh import TriMesh
from NodeConnectivity import NodeConnectivity
from ElementConnectivity import ElementConnectivity
import MatlabFuncs as m

def triangle(md,domainname,*args):
	"""
	TRIANGLE - create model mesh using the triangle package

	   This routine creates a model mesh using TriMesh and a domain outline, to within a certain resolution
	   where md is a @model object, domainname is the name of an Argus domain outline file, 
	   and resolution is a characteristic length for the mesh (same unit as the domain outline
	   unit). Riftname is an optional argument (Argus domain outline) describing rifts.

	   Usage:
	      md=triangle(md,domainname,resolution)
	   or md=triangle(md,domainname, resolution, riftname)

	   Examples:
	      md=triangle(md,'DomainOutline.exp',1000);
	      md=triangle(md,'DomainOutline.exp',1000,'Rifts.exp');
	"""

	#Figure out a characteristic area. Resolution is a node oriented concept (ex a 1000m  resolution node would 
	#be made of 1000*1000 area squares). 

	if len(args)==1:
		resolution=args[0]
		riftname=''
	if len(args)==2:
		riftname=args[0]
		resolution=args[1]

	#Check that mesh was not already run, and warn user: 
	if md.mesh.numberofelements:
		choice = raw_input('This model already has a mesh. Are you sure you want to go ahead? (y/n)')
		if not m.strcmp(choice,'y'):
			print 'no meshing done ... exiting'
			return None

	area = resolution**2

	#Check that file exist (this is a very very common mistake)
	if not os.path.exists(domainname):
		raise IOError("file '%s' not found" % domainname)

	#Mesh using TriMesh
	md.mesh=mesh2d()
	md.mesh.elements,md.mesh.x,md.mesh.y,md.mesh.segments,md.mesh.segmentmarkers=TriMesh(domainname,riftname,area)
	md.mesh.elements=md.mesh.elements.astype(int)
	md.mesh.segments=md.mesh.segments.astype(int)
	md.mesh.segmentmarkers=md.mesh.segmentmarkers.astype(int)

	#Fill in rest of fields:
	md.mesh.numberofelements = np.size(md.mesh.elements,axis=0)
	md.mesh.numberofvertices = np.size(md.mesh.x)
	md.mesh.vertexonboundary = np.zeros(md.mesh.numberofvertices,bool)
	md.mesh.vertexonboundary[md.mesh.segments[:,0:2]-1] = True

	#Now, build the connectivity tables for this mesh.
	md.mesh.vertexconnectivity = NodeConnectivity(md.mesh.elements, md.mesh.numberofvertices)[0]
	md.mesh.elementconnectivity = ElementConnectivity(md.mesh.elements, md.mesh.vertexconnectivity)[0]

	return md
