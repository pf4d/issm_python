import os
import socket
import platform
from issm.loadresultsfromdisk import loadresultsfromdisk

def loadresultsfromcluster(md,runtimename=False):
	"""
	LOADRESULTSFROMCLUSTER - load results of solution sequence from cluster
 
	   Usage:
	      md=loadresultsfromcluster(md,runtimename);
	"""

	#retrieve cluster, to be able to call its methods
	cluster=md.cluster

	if runtimename:
		md.private.runtimename=runtimename

	#Download outputs from the cluster
	filelist=[md.miscellaneous.name+'.outlog',md.miscellaneous.name+'.errlog']
	if md.qmu.isdakota:
		filelist.append(md.miscellaneous.name+'.qmu.err')
		filelist.append(md.miscellaneous.name+'.qmu.out')
		if 'tabular_graphics_data' in md.qmu.params:
			if md.qmu.params['tabular_graphics_data']:
				filelist.append('dakota_tabular.dat')
	else:
		filelist.append(md.miscellaneous.name+'.outbin')
	cluster.Download(md.private.runtimename,filelist)

	#If we are here, no errors in the solution sequence, call loadresultsfromdisk.
	if os.path.getsize(md.miscellaneous.name+'.outbin')>0:
		md=loadresultsfromdisk(md,md.miscellaneous.name+'.outbin')
	else:
		print 'WARNING, outbin file is empty for run '+md.miscellaneous.name
		
	#erase the log and output files
	if md.qmu.isdakota:
		filename=os.path.join('qmu'+str(os.getpid()),md.miscellaneous.name)
	else:
		filename=md.miscellaneous.name
		TryRem('.outbin',filename)
		if not platform.system()=='Windows':
			TryRem('.tar.gz',md.private.runtimename)

	TryRem('.errlog',filename)
	TryRem('.outlog',filename)
	
	#erase input file if run was carried out on same platform.
	hostname=socket.gethostname()
	if hostname==cluster.name:
		if md.qmu.isdakota:
			filename=os.path.join('qmu'+str(os.getpid()),md.miscellaneous.name)
			TryRem('.queue',filename)
		else:
			filename=md.miscellaneous.name
			TryRem('.toolkits',filename)
			if not platform.system()=='Windows':
				TryRem('.queue',filename)
			else:
				TryRem('.bat',filename)

		TryRem('.bin',filename)

	return md

def TryRem(extension,filename):
	try:	
		os.remove(filename+extension)
	except OSError:
		print 'WARNING, no '+extension+'  is present for run '+filename
