import numpy as np
import struct
from issm.pairoptions import pairoptions
import issm.MatlabFuncs as m

def WriteData(fid,prefix,*args):
	"""
	WRITEDATA - write model field in binary file
 
	   Usage:
	      WriteData(fid,varargin)
	"""

	#process options
	options=pairoptions(*args)

	#Get data properties
	if options.exist('object'):
		#This is an object field, construct enum and data
		obj       = options.getfieldvalue('object')
		fieldname = options.getfieldvalue('fieldname')
		classname = options.getfieldvalue('class',str(type(obj)).rsplit('.')[-1].split("'")[0])
		name      = options.getfieldvalue('name',prefix+'.'+fieldname);
		if options.exist('data'):
			data = options.getfieldvalue('data')
		else:
			data      = getattr(obj,fieldname)
	else:
		#No processing required
		data = options.getfieldvalue('data')
		name = options.getfieldvalue('name')

	format  = options.getfieldvalue('format')
	mattype = options.getfieldvalue('mattype',0)    #only required for matrices
	timeserieslength = options.getfieldvalue('timeserieslength',-1)

	#Process sparse matrices
#	if issparse(data),
#		data=full(data);
#	end

	#Scale data if necesarry
	if options.exist('scale'):
		scale = options.getfieldvalue('scale')
		if np.size(data) > 1 :
			if np.size(data,0)==timeserieslength:
				data=np.array(data)
				data[0:-1,:] = scale*data[0:-1,:]
			else:
				data  = scale*data
		else:
			data  = scale*data
	if np.size(data) > 1 :
		if np.size(data,0)==timeserieslength:
			yts = options.getfieldvalue('yts')
			data[-1,:] = yts*data[-1,:]

	#Step 1: write the enum to identify this record uniquely
	fid.write(struct.pack('i',len(name)))
	fid.write(struct.pack('%ds' % len(name),name)) 

	#Step 2: write the data itself.
	if   m.strcmpi(format,'Boolean'):    # {{{
#		if len(data) !=1:
#			raise ValueError('field %s cannot be marshalled as it has more than one element!' % name[0])

		#first write length of record
		fid.write(struct.pack('i',4+4))  #1 bool (disguised as an int)+code

		#write data code: 
		fid.write(struct.pack('i',FormatToCode(format))) 

		#now write integer
		fid.write(struct.pack('i',int(data)))  #send an int, not easy to send a bool
		# }}}

	elif m.strcmpi(format,'Integer'):    # {{{
#		if len(data) !=1:
#			raise ValueError('field %s cannot be marshalled as it has more than one element!' % name[0])

		#first write length of record
		fid.write(struct.pack('i',4+4))  #1 integer + code

		#write data code: 
		fid.write(struct.pack('i',FormatToCode(format))) 

		#now write integer
		fid.write(struct.pack('i',data)) 
		# }}}

	elif m.strcmpi(format,'Double'):    # {{{
