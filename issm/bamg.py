import os.path
import numpy as  np
from collections import OrderedDict

from issm.mesh2d import mesh2d
from issm.pairoptions import pairoptions
from issm.bamggeom import bamggeom
from issm.bamgmesh import bamgmesh
from issm.expread import expread
from issm.expwrite import expwrite
from issm.SegIntersect import SegIntersect
from issm.BamgMesher import BamgMesher
from issm.ContourToNodes import ContourToNodes
import issm.MatlabFuncs as m

def bamg(md,*args):
	"""
	BAMG - mesh generation

	   Available options (for more details see ISSM website http://issm.jpl.nasa.gov/):

	   - domain :            followed by an ARGUS file that prescribes the domain outline
	   - hmin :              minimum edge length (default is 10^-100)
	   - hmax :              maximum edge length (default is 10^100)
	   - hVertices :         imposed edge length for each vertex (geometry or mesh)
	   - hminVertices :      minimum edge length for each vertex (mesh)
	   - hmaxVertices :      maximum edge length for each vertex (mesh)

	   - anisomax :          maximum ratio between the smallest and largest edges (default is 10^30)
	   - coeff :             coefficient applied to the metric (2-> twice as many elements, default is 1)
	   - cutoff :            scalar used to compute the metric when metric type 2 or 3 are applied
	   - err :               error used to generate the metric from a field
	   - errg :              geometric error (default is 0.1)
	   - field :             field of the model that will be used to compute the metric
	                         to apply several fields, use one column per field
	   - gradation :         maximum ratio between two adjacent edges
	   - Hessiantype :       0 -> use double P2 projection (default)
	                         1 -> use Green formula
	   - KeepVertices :      try to keep initial vertices when adaptation is done on an existing mesh (default 1)
	   - MaxCornerAngle :    maximum angle of corners in degree (default is 10)
	   - maxnbv :            maximum number of vertices used to allocate memory (default is 10^6)
	   - maxsubdiv :         maximum subdivision of exisiting elements (default is 10)
	   - metric :            matrix (numberofnodes x 3) used as a metric
	   - Metrictype :        1 -> absolute error          c/(err coeff^2) * Abs(H)        (default)
	                         2 -> relative error          c/(err coeff^2) * Abs(H)/max(s,cutoff*max(s))
	                         3 -> rescaled absolute error c/(err coeff^2) * Abs(H)/(smax-smin)
	   - nbjacoby :          correction used by Hessiantype=1 (default is 1)
	   - nbsmooth :          number of metric smoothing procedure (default is 3)
	   - omega :             relaxation parameter of the smoothing procedure (default is 1.8)
	   - power :             power applied to the metric (default is 1)
	   - splitcorners :      split triangles whuch have 3 vertices on the outline (default is 1)
	   - geometricalmetric : take the geometry into account to generate the metric (default is 0)
	   - verbose :           level of verbosity (default is 1)

	   - rifts :             followed by an ARGUS file that prescribes the rifts
	   - toltip :            tolerance to move tip on an existing point of the domain outline
	   - tracks :            followed by an ARGUS file that prescribes the tracks that the mesh will stick to
	   - RequiredVertices :  mesh vertices that are required. [x,y,ref]; ref is optional
	   - tol :               if the distance between 2 points of the domain outline is less than tol, they
	                         will be merged

	   Examples:
	      md=bamg(md,'domain','DomainOutline.exp','hmax',3000);
	      md=bamg(md,'field',[md.inversion.vel_obs md.geometry.thickness],'hmax',20000,'hmin',1000);
	      md=bamg(md,'metric',A,'hmin',1000,'hmax',20000,'gradation',3,'anisomax',1);
	"""

	#process options
	options=pairoptions(*args)
