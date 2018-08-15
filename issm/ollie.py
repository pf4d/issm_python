import socket
import os
import math
import subprocess
from issm.IssmConfig import IssmConfig
from issm.issmdir import issmdir
from issm.pairoptions import pairoptions
from issm.issmssh import issmssh
from issm.issmscpin import issmscpin
from issm.issmscpout import issmscpout
import issm.MatlabFuncs as m

class ollie(object):
  """
  AWI's Ollie cluster class definition
 
     Usage:
        cluster=ollie('name','astrid','np',3);
        cluster=ollie('name',gethostname(),'np',3,'login','username');
  """

  def __init__(self,*args):    # {{{

    self.name=''
    self.login=''
    self.hostname=''
    self.np=1
    self.port=0
    self.interactive=1
    self.codepath=IssmConfig('ISSM_PREFIX')[0]+'/bin'
    self.executionpath=issmdir()+'/execution'
    self.valgrind=issmdir()+'/externalpackages/valgrind/install/bin/valgrind'
    self.valgrindlib=issmdir()+'/externalpackages/valgrind/install/lib/libmpidebug.so'
    self.valgrindsup=issmdir()+'/externalpackages/valgrind/issm.supp'

    #use provided options to change fields
    options=pairoptions(*args)

    #get name
    self.hostname='ollie0'#socket.gethostname()

    #initialize cluster using user settings if provided
    if os.path.exists(self.name+'_settings.py'):
      execfile(self.name+'_settings.py',globals())

    #OK get other fields
    self=options.AssignObjectFields(self)
  # }}}

  def __repr__(self):    # {{{
    #  display the object
    s ="class '%s' object '%s' = \n" % (type(self),'self')
    s+="    name: %s\n" % self.name
    s+="    login: %s\n" % self.login
    s+="    np: %i\n" % self.np
    s+="    port: %i\n" % self.port
    s+="    codepath: %s\n" % self.codepath
    s+="    executionpath: %s\n" % self.executionpath
    s+="    valgrind: %s\n" % self.valgrind
    s+="    valgrindlib: %s\n" % self.valgrindlib
    s+="    valgrindsup: %s\n" % self.valgrindsup
    return s
  # }}}

  def checkconsistency(self,md,solution,analyses):    # {{{
    if self.np<1:
      md = checkmessage(md,'number of processors should be at least 1')
    if math.isnan(self.np):
      md = checkmessage(md,'number of processors should not be NaN!')

    return md
  # }}}

  def BuildQueueScript(self,dirname,modelname,solution,io_gather,isvalgrind,isgprof,isdakota,isoceancoupling):    # {{{

    executable='issm.exe';
    if isdakota:
      version=IssmConfig('_DAKOTA_VERSION_')[0:2]
      version=float(version)
      if version>=6:
        executable='issm_dakota.exe'
    if isoceancoupling:
      executable='issm_ocean.exe'

    #write queuing script 
    if not m.ispc():

      fid=open(modelname+'.queue','w')
      #fid.write('#!/bin/bash -l\n\n')
      #fid.write('#SBATCH -N 1\n')
      #fid.write('#SBATCH -J my_job\n')
      #fid.write('#SBATCH --export=ALL\n\n')
      fid.write('#!/bin/bash\n')
      fid.write('#SBATCH --nodes=%i\n' % 1)#self.np)
      fid.write('#SBATCH --ntasks=%i\n' % 1)
      fid.write('#SBATCH --ntasks-per-node=%i\n' % 1)
      fid.write('#SBATCH --cpus-per-task=%i\n' % 1)
      fid.write('#SBATCH --job-name=%s\n' % modelname)
      #fid.write('#SBATCH -t %i\n',cluster.time*60); 
      fid.write('#SBATCH -p smp \n')
      fid.write('#SBATCH -o %s.outlog \n' % modelname)
      fid.write('#SBATCH -e %s.errlog \n' % modelname)
      fid.write('#SBATCH --get-user-env \n')
      #fid.write('##  Enlarge the stacksize. OpenMP-codes usually need a large stack. \n')
      #fid.write('ulimit -s unlimited\n')
      #fid.write('## This binds each thread to one core \n')
      #fid.write('export OMP_PROC_BIND=TRUE \n')
      #fid.write('## Number of threads as given by -c / --cpus-per-task \n')
      #fid.write('export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK \n')
      #fid.write('## This code snippet checks the task and thread distribution on the cores. \n')
      #fid.write('srun /global/AWIsoft/xthi/xthi.intel | sort -n -k4,4 -k6,6 > xthi.log \n')
      pth = self.executionpath + '/' + dirname
      fid.write('srun %s/issm.exe %s %s %s > %s.log\n' % (self.codepath, solution, pth, modelname, modelname))
  # }}}

  def BuildKrigingQueueScript(self,modelname,solution,io_gather,isvalgrind,isgprof):    # {{{

    #write queuing script 
    if not m.ispc():

      fid=open(modelname+'.queue','w')
      fid.write('#!/bin/sh\n')
      if not isvalgrind:
        if self.interactive:
          fid.write('srun -np %i %s/kriging.exe %s/%s %s ' % (self.np,self.codepath,self.executionpath,modelname,modelname))
        else:
          fid.write('srun -np %i %s/kriging.exe %s/%s %s 2> %s.errlog >%s.outlog ' % (self.np,self.codepath,self.executionpath,modelname,modelname,modelname,modelname))
      elif isgprof:
        fid.write('\n gprof %s/kriging.exe gmon.out > %s.performance' & (self.codepath,modelname))
      else:
        #Add --gen-suppressions=all to get suppression lines
        fid.write('LD_PRELOAD=%s \\\n' % self.valgrindlib)
        fid.write('mpiexec -np %i %s --leak-check=full --suppressions=%s %s/kriging.exe %s/%s %s 2> %s.errlog >%s.outlog ' % \
          (self.np,self.valgrind,self.valgrindsup,self.codepath,self.executionpath,modelname,modelname,modelname,modelname))
      if not io_gather:    #concatenate the output files:
        fid.write('\ncat %s.outbin.* > %s.outbin' % (modelname,modelname))
      fid.close()

    else:    # Windows

      fid=open(modelname+'.bat','w')
      fid.write('@echo off\n')
      if self.interactive:
        fid.write('"%s/issm.exe" %s "%s/%s" %s ' % (self.codepath,solution,self.executionpath,modelname,modelname))
      else:
        fid.write('"%s/issm.exe" %s "%s/%s" %s 2> %s.errlog >%s.outlog' % \
          (self.codepath,solution,self.executionpath,modelname,modelname,modelname,modelname))
      fid.close()

    #in interactive mode, create a run file, and errlog and outlog file
    if self.interactive:
      fid=open(modelname+'.errlog','w')
      fid.close()
      fid=open(modelname+'.outlog','w')
      fid.close()
  # }}}

  def UploadQueueJob(self,modelname,dirname,filelist):    # {{{

    #compress the files into one zip.
    compressstring='tar -zcf %s.tar.gz ' % dirname
    for file in filelist:
      compressstring += ' %s' % file
    if self.interactive:
      compressstring += ' %s.errlog %s.outlog ' % (modelname,modelname)
    subprocess.call(compressstring,shell=True)

    print 'uploading input file and queueing script'
    issmscpout(self.hostname,self.executionpath,self.login,self.port,[dirname+'.tar.gz'])

  # }}}

  def LaunchQueueJob(self,modelname,dirname,filelist,restart,batch):    # {{{

    print 'launching solution sequence on remote cluster'
    if restart:
      launchcommand='cd %s && cd %s chmod 777 %s.queue && ./%s.queue' % (self.executionpath,dirname,modelname,modelname)
    else:
      launchcommand='cd %s && rm -rf ./%s && mkdir %s && cd %s && mv ../%s.tar.gz ./ && tar -zxf %s.tar.gz  && source ~/.bash_profile && sbatch ./%s.queue' % (self.executionpath,dirname,dirname,dirname,dirname,dirname,modelname)
    issmssh(self.hostname,self.login,self.port,launchcommand)
  # }}}
  def Download(self,dirname,filelist):     # {{{

    if m.ispc():
      #do nothing
      return

    #copy files from cluster to current directory
    directory='%s/%s/' % (self.executionpath,dirname)
    issmscpin(self.hostname,self.login,self.port,directory,filelist)
  # }}}



