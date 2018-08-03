import os.path
import numpy as np
import copy
from issm.NodeConnectivity import NodeConnectivity
from issm.ElementConnectivity import ElementConnectivity
from issm.mesh2d import mesh2d
from issm.mesh3dprisms import mesh3dprisms
import issm.MatlabFuncs as m

def contourenvelope(md,*args):
	"""
	CONTOURENVELOPE - build a set of segments enveloping a contour .exp

	   Usage:
	      segments=contourenvelope(md,varargin)

	   Example:
	      segments=contourenvelope(md,'Stream.exp');
	      segments=contourenvelope(md);
	"""

	#some checks
	if len(args)>1:
		raise RuntimeError("contourenvelope error message: bad usage")

	if len(args)==1:
		flags=args[0]

		if   isinstance(flags,(str,unicode)):
			file=flags
			if not os.path.exists(file):
				raise IOError("contourenvelope error message: file '%s' not found" % file)
			isfile=1
		elif isinstance(flags,(bool,int,long,float)):
			#do nothing for now
			isfile=0
		else:
			raise TypeError("contourenvelope error message:  second argument should be a file or an elements flag")

	#Now, build the connectivity tables for this mesh.
	#Computing connectivity
	if np.size(md.mesh.vertexconnectivity,axis=0)!=md.mesh.numberofvertices and np.size(md.mesh.vertexconnectivity,axis=0)!=md.mesh.numberofvertices2d:
		md.mesh.vertexconnectivity=NodeConnectivity(md.mesh.elements,md.mesh.numberofvertices)[0]
	if np.size(md.mesh.elementconnectivity,axis=0)!=md.mesh.numberofelements and np.size(md.mesh.elementconnectivity,axis=0)!=md.mesh.numberofelements2d:
		md.mesh.elementconnectivity=ElementConnectivity(md.mesh.elements,md.mesh.vertexconnectivity)[0]

	#get nodes inside profile
	elementconnectivity=copy.deepcopy(md.mesh.elementconnectivity)
	if md.mesh.dimension()==2:
		elements=copy.deepcopy(md.mesh.elements)
		x=copy.deepcopy(md.mesh.x)
		y=copy.deepcopy(md.mesh.y)
		numberofvertices=copy.deepcopy(md.mesh.numberofvertices)
		numberofelements=copy.deepcopy(md.mesh.numberofelements)
	else:
		elements=copy.deepcopy(md.mesh.elements2d)
		x=copy.deepcopy(md.mesh.x2d)
		y=copy.deepcopy(md.mesh.y2d)
		numberofvertices=copy.deepcopy(md.mesh.numberofvertices2d)
		numberofelements=copy.deepcopy(md.mesh.numberofelements2d)

	if len(args)==1:

		if isfile:
			#get flag list of elements and nodes inside the contour
			nodein=ContourToMesh(elements,x,y,file,'node',1)
			elemin=(np.sum(nodein(elements),axis=1)==np.size(elements,axis=1))
			#modify element connectivity
			elemout=np.nonzero(np.logical_not(elemin))[0]
			elementconnectivity[elemout,:]=0
			elementconnectivity[np.nonzero(m.ismember(elementconnectivity,elemout+1))]=0
		else:
			#get flag list of elements and nodes inside the contour
			nodein=np.zeros(numberofvertices)
			elemin=np.zeros(numberofelements)

			pos=np.nonzero(flags)
			elemin[pos]=1
			nodein[elements[pos,:]-1]=1

			#modify element connectivity
			elemout=np.nonzero(np.logical_not(elemin))[0]
			elementconnectivity[elemout,:]=0
			elementconnectivity[np.nonzero(m.ismember(elementconnectivity,elemout+1))]=0

	#Find element on boundary
	#First: find elements on the boundary of the domain
	flag=copy.deepcopy(elementconnectivity)
	if len(args)==1:
		flag[np.nonzero(flag)]=elemin[flag[np.nonzero(flag)]]
	elementonboundary=np.logical_and(np.prod(flag,axis=1)==0,np.sum(flag,axis=1)>0)

	#Find segments on boundary
	pos=np.nonzero(elementonboundary)[0]
	num_segments=np.size(pos)
	segments=np.zeros((num_segments*3,3),int)
	count=0

	for el1 in pos:
		els2=elementconnectivity[el1,np.nonzero(elementconnectivity[el1,:])[0]]-1
		if np.size(els2)>1:
			flag=np.intersect1d(np.intersect1d(elements[els2[0],:],elements[els2[1],:]),elements[el1,:])
			nods1=elements[el1,:]
			nods1=np.delete(nods1,np.nonzero(nods1==flag))
			segments[count,:]=[nods1[0],nods1[1],el1+1]

			ord1=np.nonzero(nods1[0]==elements[el1,:])[0][0]
			ord2=np.nonzero(nods1[1]==elements[el1,:])[0][0]

			#swap segment nodes if necessary
			if ( (ord1==0 and ord2==1) or (ord1==1 and ord2==2) or (ord1==2 and ord2==0) ):
				temp=segments[count,0]
				segments[count,0]=segments[count,1]
				segments[count,1]=temp
			segments[count,0:2]=np.flipud(segments[count,0:2])
			count+=1
		else:
			nods1=elements[el1,:]
			flag=np.setdiff1d(nods1,elements[els2,:])
			for j in xrange(0,3):
				nods=np.delete(nods1,j)
				if np.any(m.ismember(flag,nods)):
					segments[count,:]=[nods[0],nods[1],el1+1]
					ord1=np.nonzero(nods[0]==elements[el1,:])[0][0]
					ord2=np.nonzero(nods[1]==elements[el1,:])[0][0]
					if ( (ord1==0 and ord2==1) or (ord1==1 and ord2==2) or (ord1==2 and ord2==0) ):
						temp=segments[count,0]
						segments[count,0]=segments[count,1]
						segments[count,1]=temp
					segments[count,0:2]=np.flipud(segments[count,0:2])
					count+=1
	segments=segments[0:count,:]

	return segments

