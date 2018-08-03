import subprocess
from issm.fielddisplay import fielddisplay
from issm.pairoptions import pairoptions
from issm.issmssh import issmssh
from issm.issmscpin import issmscpin
from issm.issmscpout import issmscpout
from issm.QueueRequirements import QueueRequirements
import datetime
try:
	from issm.cyclone_settings import cyclone_settings
except ImportError:
	print 'You need cyclone_settings.py to proceed, check presence and sys.path'
	
class cyclone(object):
	"""
	Be aware that this is not a cluster as we usually know them. There is no scheduling and ressources are pretty low.
	The Computer have 20 cpus and 512Gb of memory used by a number of person so be respectful with your usage.
	I putted some restrictive upper limits to avoid over-use. (Basile)
 
	   Usage:
	      cluster=cyclone();
	"""

	def __init__(self,*args):
		# {{{
		self.name           = 'cyclone'
		self.login          = ''
		self.np             = 2
		self.time           = 100
		self.codepath       = ''
		self.executionpath  = ''
		self.port           = ''
		self.interactive    = 0

		#use provided options to change fields
		options=pairoptions(*args)

		#initialize cluster using user settings if provided
		self=cyclone_settings(self)
		#OK get other fields
		self=options.AssignObjectFields(self)
		
		# }}}

	def __repr__(self):
	# {{{
		#  display the object
		s = "class cyclone object:"
		s = "%s\n%s"%(s,fielddisplay(self,'name','name of the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'login','login'))
		s = "%s\n%s"%(s,fielddisplay(self,'np','number of processes'))
		s = "%s\n%s"%(s,fielddisplay(self,'time','walltime requested in minutes'))
		s = "%s\n%s"%(s,fielddisplay(self,'codepath','code path on the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'executionpath','execution path on the cluster'))
		return s
	# }}}

	def checkconsistency(self,md,solution,analyses):
		# {{{
		#Miscelaneous
		if not self.login:
			md = md.checkmessage('login empty')
		if not self.codepath:
			md = md.checkmessage('codepath empty')
		if not self.executionpath:
			md = md.checkmessage('executionpath empty')
		if self.time>72:
			md = md.checkmessage('walltime exceeds 72h for niceness this is not allowed, if you need more time consider shifting to one of the Notur systems')
		if self.np >10:
			md = md.checkmessage('number of process excess 10, if you need more processing power consider shifting to one of the Notur systems')

		return self
                # }}}
	def BuildQueueScript(self,dirname,modelname,solution,io_gather,isvalgrind,isgprof,isdakota,isoceancoupling):
		# {{{

		executable='issm.exe'
		
		#write queuing script 
		shortname=modelname[0:min(12,len(modelname))]
		fid=open(modelname+'.queue','w')
		fid.write('export ISSM_DIR="%s/../"\n' % self.codepath)
		fid.write('source $ISSM_DIR/etc/environment.sh\n')
		fid.write('INTELLIBS="/opt/intel/intelcompiler-12.04/composerxe-2011.4.191/compiler/lib/intel64"\n')
		fid.write('export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/:$INTELLIBS\n')
		fid.write('export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:/usr/include/x86_64-linux-gnu/c++/4.8\n')
		fid.write('cd %s/%s/\n\n' % (self.executionpath,dirname))
		rundir=self.executionpath+'/'+dirname
		runfile=self.executionpath+'/'+dirname+'/'+modelname
		fid.write('mpiexec -np %i %s/%s %s %s %s >%s.outlog 2>%s.errlog\n' % (self.np,self.codepath,executable,str(solution),rundir,modelname,runfile,runfile))
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
			launchcommand='cd %s && rm -rf ./%s && mkdir %s && cd %s && mv ../%s.tar.gz ./ && tar -zxf %s.tar.gz  && chmod +x ./%s.queue && ./%s.queue' % (self.executionpath,dirname,dirname,dirname,dirname,dirname,modelname,modelname)
		issmssh(self.name,self.login,self.port,launchcommand)

		# }}}
	def Download(self,dirname,filelist):
		# {{{

		#copy files from cluster to current directory
		directory='%s/%s/' % (self.executionpath,dirname)
		issmscpin(self.name,self.login,self.port,directory,filelist)
		# }}}
