from WriteData import WriteData

def marshall(md):
	"""
	MARSHALL - outputs a compatible binary file from @model md, for certain solution type.

	   The routine creates a compatible binary file from @model md
	   This binary file will be used for parallel runs in JPL-package

	   Usage:
	      marshall(md)
	"""

	print "marshalling file '%s.bin'." % md.miscellaneous.name

	#open file for binary writing
	try:
		fid=open(md.miscellaneous.name+'.bin','wb')
	except IOError as e:
		raise IOError("marshall error message: could not open '%s.bin' file for binary writing." % md.miscellaneous.name)

	#Go through all model fields: check that it is a class and call checkconsistency
	fields=vars(md)

#	for field in fields.iterkeys():
	for field in md.properties():

		#Some properties do not need to be marshalled
		if field in ['results','radaroverlay','toolkits','cluster','private']:
			continue

		#Check that current field is an object
		if not hasattr(getattr(md,field),'marshall'):
			raise TypeError("field '%s' is not an object." % field)

		#Marshall current object
		#print "marshalling %s ..." % field
		exec("md.{}.marshall('md.{}',md,fid)".format(field,field))

	#Last, write "md.EOF" to make sure that the binary file is not corrupt
	WriteData(fid,'XXX','name','md.EOF','data',True,'format','Boolean');

	#close file
	try:
		fid.close()
	except IOError as e:
		raise IOError("marshall error message: could not close file '%s.bin'." % md.miscellaneous.name)

