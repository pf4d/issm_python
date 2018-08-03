import subprocess
from fielddisplay import fielddisplay
from pairoptions import pairoptions
from issmssh import issmssh
from issmscpin import issmscpin
from issmscpout import issmscpout
from QueueRequirements import QueueRequirements
import datetime
try:
	from vilje_settings import vilje_settings
except ImportError:
	print 'You need vilje_settings.py to proceed, check presence and sys.path'
	
class vilje(object):
	"""
	Vilje cluster class definition
 
	   Usage:
	      cluster=vilje();
	"""

	def __init__(self,*args):
		# {{{
		self.name           = 'vilje'
		self.login          = ''
		self.numnodes       = 2
		self.cpuspernode    = 32
		self.procspernodes  = 16
		self.mem            = 28
		self.queue          = 'workq'
		self.time           = 2*60
		self.codepath       = ''
		self.executionpath  = ''
		self.interactive    = 0
		self.port           = []
		self.accountname    = ''

		#use provided options to change fields
		options=pairoptions(*args)

		#initialize cluster using user settings if provided
		self=vilje_settings(self)
		#OK get other fields
		self=options.AssignObjectFields(self)
		self.np=self.numnodes*self.procspernodes		
		# }}}
	def __repr__(self):
		# {{{
		#  display the object
		s = "class vilje object:"
		s = "%s\n%s"%(s,fielddisplay(self,'name','name of the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'login','login'))
		s = "%s\n%s"%(s,fielddisplay(self,'numnodes','number of nodes'))
		s = "%s\n%s"%(s,fielddisplay(self,'cpuspernode','number of nodes per CPUs (32)'))
		s = "%s\n%s"%(s,fielddisplay(self,'procspernodes','number of mpi procs per nodes'))
		s = "%s\n%s"%(s,fielddisplay(self,'mem','node memory'))
		s = "%s\n%s"%(s,fielddisplay(self,'queue','name of the queue (test is an option, workq the default)'))
		s = "%s\n%s"%(s,fielddisplay(self,'time','walltime requested in minutes'))
		s = "%s\n%s"%(s,fielddisplay(self,'codepath','code path on the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'executionpath','execution path on the cluster'))
		s = "%s\n%s"%(s,fielddisplay(self,'interactive',''))
		s = "%s\n%s"%(s,fielddisplay(self,'accountname','your cluster account'))
		return s
                # }}}
	def checkconsistency(self,md,solution,analyses):
		# {{{
                #Queue dictionarry  gives queu name as key and max walltime and cpus as var
		queuedict = {'workq':[5*24*60, 30],
								 'test':[30,4]}
		QueueRequirements(queuedict,self.queue,self.np,self.time)

		#Miscelaneous
		if not self.login:
			md = md.checkmessage('login empty')
		if not self.codepath:
			md = md.checkmessage('codepath empty')
		if not self.executionpath:
			md = md.checkmessage('executionpath empty')
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
		shortname=modelname[0:min(12,len(modelname))]
		fid=open(modelname+'.queue','w')
		fid.write('#PBS -S /bin/bash\n')
		fid.write('#PBS -N %s \n' % shortname)
		fid.write('#PBS -q %s \n' % self.queue)
		fid.write('#PBS -l select=%i:ncpus=%i:mpiprocs=%s\n' % (self.numnodes,self.cpuspernode,self.procspernodes))
                timeobj=datetime.timedelta(minutes=self.time)
                m,s=divmod(timeobj.total_seconds(), 60)
                h,m=divmod(m, 60)
                timestring="%02d:%02d:%02d" % (h, m, s)
		fid.write('#PBS -l walltime=%s\n' % timestring) #walltime is hh:mm:ss
		#fid.write('#PBS -l mem=%igb\n' % self.mem)
		fid.write('#PBS -A %s\n' % self.accountname) 
		fid.write('#PBS -o %s/%s/%s.outlog \n' % (self.executionpath,dirname,modelname))
		fid.write('#PBS -e %s/%s/%s.errlog \n\n' % (self.executionpath,dirname,modelname))
		fid.write('export ISSM_DIR="%s/../"\n' % self.codepath)
		fid.write('module load intelcomp/17.0.0\n') 
		fid.write('module load mpt/2.14\n')
		fid.write('module load petsc/3.7.4d\n')
		fid.write('module load parmetis/4.0.3\n') 
		fid.write('module load mumps/5.0.2\n')
		fid.write('cd %s/%s/\n\n' % (self.executionpath,dirname))
		fid.write('mpiexec_mpt -np %i %s/%s %s %s/%s %s\n' % (self.np,self.codepath,executable,str(solution),self.executionpath,dirname,modelname))
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
