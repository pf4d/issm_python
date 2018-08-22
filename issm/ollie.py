import socket
import os, sys
import math
import subprocess
from issm.IssmConfig  import IssmConfig
from issm.issmdir     import issmdir
from issm.pairoptions import pairoptions
from issm.issmssh     import issmssh
from issm.issmscpin   import issmscpin
from issm.issmscpout  import issmscpout
import issm.MatlabFuncs   as m

class ollie(object):
  """
  AWI's Ollie cluster class definition
 
     Usage:
        cluster=ollie('name','astrid','np',3);
        cluster=ollie('name',gethostname(),'np',3,'login','username');
  """

  def __init__(self, *args):
    """
    """
    self.name            = ''
    self.login           = ''
    self.hostname        = ''
    self.ntasks          = 1
    self.nodes           = 1
    self.time            = 5   # [minutes] time to complete
    self.port            = 0
    self.interactive     = 1
    self.codepath        = IssmConfig('ISSM_PREFIX')[0] + '/bin'
    self.executionpath   = os.path.abspath(os.path.dirname(sys.argv[0]))
    valgrind_dir         = issmdir() + '/externalpackages/valgrind'
    self.valgrind        = valgrind_dir + '/install/bin/valgrind'
    self.valgrindlib     = valgrind_dir + '/install/lib/libmpidebug.so'
    self.valgrindsup     = valgrind_dir + '/issm.supp'

    #use provided options to change fields
    options              = pairoptions(*args)

    #get name
    self.hostname        = 'ollie0'  # socket.gethostname()

    #initialize cluster using user settings if provided
    if os.path.exists(self.name + '_settings.py'):
      execfile(self.name + '_settings.py', globals())

    #OK get other fields
    self                 = options.AssignObjectFields(self)

  def __repr__(self):
    """
    """
    #  display the object
    s ="class '%s' object '%s' = \n" % (type(self),'self')
    s+="    name:            %s\n" % self.name
    s+="    login:           %s\n" % self.login
    s+="    ntasks:          %i\n" % self.ntasks
    s+="    nodes:           %i\n" % self.nodes
    s+="    time (m):        %i\n" % self.time
    s+="    port:            %i\n" % self.port
    s+="    codepath:        %s\n" % self.codepath
    s+="    executionpath:   %s\n" % self.executionpath
    s+="    valgrind:        %s\n" % self.valgrind
    s+="    valgrindlib:     %s\n" % self.valgrindlib
    s+="    valgrindsup:     %s\n" % self.valgrindsup
    return s

  def checkconsistency(self, md, solution, analyses):
    """
    """
    if self.ntasks < 1:
      md = checkmessage(md, 'number of tasks should be at least 1')
    if math.isnan(self.ntasks):
      md = checkmessage(md, 'number of tasks should not be NaN!')
    return md

  def BuildQueueScript(self, dirname, modelname, solution, io_gather,
                       isvalgrind, isgprof, isdakota, isoceancoupling):
    """
    """
    executable = 'issm.exe'
    if isdakota:
      version = IssmConfig('_DAKOTA_VERSION_')[0:2]
      version = float(version)
      if version >= 6:
        executable = 'issm_dakota.exe'
    if isoceancoupling:
      executable = 'issm_ocean.exe'

    #write queuing script 
    if not m.ispc():
      if   self.time <= 30:                            qos       = 'short'
      elif self.time >  30    and self.time <= 48*60:  qos       = 'large'
      elif self.time >  48*60:                         qos       = 'xlarge'
      if   self.ntasks <= 12:                          partition = 'mini'
      if   self.ntasks >  12 and self.ntasks <= 36:    partition = 'smp'
      elif self.ntasks >  36:                          partition = 'mpp'
      fid = open(modelname + '.queue', 'w')
      fid.write('#!/bin/bash\n')
      fid.write('#SBATCH --ntasks=%i\n'          % self.ntasks)
      fid.write('#SBATCH --nodes=%i\n'           % self.nodes)
      fid.write('#SBATCH --job-name=%s\n'        % modelname)
      fid.write('#SBATCH -t %i\n'                % self.time)
      fid.write('#SBATCH -o %s.outlog\n'         % modelname)
      fid.write('#SBATCH -e %s.errlog\n'         % modelname)
      fid.write('#SBATCH -p %s\n'                % partition)
      fid.write('#SBATCH --qos=%s\n'             % qos)
      fid.write('#SBATCH --get-user-env\n\n')
      fid.write('export OMP_NUM_THREADS=1;\n\n')
      #fid.write('ulimit -s unlimited\n')
      #fid.write('export OMP_PROC_BIND=TRUE\n\n')
      #fid.write('export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK\n\n')
      #fid.write('srun /global/AWIsoft/xthi/xthi.intel\n\n')
      pth = self.executionpath + '/' + dirname
      fid.write('srun --cpu_bind=cores %s/issm.exe %s %s %s\n\n\n' % \
                (self.codepath, solution, pth, modelname))

    #in interactive mode, create a run file, and errlog and outlog file
    if self.interactive:
      fid=open(modelname+'.errlog','w')
      fid.close()
      fid=open(modelname+'.outlog','w')
      fid.close()

  def UploadQueueJob(self, modelname, dirname, filelist):
    """
    """
    #compress the files into one zip.
    compressstring='tar -zcf %s.tar.gz ' % dirname
    for file in filelist:
      compressstring += ' %s' % file
    if self.interactive:
      compressstring += ' %s.errlog %s.outlog ' % (modelname,modelname)
    subprocess.call(compressstring,shell=True)
    
    # remove the files :
    rmstring = 'rm '
    for file in filelist:
      rmstring += ' %s' % file
    if self.interactive:
      rmstring += ' %s.errlog %s.outlog ' % (modelname, modelname)
    subprocess.call(rmstring, shell=True)

    print 'uploading input file and queueing script'
    #issmscpout(self.hostname, self.executionpath, self.login, self.port, 
    #           [dirname+'.tar.gz'])

  def LaunchQueueJob(self, modelname, dirname, filelist, restart, batch):
    """
    """
    print 'launching solution sequence on remote cluster'
    if restart:
      launchcommand='cd %s && cd %s chmod 777 %s.queue && ./%s.queue' \
                     % (self.executionpath,dirname,modelname,modelname)
    else:
      launchcommand='cd %s && \
                     rm -rf ./%s && \
                     mkdir %s && \
                     cd %s && \
                     mv ../%s.tar.gz ./ && \
                     tar -zxf %s.tar.gz && \
                     source ~/.bash_profile && \
                     sbatch ./%s.queue' \
                     % (self.executionpath, \
                        dirname, \
                        dirname, \
                        dirname, \
                        dirname, \
                        dirname, \
                        modelname)
    issmssh(self.hostname,self.login,self.port,launchcommand)

  def Download(self,dirname,filelist):
    """
    """
    if m.ispc():
      #do nothing
      return

    #copy files from cluster to current directory
    directory='%s/%s/' % (self.executionpath,dirname)
    issmscpin(self.hostname,self.login,self.port,directory,filelist)



