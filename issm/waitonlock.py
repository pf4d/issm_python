import os
from socket import gethostname
import time
import MatlabFuncs as m

def waitonlock(md):
	"""
	WAITONLOCK - wait for a file
 
	   This routine will return when a file named 'filename' is written to disk.
	   If the time limit given in input is exceeded, return 0
 
	   Usage:
	      flag=waitonlock(md)
	"""

	#Get filename (lock file) and options
	executionpath=md.cluster.executionpath
	cluster=md.cluster.name
	login=md.cluster.login
	port=md.cluster.port
	timelimit=md.settings.waitonlock
	filename=os.path.join(executionpath,md.private.runtimename,md.miscellaneous.name+'.lock')

	#waitonlock will work if the lock is on the same machine only: 
	if not m.strcmpi(gethostname(),cluster):

		print 'solution launched on remote cluster. log in to detect job completion.'
		choice=raw_input('Is the job successfully completed? (y/n) ')
		if not m.strcmp(choice,'y'): 
			print 'Results not loaded... exiting' 
			flag=0
		else:
			flag=1

	#job is running on the same machine
	else:

		if 'interactive' in vars(md.cluster) and md.cluster.interactive:
			#We are in interactive mode, no need to check for job completion
			flag=1
			return flag
		#initialize time and file presence test flag
		etime=0
		ispresent=0
		print "waiting for '%s' hold on... (Ctrl+C to exit)" % filename

		#loop till file .lock exist or time is up
		while ispresent==0 and etime<timelimit:
			ispresent=os.path.exists(filename)
			time.sleep(1)
			etime+=1/60

		#build output
		if etime>timelimit:
			print 'Time limit exceeded. Increase md.settings.waitonlock'
			print 'The results must be loaded manually with md=loadresultsfromcluster(md).'
			raise RuntimeError('waitonlock error message: time limit exceeded.')
			flag=0
		else:
			flag=1

	return flag

