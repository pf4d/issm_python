import numpy as  np

def processdata(md,data,options):
	"""
	PROCESSDATA - process data to be plotted
	
	datatype = 1 -> elements
	datatype = 2 -> nodes
	datatype = 3 -> node quivers
	datatype = 4 -> patch
	
	Usage:
	data,datatype=processdata(md,data,options);
	
	See also: PLOTMODEL, PROCESSMESH
	"""
	# {{{ Initialisation and grabbing auxiliaries
	# check format
	if (len(data)==0 or (len(data)==1 and not isinstance(data,dict) and np.isnan(data).all())):
		raise ValueError("processdata error message: 'data' provided is empty")
	# get the shape
	if 'numberofvertices2d' in dir(md.mesh):
		numberofvertices2d=md.mesh.numberofvertices2d
		numberofelements2d=md.mesh.numberofelements2d
	else:
		numberofvertices2d=np.nan
		numberofelements2d=np.nan
	procdata=np.copy(data)
	#initialize datatype
	datatype=0
	# get datasize
	if np.ndim(procdata)==1:
		datasize=(np.shape(procdata)[0],1)
	elif np.ndim(procdata)==2:
		datasize=np.shape(procdata)
	elif np.ndim(procdata)==3:
		if np.shape(procdata)[0]==2:
			#treating a dim two list that needs to be stacked
			procdata=np.hstack((procdata[0,:,:],procdata[1,:,:]))
			datasize=np.shape(procdata)
		else:
			raise ValueError('data list contains more than two vectore, we can not cope with that')
	else:
		raise ValueError('data passed to plotmodel has bad dimensions; check that column vectors are rank-1')
  # }}}      
	# {{{ process NaN's if any
	nanfill=options.getfieldvalue('nan',-9999)
	if np.any(np.isnan(procdata)):
		lb=np.nanmin(procdata)
		ub=np.nanmax(procdata)
		if lb==ub:
			lb=lb-0.5
			ub=ub+0.5
			nanfill=lb-1
			#procdata[np.isnan(procdata)]=nanfill
		procdata=np.ma.array(procdata,mask=np.isnan(procdata))
		options.addfielddefault('clim',[lb,ub])
		options.addfielddefault('cmap_set_under','1')
		print "WARNING: nan's treated as", nanfill, "by default.  Change using pairoption 'nan',nan_fill_value in plotmodel call"
  # }}}  
	# {{{ log
	if options.exist('log'):
		cutoff=options.getfieldvalue('log',1)
		procdata[np.where(procdata<cutoff)]=cutoff
	# }}}
	# {{{ quiver plot
	if datasize[1]>1 and datasize[0]!= md.mesh.numberofvertices+1:
		if datasize[0]==md.mesh.numberofvertices and datasize[1]==2:
			datatype=3
		else:
			raise ValueError('plotmodel error message: data should have two columns of length md.mesh.numberofvertices for a quiver plot')
	# }}}  
	# {{{ element data

	if datasize[0]==md.mesh.numberofelements and datasize[1]==1:
		#initialize datatype if non patch
		if datatype!=4 and datatype!=5:
			datatype=1
		# {{{mask
		if options.exist('mask'):
			flags=options.getfieldvalue('mask')
			hide=np.invert(flags)
			if np.size(flags)==md.mesh.numberofvertices:
				EltMask=np.asarray([np.any(np.in1d(index,np.where(hide))) for index in md.mesh.elements-1])
				procdata=np.ma.array(procdata,mask=EltMask)
				options.addfielddefault('cmap_set_bad','w')
			elif np.size(flags)==md.mesh.numberofelements:
				procdata=np.ma.array(procdata,mask=hide)
				options.addfielddefault('cmap_set_bad','w')
			else:
				print('plotmodel warning: mask length not supported yet (supported length are md.mesh.numberofvertices and md.mesh.numberofelements')
		# }}}  

	# }}}  
	# {{{ node data
	if datasize[0]==md.mesh.numberofvertices and datasize[1]==1:
		datatype=2
		# {{{ Mask
		if options.exist('mask'):
			flags=options.getfieldvalue('mask')
			hide=np.invert(flags)
			if np.size(flags)==md.mesh.numberofvertices:
				procdata=np.ma.array(procdata,mask=hide)
				options.addfielddefault('cmap_set_bad','w')
			elif np.size(flags)==md.mesh.numberofelements:
				NodeMask=np.zeros(np.shape(md.mesh.x),dtype=bool)
				HideElt=md.mesh.elements[np.where(hide)[0]]-1
				NodeMask[HideElt]=True
				procdata=np.ma.array(procdata,mask=NodeMask)
				options.addfielddefault('cmap_set_bad','w')
			else:
				print('plotmodel warning: mask length not supported yet (supported length are md.mesh.numberofvertices and md.mesh.numberofelements')
	  # }}}  
	# }}}  
	# {{{ spc time series
	if datasize[0]==md.mesh.numberofvertices+1:
		datatype=2
		spccol=options.getfieldvalue('spccol',0)
		print 'multiple-column spc field; specify column to plot using option "spccol"'
		print 'column ', spccol, ' plotted for time: ', procdata[-1,spccol]
		procdata=procdata[0:-1,spccol]
    
		#mask?
    
    #layer projection?
    
    #control arrow density if quiver plot
	# }}}  
	# {{{ convert rank-2 array to rank-1
	if np.ndim(procdata)==2 and np.shape(procdata)[1]==1:
		procdata=procdata.reshape(-1,)
	# }}}  
	# {{{ if datatype is still zero, error out
	if datatype==0:
		raise ValueError("processdata error: data provided not recognized or not supported")
	else:
		return procdata, datatype
  # }}}  