#	options=deleteduplicates(options,1);

	#initialize the structures required as input of Bamg
	bamg_options=OrderedDict()
	bamg_geometry=bamggeom()
	bamg_mesh=bamgmesh()

	# Bamg Geometry parameters {{{
	if options.exist('domain'):

		#Check that file exists
		domainfile=options.getfieldvalue('domain')
		if not os.path.exists(domainfile):
			raise IOError("bamg error message: file '%s' not found" % domainfile)
		domain=expread(domainfile)

		#Build geometry 
		count=0
		for i,domaini in enumerate(domain):

			#Check that the domain is closed
			if (domaini['x'][0]!=domaini['x'][-1] or domaini['y'][0]!=domaini['y'][-1]):
				raise RuntimeError("bamg error message: all contours provided in ''domain'' should be closed")

			#Checks that all holes are INSIDE the principle domain outline
			if i:
				flags=ContourToNodes(domaini['x'],domaini['y'],domainfile,0)[0]
				if np.any(np.logical_not(flags)):
					raise RuntimeError("bamg error message: All holes should be strictly inside the principal domain")

			#Add all points to bamg_geometry
			nods=domaini['nods']-1    #the domain are closed 0=end
			bamg_geometry.Vertices=np.vstack((bamg_geometry.Vertices,np.vstack((domaini['x'][0:nods],domaini['y'][0:nods],np.ones((nods)))).T))
			bamg_geometry.Edges   =np.vstack((bamg_geometry.Edges,np.vstack((np.arange(count+1,count+nods+1),np.hstack((np.arange(count+2,count+nods+1),count+1)),1.*np.ones((nods)))).T))
			if i:
				bamg_geometry.SubDomains=np.vstack((bamg_geometry.SubDomains,[2,count+1,1,1]))

			# bamg_geometry.Vertices=np.hstack((bamg_geometry.Vertices,np.vstack((domaini['x'][0:nods].reshape(-1),domaini['y'][0:nods].reshape(-1),np.ones((nods))))))
			# bamg_geometry.Edges   =np.vstack((bamg_geometry.Edges,np.hstack((np.arange(count+1,count+nods+1).reshape(-1,),np.hstack((np.arange(count+2,count+nods+1),count+1)).reshape(-1,),1.*np.ones((nods,))))))
			# if i:
			# 	bamg_geometry.SubDomains=np.vstack((bamg_geometry.SubDomains,[2,count+1,1,1]))

			#update counter
			count+=nods

		#take care of rifts
		if options.exist('rifts'):

			#Check that file exists
			riftfile=options.getfieldvalue('rifts')
			if not os.path.exists(riftfile):
				raise IOError("bamg error message: file '%s' not found" % riftfile)
			rift=expread(riftfile)

			for i,rifti in enumerate(rift):

				#detect whether all points of the rift are inside the domain
				flags=ContourToNodes(rifti['x'],rifti['y'],domain[0],0)[0]
				if np.all(np.logical_not(flags)):
					raise RuntimeError("one rift has all its points outside of the domain outline")

				elif np.any(np.logical_not(flags)):
					#We LOTS of work to do
					print "Rift tip outside of or on the domain has been detected and is being processed..."

					#check that only one point is outside (for now)
					if np.sum(np.logical_not(flags).astype(int))!=1:
						raise RuntimeError("bamg error message: only one point outside of the domain is supported yet")

					#Move tip outside to the first position
					if   not flags[0]:
						#OK, first point is outside (do nothing),
						pass
					elif not flags[-1]:
						rifti['x']=np.flipud(rifti['x'])
						rifti['y']=np.flipud(rifti['y'])
					else:
						raise RuntimeError("bamg error message: only a rift tip can be outside of the domain")

					#Get cordinate of intersection point
					x1=rifti['x'][0]
					y1=rifti['y'][0]
					x2=rifti['x'][1]
					y2=rifti['y'][1]
					for j in xrange(0,np.size(domain[0]['x'])-1):
						if SegIntersect(np.array([[x1,y1],[x2,y2]]),np.array([[domain[0]['x'][j],domain[0]['y'][j]],[domain[0]['x'][j+1],domain[0]['y'][j+1]]])):

							#Get position of the two nodes of the edge in domain
							i1=j
							i2=j+1

							#rift is crossing edge [i1 i2] of the domain
							#Get coordinate of intersection point (http://mathworld.wolfram.com/Line-LineIntersection.html)
							x3=domain[0]['x'][i1]
							y3=domain[0]['y'][i1]
							x4=domain[0]['x'][i2]
							y4=domain[0]['y'][i2]
