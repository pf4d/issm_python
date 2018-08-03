# import socket
# import os
# import math
import subprocess
from fielddisplay import fielddisplay
from pairoptions import pairoptions
from issmssh import issmssh
from issmscpin import issmscpin
from issmscpout import issmscpout
from QueueRequirements import QueueRequirements
try:
	from pfe_settings import pfe_settings
except ImportError:
	print 'You need pfe_settings.py to proceed, check presence and sys.path'
	
class pfe(object):
	"""
	PFE cluster class definition
 
	   Usage:
	      cluster=pfe();
	      cluster=pfe('np',3);
	      cluster=pfe('np',3,'login','username');
	"""

	def __init__(self,*args):
		# {{{

		self.name           = 'pfe'
		self.login          = ''
		self.numnodes       = 20
		self.cpuspernode    = 8
		self.port           = 1025
		self.queue          = 'long'
		self.time           = 12*60
		self.processor      = 'wes'
		self.codepath       = ''
		self.executionpath  = ''
		self.grouplist      = 's1010'
		self.interactive    = 0
		self.bbftp          = 0
		self.numstreams     = 8
		self.hyperthreading = 0

		#use provided options to change fields
		options=pairoptions(*args)

		#initialize cluster using user settings if provided
		self=pfe_settings(self)
		self.np=self.nprocs()
		#OK get other fields
		self=options.AssignObjectFields(self)
		
		# }}}

	def __repr__(self):
		# {{{
		#  display the object
		s = "class pfe object:"
		s	= "%s\n%s"%(s,fielddisplay(self,'name','name of the cluster'))
		s	= "%s\n%s"%(s,fielddisplay(self,'login','login'))
		s = "%s\n%s"%(s,fielddisplay(self,'numnodes','number of nodes'))
		s = "%s\n%s"%(s,fielddisplay(self,'cpuspernode','number of nodes per CPUs'))
		s = "%s\n%s"%(s,fielddisplay(self,'np','number of CPUs'))
		s = "%s\n%s"%(s,fielddisplay(self,'port','machine access port'))
		s = "%s\n%s"%(s,fielddisplay(self,'codepath','code path on the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'executionpath','execution path on the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'queue','name of the queue'))
		s = "%s\n%s"%(s,fielddisplay(self,'time','walltime requested'))
		s = "%s\n%s"%(s,fielddisplay(self,'processor','type of processor'))
		s = "%s\n%s"%(s,fielddisplay(self,'grouplist','name of the group'))
		s = "%s\n%s"%(s,fielddisplay(self,'interactive',''))
		s = "%s\n%s"%(s,fielddisplay(self,'bbftp',''))
		s = "%s\n%s"%(s,fielddisplay(self,'numstreams',''))
		s = "%s\n%s"%(s,fielddisplay(self,'hyperthreading',''))
		return s
	# }}}

	def nprocs(self):
		# {{{
		self.np=self.numnodes*self.cpuspernode
		return self.np
		# }}}
	def checkconsistency(self,md,solution,analyses):
		# {{{


		queuedict = {'long': [5*24*60, 2048],
								 'normal': [8*60, 2048],
								 'debug':[2*60,150],
								 'devel':[2*60,150]}
		QueueRequirements(queuedict,self.queue,self.nprocs(),self.time)

		#now, check cluster.cpuspernode according to processor type
		if self.processor=='har' or self.processor=='neh':
			if self.hyperthreading:
				if not 0<self.cpuspernode<17:
					md = md.checkmessage('cpuspernode should be between 1 and 16 for ''neh'' and ''har'' processors in hyperthreading mode')
			else:
				if not 0<self.cpuspernode<9:
					md = md.checkmessage('cpuspernode should be between 1 and 8 for ''neh'' and ''har'' processors')

		elif self.processor=='wes':
			if self.hyperthreading:
				if not 0<self.cpuspernode<25:
					md = md.checkmessage('cpuspernode should be between 1 and 24 for ''wes'' processors in hyperthreading mode')
			else:
				if not 0<self.cpuspernode<13:
					md = md.checkmessage('cpuspernode should be between 1 and 12 for ''wes'' processors')

		elif self.processor=='ivy':
			if self.hyperthreading:
				if not 0<self.cpuspernode<41:
					md = md.checkmessage('cpuspernode should be between 1 and 40 for ''ivy'' processors in hyperthreading mode')
			else:
				if not 0<self.cpuspernode<21:
					md = md.checkmessage('cpuspernode should be between 1 and 20 for ''ivy'' processors')
		else:
			md = md.checkmessage('unknown processor type, should be ''neh'',''wes'' or ''har'' or ''ivy''')
	
		#Miscelaneous
		if not self.login:
			md = md.checkmessage('login empty')
		if not self.codepath:
			md = md.checkmessage('codepath empty')
		if not self.executionpath:
			md = md.checkmessage('executionpath empty')
		if not self.grouplist:
			md = md.checkmessage('grouplist empty')
		if self.interactive==1:
			md = md.checkmessage('interactive mode not implemented')
			
		return self
	# }}}
	def BuildQueueScript(self,dirname,modelname,solution,io_gather,isvalgrind,isgprof,isdakota,isoceancoupling):
		# {{{

		executable='issm.exe'
		if isdakota:
			version=IssmConfig('_DAKOTA_VERSION_')[0:2]
			version=float(version)
			if version>=6:
				executable='issm_dakota.exe'
		if isoceancoupling:
			executable='issm_ocean.exe'

		#write queuing script 
		fid=open(modelname+'.queue','w')
		fid.write('#PBS -S /bin/bash\n')
		fid.write('#PBS -l select=%i:ncpus=%i:model=%s\n' % (self.numnodes,self.cpuspernode,self.processor))
		fid.write('#PBS -l walltime=%i\n' % (self.time*60))
		fid.write('#PBS -q %s \n' % self.queue)
		fid.write('#PBS -W group_list=%s\n' % self.grouplist)
		fid.write('#PBS -m e\n')
		fid.write('#PBS -o %s/%s/%s.outlog \n' % (self.executionpath,dirname,modelname))
		fid.write('#PBS -e %s/%s/%s.errlog \n\n' % (self.executionpath,dirname,modelname))
		fid.write('. /usr/share/modules/init/bash\n\n')
		fid.write('module load comp-intel/2015.0.090\n')
		fid.write('module load mpi-sgi/mpt.2.11r13\n')
		fid.write('export PATH="$PATH:."\n\n')
		fid.write('export MPI_GROUP_MAX=64\n\n')
		fid.write('export ISSM_DIR="%s/../"\n' % self.codepath)
		fid.write('source $ISSM_DIR/etc/environment.sh\n')
		fid.write('cd %s/%s/\n\n' % (self.executionpath,dirname))
		fid.write('mpiexec -np %i %s/%s %s %s/%s %s\n' % (self.nprocs(),self.codepath,executable,str(solution),self.executionpath,dirname,modelname))
		
		fid.close()

	# }}}
	def UploadQueueJob(self,modelname,dirname,filelist):
			# {{{

		#compress the files into one zip.
		compressstring='tar -zcf %s.tar.gz ' % dirname
		for file in filelist:
			compressstring += ' %s' % file
		subprocess.call(compressstring,shell=True)

		print 'uploading input file and queueing script'
		issmscpout(self.name,self.executionpath,self.login,self.port,[dirname+'.tar.gz'])

		# }}}
	def LaunchQueueJob(self,modelname,dirname,filelist,restart,batch):
			# {{{

		print 'launching solution sequence on remote cluster'
		if restart:
			launchcommand='cd %s && cd %s && qsub %s.queue' % (self.executionpath,dirname,modelname)
		else:
			launchcommand='cd %s && rm -rf ./%s && mkdir %s && cd %s && mv ../%s.tar.gz ./ && tar -zxf %s.tar.gz  && qsub %s.queue' % (self.executionpath,dirname,dirname,dirname,dirname,dirname,modelname)
		issmssh(self.name,self.login,self.port,launchcommand)

		# }}}
	def Download(self,dirname,filelist):
		# {{{

		#copy files from cluster to current directory
		directory='%s/%s/' % (self.executionpath,dirname)
		issmscpin(self.name,self.login,self.port,directory,filelist)
	# }}}
