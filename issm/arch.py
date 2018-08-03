import numpy as np
import math
import struct
import sys
import os
from collections import OrderedDict

def archwrite(filename,*args): # {{{
	"""
	ARCHWRITE - Write data to a field, given the file name, field name, and data.

		Usage:
			archwrite('archive101.arch','variable_name',data);
	"""
	nargs=len(args);
	if nargs % 2 != 0 :
		raise ValueError('Incorrect number of arguments.')
	# open file
	try:
		if not os.path.isfile(filename):
			fid=open(filename,'wb')
		else:
			fid=open(filename,'ab')
	except IOError as e:
		raise IOError("archwrite error: could not open '%s' to write to." % filename)

	nfields=len(args)/2
	# generate data to write
	for i in range(nfields):
		# write field name
		name=args[2*i]
		write_field_name(fid,name)
		
		# write data associated with field name
		data=args[2*i+1]
		code=format_archive_code(data)
		if code==1:
			raise ValueError("archwrite : error writing data, string should not be written as field data")
		elif code==2:
			write_scalar(fid,data)
		elif code==3:
			write_vector(fid,data)
		else:
			raise ValueError("archwrite : error writing data, invalid code entered '%d'" % code)
	
	fid.close()

# }}}
def archread(filename,fieldname): # {{{
	"""
	ARCHREAD - Given an arch file name, and a field name, find and return the data
					associated with that field name.
		Usage:
			archread('archive101.arch','field_var_1')
	"""
	try:
		if os.path.isfile(filename):
			fid=open(filename,'rb')
		else:
			raise IOError("archread error : file '%s' does not exist" % filename)
	except IOError as e:
		raise IOError("archread error : could not open file '%s' to read from" % filename)
	
	archive_results=[]

	# read first result
	result=read_field(fid)
	while result:
		if fieldname == result['field_name']:
			# found the data we wanted
			archive_results=result['data']; # we only want the data
			break
		
		# read next result
		result=read_field(fid)
	
	# close file
	fid.close()
	
	return archive_results
# }}}
def archdisp(filename): # {{{
	"""
	ARCHDISP - Given an arch filename, display the contents of that file

		Usage:
			archdisp('archive101.arch')
	"""
	try:
		if os.path.isfile(filename):
			fid=open(filename,'rb')
		else:
			raise IOError("archread error : file '%s' does not exist" % filename)
	except IOError as e:
		raise IOError("archread error : could not open file '%s' to read from" % filename)
	
	print 'Source file: '
	print '\t{0}'.format(filename)
	print 'Variables: '

	result=read_field(fid)
	while result:
		print '\t{0}'.format(result['field_name'])
		print '\t\tSize:\t\t{0}'.format(result['size'])
		print '\t\tDatatype:\t{0}'.format(result['data_type'])
		# go to next result
		result=read_field(fid)
	
	# close file
	fid.close()

# }}}

# Helper functions 
def write_field_name(fid,data): # {{{
	"""
	Routine to write field name (variable name) to an archive file.
	"""
	# write the length of the record
	# length to write + string size (len) + format code
	reclen=len(data)+4+4
	fid.write(struct.pack('>i',reclen))
	
	# write format code
	code=format_archive_code(data);
	if code != 1:
		raise TypeError("archwrite : error writing field name, expected string, but got %s" % type(data))
	fid.write(struct.pack('>i',1))

	# write string length, and then the string
	fid.write(struct.pack('>i',len(data)))
	fid.write(struct.pack('>%ds' % len(data),data))
# }}}
def write_scalar(fid,data): # {{{
	"""
	Procedure to write a double to an arch file pointed to by fid
	"""
	# write length of record
	# double (8 bytes) + format code (4 bytes)
	reclen=8+4
	fid.write(struct.pack('>i',reclen))

	# write the format code (2 for scalar)
	fid.write(struct.pack('>i',2))
	
	# write the double
	fid.write(struct.pack('>d',data))