#							x=det([det([x1 y1; x2 y2])  x1-x2;det([x3 y3; x4 y4])  x3-x4])/det([x1-x2 y1-y2;x3-x4 y3-y4]);
#							y=det([det([x1 y1; x2 y2])  y1-y2;det([x3 y3; x4 y4])  y3-y4])/det([x1-x2 y1-y2;x3-x4 y3-y4]);
							x=np.linalg.det(np.array([[np.linalg.det(np.array([[x1,y1],[x2,y2]])),x1-x2],[np.linalg.det(np.array([[x3,y3],[x4,y4]])),x3-x4]]))/np.linalg.det(np.array([[x1-x2,y1-y2],[x3-x4,y3-y4]]))
							y=np.linalg.det(np.array([[np.linalg.det(np.array([[x1,y1],[x2,y2]])),y1-y2],[np.linalg.det(np.array([[x3,y3],[x4,y4]])),y3-y4]]))/np.linalg.det(np.array([[x1-x2,y1-y2],[x3-x4,y3-y4]]))

							segdis= sqrt((x4-x3)**2+(y4-y3)**2)
							tipdis=np.array([sqrt((x-x3)**2+(y-y3)**2),sqrt((x-x4)**2+(y-y4)**2)])

							if np.min(tipdis)/segdis < options.getfieldvalue('toltip',0):
								print "moving tip-domain intersection point"

								#Get position of the closer point
								if tipdis[0]>tipdis[1]:
									pos=i2
								else:
									pos=i1

								#This point is only in Vertices (number pos).
								#OK, now we can add our own rift
								nods=rifti['nods']-1
								bamg_geometry.Vertices=np.vstack((bamg_geometry.Vertices,np.hstack((rifti['x'][1:].reshape(-1,),rifti['y'][1:].reshape(-1,),np.ones((nods,1))))))
								bamg_geometry.Edges=np.vstack((bamg_geometry.Edges,\
									np.array([[pos,count+1,(1+i)]]),\
									np.hstack((np.arange(count+1,count+nods).reshape(-1,),np.arange(count+2,count+nods+1).reshape(-1,),(1+i)*np.ones((nods-1,1))))))
								count+=nods

								break

							else:
								#Add intersection point to Vertices
								bamg_geometry.Vertices=np.vstack((bamg_geometry.Vertices,np.array([[x,y,1]])))
								count+=1

								#Decompose the crossing edge into 2 subedges
								pos=np.nonzero(np.logical_and(bamg_geometry.Edges[:,0]==i1,bamg_geometry.Edges[:,1]==i2))[0]
								if not pos:
									raise RuntimeError("bamg error message: a problem occurred...")
								bamg_geometry.Edges=np.vstack((bamg_geometry.Edges[0:pos-1,:],\
									np.array([[bamg_geometry.Edges[pos,0],count                     ,bamg_geometry.Edges[pos,2]]]),\
									np.array([[count                     ,bamg_geometry.Edges[pos,1],bamg_geometry.Edges[pos,2]]]),\
									bamg_geometry.Edges[pos+1:,:]))

								#OK, now we can add our own rift
								nods=rifti['nods']-1
								bamg_geometry.Vertices=np.vstack((bamg_geometry.Vertices,np.hstack((rifti['x'][1:].reshape(-1,),rifti['y'][1:].reshape(-1,),np.ones((nods,1))))))
								bamg_geometry.Edges=np.vstack((bamg_geometry.Edges,\
									np.array([[count,count+1,2]]),\
									np.hstack((np.arange(count+1,count+nods).reshape(-1,),np.arange(count+2,count+nods+1).reshape(-1,),(1+i)*np.ones((nods-1,1))))))
								count+=nods

								break

				else:
					nods=rifti['nods']-1
					bamg_geometry.Vertices=np.vstack(bamg_geometry.Vertices, np.hstack(rifti['x'][:],rifti['y'][:],np.ones((nods+1,1))))
					bamg_geometry.Edges   =np.vstack(bamg_geometry.Edges, np.hstack(np.arange(count+1,count+nods).reshape(-1,),np.arange(count+2,count+nods+1).reshape(-1,),i*np.ones((nods,1))))
					count=+nods+1

		#Deal with tracks
		if options.exist('tracks'):

			#read tracks
			track=options.getfieldvalue('tracks')
			if all(isinstance(track,(str,unicode))):
				A=expread(track)
				track=np.hstack((A.x.reshape(-1,),A.y.reshape(-1,)))
			else:
				track=float(track)    #for some reason, it is of class "single"
			if np.size(track,axis=1)==2:
				track=np.hstack((track,3.*np.ones((size(track,axis=0),1))))

			#only keep those inside
			flags=ContourToNodes(track[:,0],track[:,1],domainfile,0)[0]
			track=track[np.nonzero(flags),:]

			#Add all points to bamg_geometry
			nods=np.size(track,axis=0)
			bamg_geometry.Vertices=np.vstack((bamg_geometry.Vertices,track))
			bamg_geometry.Edges   =np.vstack((bamg_geometry.Edges,np.hstack((np.arange(count+1,count+nods).reshape(-1,),np.arange(count+2,count+nods+1).reshape(-1,),3.*np.ones((nods-1,1))))))

			#update counter
			count+=nods

		#Deal with vertices that need to be kept by mesher
		if options.exist('RequiredVertices'):

			#recover RequiredVertices
			requiredvertices=options.getfieldvalue('RequiredVertices')    #for some reason, it is of class "single"
			if np.size(requiredvertices,axis=1)==2:
				requiredvertices=np.hstack((requiredvertices,4.*np.ones((np.size(requiredvertices,axis=0),1))))

			#only keep those inside
			flags=ContourToNodes(requiredvertices[:,0],requiredvertices[:,1],domainfile,0)[0]
			requiredvertices=requiredvertices[np.nonzero(flags)[0],:]
			#Add all points to bamg_geometry
			nods=np.size(requiredvertices,axis=0)
			bamg_geometry.Vertices=np.vstack((bamg_geometry.Vertices,requiredvertices))

			#update counter
			count+=nods

		#process geom
		#bamg_geometry=processgeometry(bamg_geometry,options.getfieldvalue('tol',float(nan)),domain[0])

	elif isinstance(md.private.bamg,dict) and 'geometry' in md.private.bamg:
		bamg_geometry=bamggeom(md.private.bamg['geometry'].__dict__) 
	else:
		#do nothing...
		pass
	#}}}
	# Bamg Mesh parameters {{{
	if not options.exist('domain') and md.mesh.numberofvertices and m.strcmp(md.mesh.elementtype(),'Tria'):

		if isinstance(md.private.bamg,dict) and 'mesh' in md.private.bamg:
			bamg_mesh=bamgmesh(md.private.bamg['mesh'].__dict__)
		else:
			bamg_mesh.Vertices=np.vstack((md.mesh.x,md.mesh.y,np.ones((md.mesh.numberofvertices)))).T
			#bamg_mesh.Vertices=np.hstack((md.mesh.x.reshape(-1,),md.mesh.y.reshape(-1,),np.ones((md.mesh.numberofvertices,1))))
			bamg_mesh.Triangles=np.hstack((md.mesh.elements,np.ones((md.mesh.numberofelements,1))))

		if isinstance(md.rifts.riftstruct,dict):
			raise TypeError("bamg error message: rifts not supported yet. Do meshprocessrift AFTER bamg")
	#}}}
	# Bamg Options {{{
	bamg_options['Crack']=options.getfieldvalue('Crack',0)
	bamg_options['anisomax']=options.getfieldvalue('anisomax',10.**30)
	bamg_options['coeff']=options.getfieldvalue('coeff',1.)
	bamg_options['cutoff']=options.getfieldvalue('cutoff',10.**-5)
	bamg_options['err']=options.getfieldvalue('err',np.array([[0.01]]))
	bamg_options['errg']=options.getfieldvalue('errg',0.1)
	bamg_options['field']=options.getfieldvalue('field',np.empty((0,1)))
	bamg_options['gradation']=options.getfieldvalue('gradation',1.5)
	bamg_options['Hessiantype']=options.getfieldvalue('Hessiantype',0)
	bamg_options['hmin']=options.getfieldvalue('hmin',10.**-100)
	bamg_options['hmax']=options.getfieldvalue('hmax',10.**100)
	bamg_options['hminVertices']=options.getfieldvalue('hminVertices',np.empty((0,1)))
	bamg_options['hmaxVertices']=options.getfieldvalue('hmaxVertices',np.empty((0,1)))
	bamg_options['hVertices']=options.getfieldvalue('hVertices',np.empty((0,1)))
	bamg_options['KeepVertices']=options.getfieldvalue('KeepVertices',1)
	bamg_options['MaxCornerAngle']=options.getfieldvalue('MaxCornerAngle',10.)
	bamg_options['maxnbv']=options.getfieldvalue('maxnbv',10**6)
	bamg_options['maxsubdiv']=options.getfieldvalue('maxsubdiv',10.)
	bamg_options['metric']=options.getfieldvalue('metric',np.empty((0,1)))
	bamg_options['Metrictype']=options.getfieldvalue('Metrictype',0)
	bamg_options['nbjacobi']=options.getfieldvalue('nbjacobi',1)
	bamg_options['nbsmooth']=options.getfieldvalue('nbsmooth',3)
	bamg_options['omega']=options.getfieldvalue('omega',1.8)
	bamg_options['power']=options.getfieldvalue('power',1.)
	bamg_options['splitcorners']=options.getfieldvalue('splitcorners',1)
	bamg_options['geometricalmetric']=options.getfieldvalue('geometricalmetric',0)
	bamg_options['random']=options.getfieldvalue('rand',True)
	bamg_options['verbose']=options.getfieldvalue('verbose',1)
	#}}}

	#call Bamg
	bamgmesh_out,bamggeom_out=BamgMesher(bamg_mesh.__dict__,bamg_geometry.__dict__,bamg_options)

	# plug results onto model
	md.private.bamg=OrderedDict()
	md.private.bamg['mesh']=bamgmesh(bamgmesh_out)
	md.private.bamg['geometry']=bamggeom(bamggeom_out)
	md.mesh = mesh2d()
	md.mesh.x=bamgmesh_out['Vertices'][:,0].copy()
	md.mesh.y=bamgmesh_out['Vertices'][:,1].copy()
	md.mesh.elements=bamgmesh_out['Triangles'][:,0:3].astype(int)
	md.mesh.edges=bamgmesh_out['IssmEdges'].astype(int)
	md.mesh.segments=bamgmesh_out['IssmSegments'][:,0:3].astype(int)
	md.mesh.segmentmarkers=bamgmesh_out['IssmSegments'][:,3].astype(int)

	#Fill in rest of fields:
	md.mesh.numberofelements=np.size(md.mesh.elements,axis=0)
	md.mesh.numberofvertices=np.size(md.mesh.x)
	md.mesh.numberofedges=np.size(md.mesh.edges,axis=0)
	md.mesh.vertexonboundary=np.zeros(md.mesh.numberofvertices,bool)
	md.mesh.vertexonboundary[md.mesh.segments[:,0:2]-1]=True
	md.mesh.elementconnectivity=md.private.bamg['mesh'].ElementConnectivity
	md.mesh.elementconnectivity[np.nonzero(np.isnan(md.mesh.elementconnectivity))]=0
	md.mesh.elementconnectivity=md.mesh.elementconnectivity.astype(int)

	#Check for orphan
	if np.any(np.logical_not(np.in1d(np.arange(1,md.mesh.numberofvertices+1),md.mesh.elements.flat))):
		raise RuntimeError("Output mesh has orphans. Decrease MaxCornerAngle to prevent outside points (ex: 0.01)")

	return md

