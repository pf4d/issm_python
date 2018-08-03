import datetime
import os
import shutil
from issm.pairoptions import pairoptions
from issm.ismodelselfconsistent import ismodelselfconsistent
from issm.marshall import marshall
from issm.waitonlock import waitonlock
from issm.loadresultsfromcluster import loadresultsfromcluster

def solve(md,solutionstring,*args):
	"""
	SOLVE - apply solution sequence for this model
 
	   Usage:
	      md=solve(md,solutionstring,varargin)
	      where varargin is a list of paired arguments of string OR enums
 
		solution types available comprise:
		 - 'Stressbalance'    or 'sb'
		 - 'Masstransport'    or 'mt'
		 - 'Thermal'          or 'th'
		 - 'Steadystate'      or 'ss'
		 - 'Transient'        or 'tr'
		 - 'Balancethickness' or 'mc'
		 - 'Balancevelocity'  or 'bv'
		 - 'BedSlope'         or 'bsl'
		 - 'SurfaceSlope'     or 'ssl'
		 - 'Hydrology'        or 'hy'
		 - 'DamageEvolution'  or 'da'
		 - 'Gia'              or 'gia'
		 - 'Sealevelrise'     or 'slr'

	   extra options:
        - loadonly : does not solve. only load results
		  - checkconsistency : 'yes' or 'no' (default is 'yes'), ensures checks on consistency of model
		  - restart: 'directory name (relative to the execution directory) where the restart file is located.
 
	   Examples:
	      md=solve(md,'Stressbalance');
         md=solve(md,'sb');
	"""

	#recover and process solve options
	if solutionstring.lower() == 'sb' or solutionstring.lower() == 'stressbalance':
		solutionstring = 'StressbalanceSolution';
	elif solutionstring.lower() == 'mt' or solutionstring.lower() == 'masstransport':
		solutionstring = 'MasstransportSolution';	
	elif solutionstring.lower() == 'th' or solutionstring.lower() == 'thermal':
		solutionstring = 'ThermalSolution';
	elif solutionstring.lower() == 'st' or solutionstring.lower() == 'steadystate':
		solutionstring = 'SteadystateSolution';
	elif solutionstring.lower() == 'tr' or solutionstring.lower() == 'transient':
		solutionstring = 'TransientSolution';
	elif solutionstring.lower() == 'mc' or solutionstring.lower() == 'balancethickness':
		solutionstring = 'BalancethicknessSolution';
	elif solutionstring.lower() == 'bv' or solutionstring.lower() == 'balancevelocity':
		solutionstring = 'BalancevelocitySolution';
	elif solutionstring.lower() == 'bsl' or solutionstring.lower() == 'bedslope':
		solutionstring = 'BedSlopeSolution';
	elif solutionstring.lower() == 'ssl' or solutionstring.lower() == 'surfaceslope':
		solutionstring = 'SurfaceSlopeSolution';
	elif solutionstring.lower() == 'hy' or solutionstring.lower() == 'hydrology':
		solutionstring = 'HydrologySolution';
	elif solutionstring.lower() == 'da' or solutionstring.lower() == 'damageevolution':
		solutionstring = 'DamageEvolutionSolution';
	elif solutionstring.lower() == 'gia' or solutionstring.lower() == 'gia':
		solutionstring = 'GiaSolution';
	elif solutionstring.lower() == 'slr' or solutionstring.lower() == 'sealevelrise':
		solutionstring = 'SealevelriseSolution';
	else: 	
		raise ValueError("solutionstring '%s' not supported!" % solutionstring)
	options=pairoptions('solutionstring',solutionstring,*args)

	#recover some fields
	md.private.solution=solutionstring
	cluster=md.cluster 
	if options.getfieldvalue('batch','no')=='yes':
		batch=1
	else:
		batch=0;

	#check model consistency
	if options.getfieldvalue('checkconsistency','yes')=='yes':
		print "checking model consistency"
		ismodelselfconsistent(md)

	#First, build a runtime name that is unique
	restart=options.getfieldvalue('restart','')
	if restart == 1:
		pass #do nothing
	else:
		if restart:
			md.private.runtimename=restart
		else:
			if options.getfieldvalue('runtimename',True):
				c=datetime.datetime.now()
				md.private.runtimename="%s-%02i-%02i-%04i-%02i-%02i-%02i-%i" % (md.miscellaneous.name,c.month,c.day,c.year,c.hour,c.minute,c.second,os.getpid())
			else:
				md.private.runtimename=md.miscellaneous.name 

	#if running qmu analysis, some preprocessing of dakota files using models
	#fields needs to be carried out. 
	if md.qmu.isdakota:
		md=preqmu(md,options)

	#Do we load results only?
	if options.getfieldvalue('loadonly',False):
		md=loadresultsfromcluster(md)
		return md


	#Write all input files
	marshall(md)                                           # bin file
	md.toolkits.ToolkitsFile(md.miscellaneous.name+'.toolkits')    # toolkits file
	cluster.BuildQueueScript(md.private.runtimename,md.miscellaneous.name,md.private.solution,md.settings.io_gather,md.debug.valgrind,md.debug.gprof,md.qmu.isdakota,md.transient.isoceancoupling)    # queue file

	#Stop here if batch mode
	if options.getfieldvalue('batch','no')=='yes':
		print 'batch mode requested: not launching job interactively'
		print 'launch solution sequence on remote cluster by hand'
		return md

	#Upload all required files: 
	modelname = md.miscellaneous.name
	filelist  = [modelname+'.bin ',modelname+'.toolkits ',modelname+'.queue ']
	if md.qmu.isdakota:
		filelist.append(modelname+'.qmu.in')

	if not restart:
		cluster.UploadQueueJob(md.miscellaneous.name,md.private.runtimename,filelist)
	
	#Launch job
	cluster.LaunchQueueJob(md.miscellaneous.name,md.private.runtimename,filelist,restart,batch)

	#wait on lock
	if md.settings.waitonlock>0:
		#we wait for the done file
		islock=waitonlock(md)
		if islock==0:    #no results to be loaded
			print 'The results must be loaded manually with md=loadresultsfromcluster(md).'
		else:            #load results
			print 'loading results from cluster'
			md=loadresultsfromcluster(md)

	#post processes qmu results if necessary
	if md.qmu.isdakota:
		if not strncmpi(options['keep'],'y',1):
			shutil.rmtree('qmu'+str(os.getpid()))

	return md