#		if len(data) !=1:
#			raise ValueError('field %s cannot be marshalled as it has more than one element!' % name[0])

		#first write length of record
		fid.write(struct.pack('i',8+4))  #1 double+code

		#write data code: 
		fid.write(struct.pack('i',FormatToCode(format))) 

		#now write double
		fid.write(struct.pack('d',data)) 
		# }}}

	elif m.strcmpi(format,'String'):    # {{{
		#first write length of record
		fid.write(struct.pack('i',len(data)+4+4))  #string + string size + code

		#write data code: 
		fid.write(struct.pack('i',FormatToCode(format))) 

		#now write string
		fid.write(struct.pack('i',len(data))) 
		fid.write(struct.pack('%ds' % len(data),data)) 
		# }}}

	elif m.strcmpi(format,'BooleanMat'):    # {{{

		if   isinstance(data,bool):
			data=np.array([data])
		elif isinstance(data,(list,tuple)):
			data=np.array(data).reshape(-1,)
		if np.ndim(data) == 1:
			if np.size(data):
				data=data.reshape(np.size(data),)
			else:
				data=data.reshape(0,0)

		#Get size
		s=data.shape
		#if matrix = NaN, then do not write anything
		if np.ndim(data)==2 and np.product(s)==1 and np.all(np.isnan(data)):
			s=(0,0)

		#first write length of record
		fid.write(struct.pack('i',4+4+8*np.product(s)+4+4))    #2 integers (32 bits) + the double matrix + code + matrix type

		#write data code and matrix type: 
		fid.write(struct.pack('i',FormatToCode(format))) 
		fid.write(struct.pack('i',mattype))

		#now write matrix
		if np.ndim(data)==1:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',1)) 
			for i in xrange(s[0]):
				fid.write(struct.pack('d',float(data[i])))    #get to the "c" convention, hence the transpose
		else:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',s[1])) 
			for i in xrange(s[0]):
				for j in xrange(s[1]):
					fid.write(struct.pack('d',float(data[i][j])))    #get to the "c" convention, hence the transpose
		# }}}

	elif m.strcmpi(format,'IntMat'):    # {{{

		if   isinstance(data,(int,long)):
			data=np.array([data])
		elif isinstance(data,(list,tuple)):
			data=np.array(data).reshape(-1,)
		if np.ndim(data) == 1:
			if np.size(data):
				data=data.reshape(np.size(data),)
			else:
				data=data.reshape(0,0)

		#Get size
		s=data.shape
		#if matrix = NaN, then do not write anything
		if np.ndim(data)==2 and np.product(s)==1 and np.all(np.isnan(data)):
			s=(0,0)

		#first write length of record
		fid.write(struct.pack('i',4+4+8*np.product(s)+4+4))    #2 integers (32 bits) + the double matrix + code + matrix type

		#write data code and matrix type: 
		fid.write(struct.pack('i',FormatToCode(format))) 
		fid.write(struct.pack('i',mattype))

		#now write matrix
		if np.ndim(data) == 1:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',1)) 
			for i in xrange(s[0]):
				fid.write(struct.pack('d',float(data[i])))    #get to the "c" convention, hence the transpose
		else:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',s[1])) 
			for i in xrange(s[0]):
				for j in xrange(s[1]):
					fid.write(struct.pack('d',float(data[i][j])))    #get to the "c" convention, hence the transpose
		# }}}

	elif m.strcmpi(format,'DoubleMat'):    # {{{

		if   isinstance(data,(bool,int,long,float)):
			data=np.array([data])
		elif isinstance(data,(list,tuple)):
			data=np.array(data).reshape(-1,)
		if np.ndim(data) == 1:
			if np.size(data):
				data=data.reshape(np.size(data),)
			else:
				data=data.reshape(0,0)

		#Get size
		s=data.shape
		#if matrix = NaN, then do not write anything
		if np.ndim(data)==1 and np.product(s)==1 and np.all(np.isnan(data)):
			s=(0,0)

		#first write length of record
		recordlength=4+4+8*np.product(s)+4+4; #2 integers (32 bits) + the double matrix + code + matrix type
		if recordlength > 4**31 :
			raise ValueError('field %s cannot be marshalled because it is larger than 4^31 bytes!' % enum)

		fid.write(struct.pack('i',recordlength))  #2 integers (32 bits) + the double matrix + code + matrix type

		#write data code and matrix type: 
		fid.write(struct.pack('i',FormatToCode(format))) 
		fid.write(struct.pack('i',mattype))

		#now write matrix
		if np.ndim(data) == 1:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',1)) 
			for i in xrange(s[0]):
				fid.write(struct.pack('d',float(data[i])))    #get to the "c" convention, hence the transpose
		else:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',s[1])) 
			for i in xrange(s[0]):
				for j in xrange(s[1]):
					fid.write(struct.pack('d',float(data[i][j])))    #get to the "c" convention, hence the transpose
		# }}}

	elif m.strcmpi(format,'CompressedMat'):    # {{{

		if   isinstance(data,(bool,int,long,float)):
			data=np.array([data])
		elif isinstance(data,(list,tuple)):
			data=np.array(data).reshape(-1,)
		if np.ndim(data) == 1:
			if np.size(data):
				data=data.reshape(np.size(data),)
			else:
				data=data.reshape(0,0)

		#Get size
		s=data.shape
		if np.ndim(data) == 1:
		   n2=1
		else:
			n2=s[1]

		#if matrix = NaN, then do not write anything
		if np.ndim(data)==1 and np.product(s)==1 and np.all(np.isnan(data)):
			s=(0,0)
			n2=0

		#first write length of record
		recordlength=4+4+8+8+1*(s[0]-1)*n2+8*n2+4+4 #2 integers (32 bits) + the matrix + code + matrix type
		if recordlength > 4**31 :
			raise ValueError('field %s cannot be marshalled because it is larger than 4^31 bytes!' % enum)

		fid.write(struct.pack('i',recordlength))  #2 integers (32 bits) + the matrix + code + matrix type

		#write data code and matrix type: 
		fid.write(struct.pack('i',FormatToCode(format))) 
		fid.write(struct.pack('i',mattype))

		#Write offset and range
		A = data[0:s[0]-1]
		offsetA = A.min()
		rangeA = A.max() - offsetA

		if rangeA == 0:
			A = A*0 
		else:
			A = (A-offsetA)/rangeA*255. 
		
		#now write matrix
		if np.ndim(data) == 1:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',1)) 
			fid.write(struct.pack('d',float(offsetA)))
			fid.write(struct.pack('d',float(rangeA)))
			for i in xrange(s[0]-1):
				fid.write(struct.pack('B',int(A[i])))

			fid.write(struct.pack('d',float(data[s[0]-1])))    #get to the "c" convention, hence the transpose

		elif np.product(s) > 0:
			fid.write(struct.pack('i',s[0])) 
			fid.write(struct.pack('i',s[1])) 
			fid.write(struct.pack('d',float(offsetA)))
			fid.write(struct.pack('d',float(rangeA)))
			for i in xrange(s[0]-1):
				for j in xrange(s[1]):
					fid.write(struct.pack('B',int(A[i][j])))    #get to the "c" convention, hence the transpose

			for j in xrange(s[1]):
				fid.write(struct.pack('d',float(data[s[0]-1][j])))

		# }}}

	elif m.strcmpi(format,'MatArray'):    # {{{

		#first get length of record
		recordlength=4+4    #number of records + code
		for matrix in data:
			if   isinstance(matrix,(bool,int,long,float)):
				matrix=np.array([matrix])
			elif isinstance(matrix,(list,tuple)):
				matrix=np.array(matrix).reshape(-1,)
			if np.ndim(matrix) == 1:
				if np.size(matrix):
					matrix=matrix.reshape(np.size(matrix),)
				else:
					matrix=matrix.reshape(0,0)

			s=matrix.shape
			recordlength+=4*2+np.product(s)*8    #row and col of matrix + matrix of doubles

		#write length of record
		fid.write(struct.pack('i',recordlength)) 

		#write data code: 
		fid.write(struct.pack('i',FormatToCode(format))) 

		#write data, first number of records
		fid.write(struct.pack('i',len(data))) 

		#write each matrix: 
		for matrix in data:
			if   isinstance(matrix,(bool,int,long,float)):
				matrix=np.array([matrix])
			elif isinstance(matrix,(list,tuple)):
				matrix=np.array(matrix).reshape(-1,)
			if np.ndim(matrix) == 1:
				matrix=matrix.reshape(np.size(matrix),)

			s=matrix.shape
			if np.ndim(data) == 1:
				fid.write(struct.pack('i',s[0])) 
				fid.write(struct.pack('i',1)) 
				for i in xrange(s[0]):
					fid.write(struct.pack('d',float(matrix[i])))    #get to the "c" convention, hence the transpose
			else:
				fid.write(struct.pack('i',s[0])) 
				fid.write(struct.pack('i',s[1])) 
				for i in xrange(s[0]):
					for j in xrange(s[1]):
						fid.write(struct.pack('d',float(matrix[i][j])))
		# }}}

	elif m.strcmpi(format,'StringArray'):    # {{{

		#first get length of record
		recordlength=4+4    #for length of array + code
		for string in data:
			recordlength+=4+len(string)    #for each string

		#write length of record
		fid.write(struct.pack('i',recordlength)) 

		#write data code: 
		fid.write(struct.pack('i',FormatToCode(format))) 

		#now write length of string array
		fid.write(struct.pack('i',len(data))) 

		#now write the strings
		for string in data:
			fid.write(struct.pack('i',len(string))) 
			fid.write(struct.pack('%ds' % len(string),string)) 
		# }}}

	else:    # {{{
		raise TypeError('WriteData error message: data type: %d not supported yet! (%s)' % (format,enum))
	# }}}

def FormatToCode(format): # {{{
	"""
	This routine takes the format string, and hardcodes it into an integer, which 
	is passed along the record, in order to identify the nature of the dataset being 
	sent.
	"""

	if   m.strcmpi(format,'Boolean'):
		code=1
	elif m.strcmpi(format,'Integer'):
		code=2
	elif m.strcmpi(format,'Double'):
		code=3
	elif m.strcmpi(format,'String'):
		code=4
	elif m.strcmpi(format,'BooleanMat'):
		code=5
	elif m.strcmpi(format,'IntMat'):
		code=6
	elif m.strcmpi(format,'DoubleMat'):
		code=7
	elif m.strcmpi(format,'MatArray'):
		code=8
	elif m.strcmpi(format,'StringArray'):
		code=9
	elif m.strcmpi(format,'CompressedMat'):
		code=10
	else:
		raise InputError('FormatToCode error message: data type not supported yet!')

	return code
# }}}
