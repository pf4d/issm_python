import struct
import numpy as np
from collections import OrderedDict
import issm.results as resultsclass

def parseresultsfromdisk(md,filename,iosplit):
	if iosplit:
		saveres=parseresultsfromdiskiosplit(md,filename)
	else:
		saveres=parseresultsfromdiskioserial(md,filename)

	return saveres

def parseresultsfromdiskioserial(md,filename):    # {{{
	#Open file
	try:
		fid=open(filename,'rb')
	except IOError as e:
		raise IOError("loadresultsfromdisk error message: could not open '%s' for binary reading." % filename)

	#initialize results: 
	saveres=[]

	#Read fields until the end of the file.
	loadres=ReadData(fid,md)

	counter=0
	check_nomoresteps=0
	step=loadres['step']

	while loadres:
		#check that the new result does not add a step, which would be an error: 
		if check_nomoresteps:
			if loadres['step']>=1:
				raise TypeError("parsing results for a steady-state core, which incorporates transient results!")

		#Check step, increase counter if this is a new step
		if(step!=loadres['step'] and loadres['step']>1):
			counter = counter + 1
			step    = loadres['step']

		#Add result
		if loadres['step']==0:
			#if we have a step = 0, this is a steady state solution, don't expect more steps. 
			index = 0;
			check_nomoresteps=1
		elif loadres['step']==1:
			index = 0
		else:
			index = counter;
		
		if index > len(saveres)-1:
			for i in xrange(len(saveres)-1,index-1):
				saveres.append(None)
			saveres.append(resultsclass())
		elif saveres[index] is None:
			saveres[index]=resultsclass()
			
		#Get time and step
		if loadres['step'] != -9999.:
			saveres[index].__dict__['step']=loadres['step']
		if loadres['time'] != -9999.:
			saveres[index].__dict__['time']=loadres['time']

		#Add result
		saveres[index].__dict__[loadres['fieldname']]=loadres['field']

		#read next result
		loadres=ReadData(fid,md)

	fid.close()

	return saveres
	# }}}
def parseresultsfromdiskiosplit(md,filename):    # {{{

	#Open file
	try:
		fid=open(filename,'rb')
	except IOError as e:
		raise IOError("loadresultsfromdisk error message: could not open '%s' for binary reading." % filename)

	saveres=[]

	#if we have done split I/O, ie, we have results that are fragmented across patches, 
	#do a first pass, and figure out the structure of results
	loadres=ReadDataDimensions(fid)
	while loadres:

		#Get time and step
		if loadres['step'] > len(saveres):
			for i in xrange(len(saveres),loadres['step']-1):
				saveres.append(None)
			saveres.append(resultsclass())
		setattr(saveres[loadres['step']-1],'step',loadres['step'])
		setattr(saveres[loadres['step']-1],'time',loadres['time']) 

		#Add result
		setattr(saveres[loadres['step']-1],loadres['fieldname'],float('NaN'))

		#read next result
		loadres=ReadDataDimensions(fid)

	#do a second pass, and figure out the size of the patches
	fid.seek(0)    #rewind
	loadres=ReadDataDimensions(fid)
	while loadres:

		#read next result
		loadres=ReadDataDimensions(fid)

	#third pass, this time to read the real information
	fid.seek(0)    #rewind
	loadres=ReadData(fid,md)
	while loadres:

		#Get time and step
		if loadres['step']> len(saveres):
			for i in xrange(len(saveres),loadres['step']-1):
				saveres.append(None)
			saveres.append(saveresclass.saveres())
		setattr(saveres[loadres['step']-1],'step',loadres['step'])
		setattr(saveres[loadres['step']-1],'time',loadres['time']) 

		#Add result
		setattr(saveres[loadres['step']-1],loadres['fieldname'],loadres['field'])

		#read next result
		loadres=ReadData(fid,md)

	#close file
	fid.close()

	return saveres
	# }}}
