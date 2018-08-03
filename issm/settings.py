from fielddisplay import fielddisplay
from checkfield import checkfield
from WriteData import WriteData

class settings(object):
	"""
	SETTINGS class definition

	   Usage:
	      settings=settings();
	"""

	def __init__(self): # {{{
		self.results_on_nodes    = 0
		self.io_gather           = 0
		self.lowmem              = 0
		self.output_frequency    = 0
		self.recording_frequency = 0
		self.waitonlock          = 0
		self.solver_residue_threshold = 0

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string="   general settings parameters:"

		string="%s\n%s"%(string,fielddisplay(self,"results_on_nodes","results are output for all the nodes of each element"))
		string="%s\n%s"%(string,fielddisplay(self,"io_gather","I/O gathering strategy for result outputs (default 1)"))
		string="%s\n%s"%(string,fielddisplay(self,"lowmem","is the memory limited ? (0 or 1)"))
		string="%s\n%s"%(string,fielddisplay(self,"output_frequency","frequency at which results are saved in all solutions with multiple time_steps"))
		string="%s\n%s"%(string,fielddisplay(self,"recording_frequency","frequency at which the runs are being recorded, allowing for a restart"))
		string="%s\n%s"%(string,fielddisplay(self,"waitonlock","maximum number of minutes to wait for batch results, or return 0"))
		string="%s\n%s"%(string,fielddisplay(self,"solver_residue_threshold","throw an error if solver residue exceeds this value (NaN to deactivate)"))
		return string
		#}}}
	def setdefaultparameters(self): # {{{
		
		#are we short in memory ? (0 faster but requires more memory)
		self.lowmem=0

		#i/o:
		self.io_gather=1

		#results frequency by default every step
		self.output_frequency=1

		#checkpoints frequency, by default never: 
		self.recording_frequency=0


		#this option can be activated to load automatically the results
		#onto the model after a parallel run by waiting for the lock file
		#N minutes that is generated once the solution has converged
		#0 to deactivate
		self.waitonlock=2**31-1

      #throw an error if solver residue exceeds this value
		self.solver_residue_threshold=1e-6;

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{
		md = checkfield(md,'fieldname','settings.results_on_nodes','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','settings.io_gather','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','settings.lowmem','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','settings.output_frequency','numel',[1],'>=',1)
		md = checkfield(md,'fieldname','settings.recording_frequency','numel',[1],'>=',0)
		md = checkfield(md,'fieldname','settings.waitonlock','numel',[1])
		md = checkfield(md,'fieldname','settings.solver_residue_threshold','numel',[1],'>',0)

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'object',self,'fieldname','results_on_nodes','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','io_gather','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','lowmem','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','output_frequency','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','recording_frequency','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','solver_residue_threshold','format','Double')
		if self.waitonlock>0:
			WriteData(fid,prefix,'name','md.settings.waitonlock','data',True,'format','Boolean');
		else:
			WriteData(fid,prefix,'name','md.settings.waitonlock','data',False,'format','Boolean');
	# }}}