def processgeometry(geom,tol,outline):    # {{{

	raise RuntimeError("bamg.py/processgeometry is not complete.")
	#Deal with edges
	print "Checking Edge crossing..."
	i=0
	while (i<np.size(geom.Edges,axis=0)):

		#edge counter
		i+=1

		#Get coordinates
		x1=geom.Vertices[geom.Edges[i,0],0]
		y1=geom.Vertices[geom.Edges[i,0],1]
		x2=geom.Vertices[geom.Edges[i,1],0]
		y2=geom.Vertices[geom.Edges[i,1],1]
		color1=geom.Edges[i,2]

		j=i    #test edges located AFTER i only
		while (j<np.size(geom.Edges,axis=0)):

			#edge counter
			j+=1

			#Skip if the two edges already have a vertex in common
			if any(m.ismember(geom.Edges[i,0:2],geom.Edges[j,0:2])):
				continue

			#Get coordinates
			x3=geom.Vertices[geom.Edges[j,0],0]
			y3=geom.Vertices[geom.Edges[j,0],1]
			x4=geom.Vertices[geom.Edges[j,1],0]
			y4=geom.Vertices[geom.Edges[j,1],1]
			color2=geom.Edges[j,2]

			#Check if the two edges are crossing one another
			if SegIntersect(np.array([[x1,y1],[x2,y2]]),np.array([[x3,y3],[x4,y4]])):

				#Get coordinate of intersection point (http://mathworld.wolfram.com/Line-LineIntersection.html)
				x=np.linalg.det(np.array([np.linalg.det(np.array([[x1,y1],[x2,y2]])),x1-x2],[np.linalg.det(np.array([[x3,y3],[x4,y4]])),x3-x4])/np.linalg.det(np.array([[x1-x2,y1-y2],[x3-x4,y3-y4]])))
				y=np.linalg.det(np.array([np.linalg.det(np.array([[x1,y1],[x2,y2]])),y1-y2],[np.linalg.det(np.array([[x3,y3],[x4,y4]])),y3-y4])/np.linalg.det(np.array([[x1-x2,y1-y2],[x3-x4,y3-y4]])))

				#Add vertex to the list of vertices
				geom.Vertices=np.vstack((geom.Vertices,[x,y,min(color1,color2)]))
				id=np.size(geom.Vertices,axis=0)

				#Update edges i and j
				edgei=geom.Edges[i,:].copy()
				edgej=geom.Edges[j,:].copy()
				geom.Edges[i,:]    =[edgei(0),id      ,edgei(2)]
				geom.Edges=np.vstack((geom.Edges,[id      ,edgei(1),edgei(2)]))
				geom.Edges[j,:]    =[edgej(0),id      ,edgej(2)]
				geom.Edges=np.vstack((geom.Edges,[id      ,edgej(1),edgej(2)]))

				#update current edge second tip
				x2=x
				y2=y

	#Check point outside
	print "Checking for points outside the domain..."
	i=0
	num=0
	while (i<np.size(geom.Vertices,axis=0)):

		#vertex counter
		i+=1

		#Get coordinates
		x=geom.Vertices[i,0]
		y=geom.Vertices[i,1]
		color=geom.Vertices[i,2]

		#Check that the point is inside the domain
		if color!=1 and not ContourToNodes(x,y,outline[0],1):

			#Remove points from list of Vertices
			num+=1
			geom.Vertices[i,:]=[]

			#update edges
			posedges=np.nonzero(geom.Edges==i)
			geom.Edges[posedges[0],:]=[]
			posedges=np.nonzero(geom.Edges>i)
			geom.Edges[posedges]=geom.Edges[posedges]-1

			#update counter
			i-=1

	if num:
		print "WARNING: %d points outside the domain outline have been removed" % num

	"""
	%Check point spacing
	if ~isnan(tol),
		disp('Checking point spacing...');
		i=0;
		while (i<size(geom.Vertices,1)),

			%vertex counter
			i=i+1;

			%Get coordinates
			x1=geom.Vertices(i,1);
			y1=geom.Vertices(i,2);

			j=i; %test edges located AFTER i only
			while (j<size(geom.Vertices,1)),

				%vertex counter
				j=j+1;

				%Get coordinates
				x2=geom.Vertices(j,1);
				y2=geom.Vertices(j,2);

				%Check whether the two vertices are too close
				if ((x2-x1)**2+(y2-y1)**2<tol**2)

					%Remove points from list of Vertices
					geom.Vertices(j,:)=[];

					%update edges
					posedges=find(m.ismember(geom.Edges,j));
					geom.Edges(posedges)=i;
					posedges=find(geom.Edges>j);
					geom.Edges(posedges)=geom.Edges(posedges)-1;

					%update counter
					j=j-1;

				end
			end
		end
	end
	%remove empty edges
	geom.Edges(find(geom.Edges(:,1)==geom.Edges(:,2)),:)=[];
	"""
	return geom
# }}}

