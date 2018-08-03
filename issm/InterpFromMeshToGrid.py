from InterpFromMeshToGrid_python import InterpFromMeshToGrid_python

def InterpFromMeshToGrid(index,x,y,data,xmin,ymax,xposting,yposting,nlines,ncols,default_value):
	"""
	INTERPFROMMESHTOGRID - Interpolation of a data defined on a mesh onto a grid

		This function is a multi-threaded mex file that interpolates a field defined
		on a triangular mesh onto a regular grid

		index,x,y:	delaunay triangulation defining the mesh
		meshdata:	vertex values of data to be interpolated

		xmin,ymax,posting,nlines,ncols:	parameters that define the grid
		default_value:	value of points located out of the mesh
	"""
	# Call mex module
	x_m,y_m,griddata=InterpFromMeshToGrid_python(index,x,y,data,xmin,ymax,xposting,yposting,nlines,ncols,default_value)
	# Return
	return x_m,y_m,griddate