# }}}
def write_vector(fid,data): # {{{
	"""
	Procedure to write a np.array to an arch file
	"""
	# Make sure our vector is the correct shape.
	# Reshape it into a row vector if it is not correct.
	if isinstance(data,(bool,int,long,float)):
		data=np.array([data])
	elif isinstance(data,(list,tuple)):
		data=np.array(data).reshape(-1,)
	
	if np.ndim(data) == 1:
		if np.size(data):
			data=data.reshape(np.size(data),)
		else:
			data=data.reshape(0,0)
	
	# get size of data
	sz=data.shape

	# write length of record
	# format code + row size + col size + (double size * row amt * col amt)
	reclen=4+4+4+8*sz[0]*sz[1]
	# make sure we can fit data into file
	if reclen>2**31:
		raise ValueError("archwrite error : can not write vector to binary file because it is too large")
	fid.write(struct.pack('>i',reclen))
	
	# write format code
	fid.write(struct.pack('>i',3))

	# write vector
	fid.write(struct.pack('>i',sz[0]))
	fid.write(struct.pack('>i',sz[1]))
	for i in xrange(sz[0]):
		for j in xrange(sz[1]):
			fid.write(struct.pack('>d',float(data[i][j])))

# }}}

def read_field(fid): # {{{
	"""
	Procedure to read a field and return a results list with the following attributes:
	result['field_name']	-> the name of the variable that was just read
	result['size']			-> size (dimensions) of the variable just read
	result['data_type']	-> the type of data that was just read
	result['data']			-> the actual data
	"""

	try:
		# first, read the string
		reclen=struct.unpack('>i',fid.read(struct.calcsize('>i')))[0]
		check_name=struct.unpack('>i',fid.read(struct.calcsize('>i')))[0]
		if check_name != 1:
			raise ValueError('archread error : a string was not present at the start of the arch file')
		namelen=struct.unpack('>i',fid.read(struct.calcsize('>i')))[0]
		fieldname=struct.unpack('>%ds' % namelen,fid.read(namelen))[0]
		
		# then, read the data
		datalen=struct.unpack('>i',fid.read(struct.calcsize('>i')))[0]
		data_type=struct.unpack('>i',fid.read(struct.calcsize('>i')))[0]

		if data_type==2:
			# unpack scalar
			data=struct.unpack('>d',fid.read(struct.calcsize('>d')))[0]
		elif data_type==3:
			rows=struct.unpack('>i',fid.read(struct.calcsize('>i')))[0]
			cols=struct.unpack('>i',fid.read(struct.calcsize('>i')))[0]
			raw_data=np.zeros(shape=(rows,cols),dtype=float)
			for i in xrange(rows):
				raw_data[i,:]=struct.unpack('>%dd' % cols,fid.read(cols*struct.calcsize('>d')))
			# The matrix will be unpacked in order and will be filled left -> right by column
			# We need to reshape and transpose the matrix so it can be read correctly
			data=raw_data.reshape(raw_data.shape[::-1]).T
		else:
			raise TypeError("Cannot read data type %d" % data_type)
			
		# give additional data to user
		if data_type==2:
			data_size='1x1'
			data_type_str='double'
		elif data_type==3:
			data_size='{0}x{1}'.format(rows,cols)
			data_type_str='vector/matrix'

		result=OrderedDict()
		result['field_name']=fieldname
		result['size']=data_size
		result['data_type']=data_type_str
		result['data']=data

	except struct.error as e:
		result=None

	return result
# }}}

def format_archive_code(format): # {{{
	"""
	Given a variable, determine it's type and return
	an integer value:

	1 : string
	2 : double (scalar)
	3 : vector or matrix (of type double)

	"""
	if isinstance(format,basestring):
		code=1
	elif format.shape[0] == 1 and format.shape[1] == 1:
		code=2
	elif isinstance(format,(list,tuple,np.ndarray)):
		code=3
	else:
		raise TypeError("archwrite error: data type '%s' is not valid." % type(format))
	return code
# }}}
