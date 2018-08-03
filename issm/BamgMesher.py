from BamgMesher_python import BamgMesher_python

def BamgMesher(bamgmesh,bamggeom,bamgoptions):
	"""
	BAMGMESHER

	Usage:
		bamgmesh,bamggeom = BamgMesher(bamgmesh,bamggeom,bamgoptions);

	bamgmesh: input bamg mesh
	bamggeom: input bamg geometry for the mesh
	bamgoptions: options for the bamg mesh
	"""
	
	#Call mex module
	bamgmesh, bamggeom = BamgMesher_python(bamgmesh, bamggeom, bamgoptions)

	#return
	return bamgmesh, bamggeom
