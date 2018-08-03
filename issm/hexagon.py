import subprocess
from issm.fielddisplay import fielddisplay
from issm.pairoptions import pairoptions
from issm.issmssh import issmssh
from issm.issmscpin import issmscpin
from issm.issmscpout import issmscpout
from issm.QueueRequirements import QueueRequirements
import datetime
try:
	from issm.hexagon_settings import hexagon_settings
except ImportError:
	print 'You need hexagon_settings.py to proceed, check presence and sys.path'
	
class hexagon(object):
	"""
	Hexagon cluster class definition
	Hexagon have nodes built of 2*16 CPUs. Nodes are dedicated to one job so the best usage is to use 32 procs per nodes (16 per cores) as it is what is billed anyway. 
	You can reduce this number if you run out of memory as the total node memory is divided by the number of procs
	   Usage:
	      cluster=hexagon();
	"""

	def __init__(self,*args):
		# {{{
		self.name           = 'hexagon'
		self.login          = ''
		self.numnodes       = 2
		self.procspernodes  = 32
		self.mem            = 32000
		self.queue          = 'batch'
		self.time           = 2*60
		self.codepath       = ''
		self.executionpath  = ''
		self.interactive    = 0
		self.port           = []
		self.accountname    = ''

		#use provided options to change fields
		options=pairoptions(*args)

		#initialize cluster using user settings if provided
		self=hexagon_settings(self)

		#OK get other fields
		self=options.AssignObjectFields(self)
		self.np=self.numnodes*self.procspernodes
		# }}}
	def __repr__(self):
		# {{{
		#  display the object
		s = "class hexagon object:"
		s = "%s\n%s"%(s,fielddisplay(self,'name','name of the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'login','login'))
		s = "%s\n%s"%(s,fielddisplay(self,'numnodes','number of nodes'))
		s = "%s\n%s"%(s,fielddisplay(self,'procspernodes','number of mpi procs per nodes  default and optimal is 32'))
		s = "%s\n%s"%(s,fielddisplay(self,'mem','Total node memory'))
		s = "%s\n%s"%(s,fielddisplay(self,'queue','name of the queue'))
		s = "%s\n%s"%(s,fielddisplay(self,'time','walltime requested in minutes'))
		s = "%s\n%s"%(s,fielddisplay(self,'codepath','code path on the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'executionpath','execution path on the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'interactive',''))
		s = "%s\n%s"%(s,fielddisplay(self,'accountname','your cluster account'))
		return s
                # }}}
	def checkconsistency(self,md,solution,analyses):
		# {{{
		#mem should not be over 32000mb
		#numprocs should not be over 4096
		#we have cpupernodes*numberofcpus=mppwidth and mppnppn=cpupernodes, 
		#Miscelaneous
		if not self.login:
			md = md.checkmessage('login empty')
		if not self.codepath:
			md = md.checkmessage('codepath empty')
		if not self.executionpath:
			md = md.checkmessage('executionpath empty')
		if self.interactive==1:
			md = md.checkmessage('interactive mode not implemented')
		if self.mem>32000:
			md = md.checkmessage('asking too much memory max is 32000 per node')
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
		shortname=modelname[0:min(12,len(modelname))]
		fid=open(modelname+'.queue','w')
		fid.write('#!/bin/bash\n')
		fid.write('#PBS -N %s \n' % shortname)
		fid.write('#PBS -l mppwidth=%i,mppnppn=%i\n' % (self.np,self.procspernodes))
                timeobj=datetime.timedelta(minutes=self.time)
                m,s=divmod(timeobj.total_seconds(), 60)
                h,m=divmod(m, 60)
                timestring="%02d:%02d:%02d" % (h, m, s)
		fid.write('#PBS -l walltime=%s\n' % timestring) #walltime is hh:mm:ss
		fid.write('#PBS -l mppmem=%imb\n' % int(self.mem/self.procspernodes))
		fid.write('#PBS -A %s\n' % self.accountname) 
		fid.write('#PBS -o %s/%s/%s.outlog \n' % (self.executionpath,dirname,modelname))
		fid.write('#PBS -e %s/%s/%s.errlog \n\n' % (self.executionpath,dirname,modelname))
		fid.write('export ISSM_DIR="%s/../"\n' % self.codepath)
		fid.write('export CRAY_ROOTFS=DSL\n')
		fid.write('module swap PrgEnv-cray/5.2.40 PrgEnv-gnu\n')
		fid.write('module load cray-petsc\n')
		fid.write('module load cray-tpsl\n')
		fid.write('module load cray-mpich\n')
		fid.write('module load gsl\n')
		fid.write('cd %s/%s/\n\n' % (self.executionpath,dirname))
		fid.write('aprun -B %s/%s %s %s/%s %s\n' % (self.codepath,executable,str(solution),self.executionpath,dirname,modelname))
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
