from issm.loadvars import loadvars
from whichdb import whichdb
from netCDF4 import Dataset

def loadmodel(path):
	"""
	LOADMODEL - load a model using built-in load module

	   check that model prototype has not changed. if so, adapt to new model prototype.
	
	   Usage:
	      md=loadmodel(path)
	"""

	#check existence of database (independent of file extension!)
	if whichdb(path):
		#do nothing
		pass
	else:
		try:
			NCFile=Dataset(path,mode='r')
			NCFile.close()
			pass
		except RuntimeError:
			raise IOError("loadmodel error message: file '%s' does not exist" % path)
		#	try:
	#recover model on file and name it md
	struc=loadvars(path)
	name=[key for key in struc.iterkeys()]
	if len(name)>1:
		raise IOError("loadmodel error message: file '%s' contains several variables. Only one model should be present." % path)

	md=struc[name[0]]
	return md
