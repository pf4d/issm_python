import sys, os, math, subprocess, socket
from issm.IssmConfig  import IssmConfig
from issm.issmdir     import issmdir
from issm.pairoptions import pairoptions
from issm.issmssh     import issmssh
from issm.issmscpin   import issmscpin
from issm.issmscpout  import issmscpout
import issm.MatlabFuncs   as m

class generic(object):
  """
  GENERIC cluster class definition
 
     Usage:
        cluster=generic('name','astrid','np',3);
        cluster=generic('name',gethostname(),'np',3,'login','username');
  """

  def __init__(self,*args):

    self.name            = ''
    self.login           = ''
    self.np              = 1
    self.port            = 0
    self.interactive     = 1
    self.codepath        = IssmConfig('ISSM_PREFIX')[0] + '/bin'
    self.executionpath   = os.path.abspath(os.path.dirname(sys.argv[0]))
    valgrind_dir         = issmdir() + '/externalpackages/valgrind'
    self.valgrind        = valgrind_dir + '/install/bin/valgrind'
    self.valgrindlib     = valgrind_dir + '/install/lib/libmpidebug.so'
    self.valgrindsup     = valgrind_dir + '/issm.supp'

    # use provided options to change fields :
    options              = pairoptions(*args)

    # get name :
    self.name        = socket.gethostname()

    #initialize cluster using user settings if provided
    if os.path.exists(self.name+'_settings.py'):
      execfile(self.name+'_settings.py',globals())

    #OK get other fields
    self=options.AssignObjectFields(self)

  def __repr__(self):
    #  display the object
    s ="class '%s' object '%s' = \n" % (type(self),'self')
    s+="    name:          %s\n" % self.name
    s+="    login:         %s\n" % self.login
    s+="    np:            %i\n" % self.np
    s+="    port:          %i\n" % self.port
    s+="    codepath:      %s\n" % self.codepath
    s+="    executionpath: %s\n" % self.executionpath
    s+="    valgrind:      %s\n" % self.valgrind
    s+="    valgrindlib:   %s\n" % self.valgrindlib
    s+="    valgrindsup:   %s\n" % self.valgrindsup
    return s

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
      fid.write('#!/bin/sh\n')
      if not isvalgrind:
        if self.interactive: 
          if IssmConfig('_HAVE_MPI_')[0]:
            fid.write('mpiexec -np %i %s/%s %s %s/%s %s ' % (self.np,self.codepath,executable,solution,self.executionpath,dirname,modelname))
          else:
            fid.write('%s/%s %s %s/%s %s ' % (self.codepath,executable,solution,self.executionpath,dirname,modelname))
        else:
          if IssmConfig('_HAVE_MPI_')[0]:
            fid.write('mpiexec -np %i %s/%s %s %s/%s %s 2> %s.errlog >%s.outlog ' % (self.np,self.codepath,executable,solution,self.executionpath,dirname,modelname,modelname,modelname))
          else:
            fid.write('%s/%s %s %s/%s %s 2> %s.errlog >%s.outlog ' % (self.codepath,executable,solution,self.executionpath,dirname,modelname,modelname,modelname))
      elif isgprof:
        fid.write('\n gprof %s/%s gmon.out > %s.performance' % (self.codepath,executable,modelname))
      else:
        #Add --gen-suppressions=all to get suppression lines
        fid.write('LD_PRELOAD=%s \\\n' % self.valgrindlib)
        if IssmConfig('_HAVE_MPI_')[0]:
          fid.write('mpiexec -np %i %s --leak-check=full --suppressions=%s %s/%s %s %s/%s %s 2> %s.errlog >%s.outlog ' % \
              (self.np,self.valgrind,self.valgrindsup,self.codepath,executable,solution,self.executionpath,dirname,modelname,modelname,modelname))
        else:  
          fid.write('%s --leak-check=full --suppressions=%s %s/%s %s %s/%s %s 2> %s.errlog >%s.outlog ' % \
              (self.valgrind,self.valgrindsup,self.codepath,executable,solution,self.executionpath,dirname,modelname,modelname,modelname))

      if not io_gather:    #concatenate the output files:
        fid.write('\ncat %s.outbin.* > %s.outbin' % (modelname,modelname))
      fid.close()

    else:    # Windows

      fid=open(modelname+'.bat','w')
      fid.write('@echo off\n')
      if self.interactive:
        fid.write('"%s/%s" %s "%s/%s" %s ' % (self.codepath,executable,solution,self.executionpath,dirname,modelname))
      else:
        fid.write('"%s/%s" %s "%s/%s" %s 2> %s.errlog >%s.outlog' % \
          (self.codepath,executable,solution,self.executionpath,dirname,modelname,modelname,modelname))
      fid.close()

    #in interactive mode, create a run file, and errlog and outlog file
    if self.interactive:
      fid=open(modelname+'.errlog','w')
      fid.close()
      fid=open(modelname+'.outlog','w')
      fid.close()
  # }}}
  def BuildKrigingQueueScript(self,modelname,solution,io_gather,isvalgrind,isgprof):    # {{{

    #write queuing script 
    if not m.ispc():

      fid=open(modelname+'.queue','w')
      fid.write('#!/bin/sh\n')
      if not isvalgrind:
        if self.interactive:
          fid.write('mpiexec -np %i %s/kriging.exe %s/%s %s ' % (self.np,self.codepath,self.executionpath,modelname,modelname))
        else:
          fid.write('mpiexec -np %i %s/kriging.exe %s/%s %s 2> %s.errlog >%s.outlog ' % (self.np,self.codepath,self.executionpath,modelname,modelname,modelname,modelname))
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
    #issmscpout(self.name,self.executionpath,self.login,self.port,[dirname+'.tar.gz'])

  # }}}
  def LaunchQueueJob(self,modelname,dirname,filelist,restart,batch):    # {{{

    print 'launching solution sequence on remote cluster'
    if restart:
      launchcommand='cd %s && cd %s chmod 777 %s.queue && ./%s.queue' % (self.executionpath,dirname,modelname,modelname)
    else:
      if batch:
        launchcommand='cd %s && rm -rf ./%s && mkdir %s && cd %s && mv ../%s.tar.gz ./ && tar -zxf %s.tar.gz' % \
            (self.executionpath,dirname,dirname,dirname,dirname,dirname)
      else:
        launchcommand='cd %s && rm -rf ./%s && mkdir %s && cd %s && mv ../%s.tar.gz ./ && tar -zxf %s.tar.gz  && chmod 777 %s.queue && ./%s.queue' % \
          (self.executionpath,dirname,dirname,dirname,dirname,dirname,modelname,modelname)
    issmssh(self.name,self.login,self.port,launchcommand)
  # }}}
  def Download(self,dirname,filelist):     # {{{

    if m.ispc():
      #do nothing
      return

    #copy files from cluster to current directory
    directory='%s/%s/' % (self.executionpath,dirname)
    issmscpin(self.name,self.login,self.port,directory,filelist)
  # }}}
