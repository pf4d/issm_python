from fielddisplay import fielddisplay
from checkfield import checkfield
from WriteData import WriteData

class timestepping(object):
	"""
	TIMESTEPPING Class definition

	   Usage:
	      timestepping=timestepping();
	"""

	def __init__(self): # {{{
		self.start_time      = 0.
		self.final_time      = 0.
		self.time_step       = 0.
		self.time_adapt      = 0
		self.cfl_coefficient = 0.
		self.interp_forcings = 1
		
		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string="   timestepping parameters:"
		string="%s\n%s"%(string,fielddisplay(self,"start_time","simulation starting time [yr]"))
		string="%s\n%s"%(string,fielddisplay(self,"final_time","final time to stop the simulation [yr]"))
		string="%s\n%s"%(string,fielddisplay(self,"time_step","length of time steps [yr]"))
		string="%s\n%s"%(string,fielddisplay(self,"time_adapt","use cfl condition to define time step ? (0 or 1) "))
		string="%s\n%s"%(string,fielddisplay(self,"cfl_coefficient","coefficient applied to cfl condition"))
		string="%s\n%s"%(string,fielddisplay(self,"interp_forcings","interpolate in time between requested forcing values ? (0 or 1)"))
		return string
		#}}}
	def setdefaultparameters(self): # {{{
		
		#time between 2 time steps
		self.time_step=1./2.

		#final time
		self.final_time=10.*self.time_step

		#time adaptation? 
		self.time_adapt=0
		self.cfl_coefficient=0.5
		
		#should we interpolate forcings between timesteps?
		self.interp_forcings=1

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		md = checkfield(md,'fieldname','timestepping.start_time','numel',[1],'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','timestepping.final_time','numel',[1],'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','timestepping.time_step','numel',[1],'>=',0,'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','timestepping.time_adapt','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','timestepping.cfl_coefficient','numel',[1],'>',0,'<=',1)
		if self.final_time-self.start_time<0:
			md.checkmessage("timestepping.final_time should be larger than timestepping.start_time")
		md = checkfield(md,'fieldname','timestepping.interp_forcings','numel',[1],'values',[0,1])

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts
		WriteData(fid,prefix,'object',self,'fieldname','start_time','format','Double','scale',yts)
		WriteData(fid,prefix,'object',self,'fieldname','final_time','format','Double','scale',yts)
		WriteData(fid,prefix,'object',self,'fieldname','time_step','format','Double','scale',yts)
		WriteData(fid,prefix,'object',self,'fieldname','time_adapt','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','cfl_coefficient','format','Double')
		WriteData(fid,prefix,'object',self,'fieldname','interp_forcings','format','Boolean')
	# }}}
