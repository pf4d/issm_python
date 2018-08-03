import numpy as np
import os
from issm.pairoptions import pairoptions
import issm.MatlabFuncs as m

def checkfield(md,*args):
	"""
	CHECKFIELD - check field consistency

	   Used to check model consistency.,
	   Requires: 
	   'field' or 'fieldname' option. If 'fieldname' is provided, it will retrieve it from the model md. (md.(fieldname)) 
             If 'field' is provided, it will assume the argument following 'field' is a numeric array.

	   Available options:
	      - NaN: 1 if check that there is no NaN
	      - size: [lines cols], NaN for non checked dimensions
	      - >:  greater than provided value
	      - >=: greater or equal to provided value
	      - <:  smallerthan provided value
	      - <=: smaller or equal to provided value
	      - < vec:  smallerthan provided values on each vertex
	      - timeseries: 1 if check time series consistency (size and time)
	      - values: cell of strings or vector of acceptable values
	      - numel: list of acceptable number of elements
	      - cell: 1 if check that is cell
	      - empty: 1 if check that non empty
	      - message: overloaded error message

	   Usage:
	      md = checkfield(md,fieldname,options);
	"""

	#get options
	options=pairoptions(*args)

	#get field from model
	if options.exist('field'):
		field=options.getfieldvalue('field')
		fieldname=options.getfieldvalue('fieldname','no fieldname')
	else:
		fieldname=options.getfieldvalue('fieldname') 
		exec("field=md.{}".format(fieldname))

	if isinstance(field,(bool,int,long,float)):
		field=np.array([field])

	#check empty
	if options.exist('empty'):
		if not field:
			md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' is empty" % fieldname))

	#Check size
	if options.exist('size'):
		fieldsize=options.getfieldvalue('size')
		if len(fieldsize) == 1:
			if np.isnan(fieldsize[0]):
				pass
			elif np.ndim(field)==1:
				if not np.size(field)==fieldsize[0]:
					md = md.checkmessage(options.getfieldvalue('message',"field {} size should be {}".format(fieldname,fieldsize[0])))
			else:
				try:
					 exec("md.{}=field[:,0]".format(fieldname))
					 print('{} had a bad dimension, we fixed it but you should check it'.format(fieldname))
				except IndexError:
					md = md.checkmessage(options.getfieldvalue('message',"field {} should have {} dimension".format(fieldname,len(fieldsize))))
		elif len(fieldsize) == 2:
			if   np.isnan(fieldsize[0]):
				if not np.size(field,1)==fieldsize[1]:
					md = md.checkmessage(options.getfieldvalue('message',"field '%s' should have %d columns" % (fieldname,fieldsize[1])))
			elif np.isnan(fieldsize[1]):
				if not np.size(field,0)==fieldsize[0]:
					md = md.checkmessage(options.getfieldvalue('message',"field '%s' should have %d lines" % (fieldname,fieldsize[0])))
			elif fieldsize[1]==1:
				if (not np.size(field,0)==fieldsize[0]):
					md = md.checkmessage(options.getfieldvalue('message',"field '%s' size should be %d x %d" % (fieldname,fieldsize[0],fieldsize[1])))
			else:
				if (not np.size(field,0)==fieldsize[0]) or (not np.size(field,1)==fieldsize[1]):
					md = md.checkmessage(options.getfieldvalue('message',"field '%s' size should be %d x %d" % (fieldname,fieldsize[0],fieldsize[1])))
	
	#Check numel
	if options.exist('numel'):
		fieldnumel=options.getfieldvalue('numel')
		if np.size(field) not in fieldnumel:
			if   len(fieldnumel)==1:
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' size should be %d" % (fieldname,fieldnumel)))
			elif len(fieldnumel)==2:
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' size should be %d or %d" % (fieldname,fieldnumel[0],fieldnumel[1])))
			else:
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' size should be %s" % (fieldname,fieldnumel)))

	#check NaN
	if options.getfieldvalue('NaN',0):
		if np.any(np.isnan(field)):
			md = md.checkmessage(options.getfieldvalue('message',\
				"NaN values found in field '%s'" % fieldname))

	#check Inf
	if options.getfieldvalue('Inf',0):
		if np.any(np.isinf(field)):
			md = md.checkmessage(options.getfieldvalue('message',\
				"Inf values found in field '%s'" % fieldname))

	#check cell
	if options.getfieldvalue('cell',0):
		if not isinstance(field,(tuple,list,dict)):
			md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' should be a cell" % fieldname))

	#check values
	if options.exist('values'):
		fieldvalues=options.getfieldvalue('values')
		if False in m.ismember(field,fieldvalues):
			if   len(fieldvalues)==1:
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' value should be '%s'"  % (fieldname,fieldvalues[0])))
			elif len(fieldvalues)==2:
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' values should be '%s' or '%s'"  % (fieldname,fieldvalues[0],fieldvalues[1])))
			else:
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' should have values in %s" % (fieldname,fieldvalues)))

	#check greater
	if options.exist('>='):
		lowerbound=options.getfieldvalue('>=')
		if np.any(field<lowerbound):
			md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' should have values above %d" % (fieldname,lowerbound)))
	if options.exist('>'):
		lowerbound=options.getfieldvalue('>')
		if np.any(field<=lowerbound):
			md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' should have values above %d" % (fieldname,lowerbound)))

	#check smaller
	if options.exist('<='):
		upperbound=options.getfieldvalue('<=')
		if np.any(field>upperbound):
			md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' should have values below %d" % (fieldname,upperbound)))
	if options.exist('<'):
		upperbound=options.getfieldvalue('<')
		if np.any(field>=upperbound):
			md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' should have values below %d" % (fieldname,upperbound)))

	#check file
	if options.getfieldvalue('file',0):
		if not os.path.exists(field):
			md = md.checkmessage("file provided in '%s': '%s' does not exist" % (fieldname,field))

	#Check row of strings
	if options.exist('stringrow'):
		if not isinstance(field,list):
			md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' should be a list" %fieldname))

	#Check forcings (size and times)
	if options.getfieldvalue('timeseries',0):
		if   np.size(field,0)==md.mesh.numberofvertices:
			if np.ndim(field)>1 and not np.size(field,1)==1:
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' should have only one column as there are md.mesh.numberofvertices lines" % fieldname))
		elif np.size(field,0)==md.mesh.numberofvertices+1 or np.size(field,0)==2:
			if not all(field[-1,:]==np.sort(field[-1,:])):
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' columns should be sorted chronologically" % fieldname))
			if any(field[-1,0:-1]==field[-1,1:]):
				md = md.checkmessage(options.getfieldvalue('message',\
					"field '%s' columns must not contain duplicate timesteps" % fieldname))
		else:
			md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' should have md.mesh.numberofvertices or md.mesh.numberofvertices+1 lines" % fieldname))

	#Check single value forcings (size and times)
	if options.getfieldvalue('singletimeseries',0):
		if np.size(field,0)==2:
			if not all(field[-1,:]==np.sort(field[-1,:])):
				md = md.checkmessage(options.getfieldvalue('message',\
						"field '%s' columns should be sorted chronologically" % fieldname))
			if any(field[-1,0:-1]==field[-1,1:]):
				md = md.checkmessage(options.getfieldvalue('message',\
						"field '%s' columns must not contain duplicate timesteps" % fieldname))
		else:
				md = md.checkmessage(options.getfieldvalue('message',\
				"field '%s' should have 2 lines" % fieldname))

	return md

