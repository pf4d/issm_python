import numpy as np

def expwrite(contours,filename):
	"""
	EXPWRITE - write an Argus file from a dictionary given in input

	   This routine writes an Argus file from a dict containing the fields:
	   x and y of the coordinates of the points.
	   The first argument is the list containing the points coordinates 
	   and the second one the file to be written.

	   Usage:
	      expwrite(contours,filename)

	   Example:
	      expwrite(coordstruct,'domainoutline.exp')

	   See also EXPDOC, EXPREAD, EXPWRITEASVERTICES
	"""

	fid=open(filename,'w')
	for x,y in zip(contours['x'],contours['y']):
		#if np.size(contour['x'])!=np.size(contour['y']):
		if len(x)!=len(y):
			raise RuntimeError("contours x and y coordinates must be of identical size")
		if 'name' in contours:
			fid.write("%s%s\n" % ('## Name:',contours['name']))
		else:
			fid.write("%s%s\n" % ('## Name:',filename))
   
		#Add density if it's not there FIXME what is this ever used for?
		#if 'density' not in contours:
		#	contours['density']=1
		density=1

		fid.write("%s\n" % '## Icon:0')
		fid.write("%s\n" % '# Points Count Value')
		#fid.write("%i %f\n" % (np.size(contour['x']),contour['density']))
		fid.write("%i %f\n" % (np.size(x),density))
		fid.write("%s\n" % '# X pos Y pos')
		#for x,y in zip(contour['x'],contour['y']):
		for xi,yi in zip(x,y):
			fid.write("%10.10f %10.10f\n" % (xi,yi))
		fid.write("\n")

	fid.close()