def ReadData(fid,md):    # {{{
	"""
	READDATA - ...
	 
	    Usage:
	       field=ReadData(fid,md)
	"""

	#read field
	try:
		length=struct.unpack('i',fid.read(struct.calcsize('i')))[0]

		fieldname=struct.unpack('%ds' % length,fid.read(length))[0][:-1]
		time=struct.unpack('d',fid.read(struct.calcsize('d')))[0]
		step=struct.unpack('i',fid.read(struct.calcsize('i')))[0]

		type=struct.unpack('i',fid.read(struct.calcsize('i')))[0]
		M=struct.unpack('i',fid.read(struct.calcsize('i')))[0]
		if   type==1:
			field=np.array(struct.unpack('%dd' % M,fid.read(M*struct.calcsize('d'))),dtype=float)
		elif type==2:
			field=struct.unpack('%ds' % M,fid.read(M))[0][:-1]
		elif type==3:
			N=struct.unpack('i',fid.read(struct.calcsize('i')))[0]
#			field=transpose(fread(fid,[N M],'double'));
			field=np.zeros(shape=(M,N),dtype=float)
			for i in xrange(M):
				field[i,:]=struct.unpack('%dd' % N,fid.read(N*struct.calcsize('d')))
		elif type==4:
			N=struct.unpack('i',fid.read(struct.calcsize('i')))[0]
#			field=transpose(fread(fid,[N M],'int'));
			field=np.zeros(shape=(M,N),dtype=int)
			for i in xrange(M):
				field[i,:]=struct.unpack('%ii' % N,fid.read(N*struct.calcsize('i')))
		else:
			raise TypeError("cannot read data of type %d" % type)

		#Process units here FIXME: this should not be done here!
		yts=md.constants.yts
		if fieldname=='BalancethicknessThickeningRate':
			field = field*yts
		elif fieldname=='Time':
			field = field/yts
		elif fieldname=='HydrologyWaterVx':
			field = field*yts
		elif fieldname=='HydrologyWaterVy':
			field = field*yts
		elif fieldname=='Vx':
			field = field*yts
		elif fieldname=='Vy':
			field = field*yts
		elif fieldname=='Vz':
			field = field*yts
		elif fieldname=='Vel':
			field = field*yts
		elif fieldname=='BasalforcingsGroundediceMeltingRate':
			field = field*yts
		elif fieldname=='TotalFloatingBmb':
			field = field/10.**12.*yts #(GigaTon/year)
		elif fieldname=='TotalGroundedBmb':
			field = field/10.**12.*yts #(GigaTon/year)
		elif fieldname=='TotalSmb':
			field = field/10.**12.*yts #(GigaTon/year)
		elif fieldname=='SmbMassBalance':
			field = field*yts
		elif fieldname=='CalvingCalvingrate':
			field = field*yts

		saveres=OrderedDict()
		saveres['fieldname']=fieldname
		saveres['time']=time
		saveres['step']=step
		saveres['field']=field

	except struct.error as e:
		saveres=None

	return saveres
	# }}}
def ReadDataDimensions(fid):    # {{{
	"""
	READDATADIMENSIONS - read data dimensions, step and time, but not the data itself.
	 
	    Usage:
	       field=ReadDataDimensions(fid)
	"""

	#read field
	try:
		length=struct.unpack('i',fid.read(struct.calcsize('i')))[0]

		fieldname=struct.unpack('%ds' % length,fid.read(length))[0][:-1]
		time=struct.unpack('d',fid.read(struct.calcsize('d')))[0]
		step=struct.unpack('i',fid.read(struct.calcsize('i')))[0]

		type=struct.unpack('i',fid.read(struct.calcsize('i')))[0]
		M=struct.unpack('i',fid.read(struct.calcsize('i')))[0]
		N=1    #default
		if   type==1:
			fid.seek(M*8,1)
		elif type==2:
			fid.seek(M,1)
		elif type==3:
			N=struct.unpack('i',fid.read(struct.calcsize('i')))[0]
			fid.seek(N*M*8,1)
		else:
			raise TypeError("cannot read data of type %d" % type)

		saveres=OrderedDict()
		saveres['fieldname']=fieldname
		saveres['time']=time
		saveres['step']=step
		saveres['M']=M
		saveres['N']=N

	except struct.error as e:
		saveres=None

	return saveres
	# }}}
