from TriMesh_python import TriMesh_python

def TriMesh(domainoutlinefilename,rifts,mesh_area):
	"""
	TRIMESH - Mesh a domain using an .exp file

	   Usage: 
			[index,x,y,segments,segmentmarkers]=TriMesh(domainoutlinefilename,rifts,mesh_area); 

	   index,x,y: defines a triangulation 
		segments: An array made of exterior segments to the mesh domain outline 
		segmentmarkers: An array flagging each segment

	   domainoutlinefilename: an Argus domain outline file
		mesh_area: The maximum area desired for any element of the resulting mesh
	"""
	# Call mex module
	index,x,y,segments,segmentmarkers=TriMesh_python(domainoutlinefilename,rifts,mesh_area)
	# Return
	return index,x,y,segments,segmentmarkers

