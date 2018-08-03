from fielddisplay import fielddisplay
from checkfield import checkfield
from WriteData import WriteData

class transient(object):
	"""
	TRANSIENT class definition

	   Usage:
	      transient=transient();
	"""

	def __init__(self): # {{{
		self.issmb   = False
		self.ismasstransport   = False
		self.isstressbalance   = False
		self.isthermal         = False
		self.isgroundingline   = False
		self.isgia             = False
		self.isesa             = False
		self.isdamageevolution = False
		self.ismovingfront     = False
		self.ishydrology       = False
		self.isslr             = False
		self.isoceancoupling   = False
		self.iscoupler         = False
		amr_frequency			  = 0
		self.requested_outputs = []

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   transient solution parameters:'
		string="%s\n%s"%(string,fielddisplay(self,'issmb','indicates if a surface mass balance solution is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'ismasstransport','indicates if a masstransport solution is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'isstressbalance','indicates if a stressbalance solution is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'isthermal','indicates if a thermal solution is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'isgroundingline','indicates if a groundingline migration is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'isgia','indicates if a postglacial rebound is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'isesa','indicates whether an elastic adjustment model is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'isdamageevolution','indicates whether damage evolution is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'ismovingfront','indicates whether a moving front capability is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'ishydrology','indicates whether an hydrology model is used'))
		string="%s\n%s"%(string,fielddisplay(self,'isslr','indicates if a sea level rise solution is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'isoceancoupling','indicates whether coupling with an ocean model is used in the transient'))
		string="%s\n%s"%(string,fielddisplay(self,'iscoupler','indicates whether different models are being run with need for coupling'))
		string="%s\n%s"%(string,fielddisplay(self,'amr_frequency','frequency at which mesh is refined in simulations with multiple time_steps'))
		string="%s\n%s"%(string,fielddisplay(self,'requested_outputs','list of additional outputs requested'))
		return string
		#}}}
	def defaultoutputs(self,md): # {{{

		if self.issmb:
			return ['SmbMassBalance']
		else:
			return []

	#}}}
	def setallnullparameters(self): # {{{
		
		#Nothing done
		self.issmb   = False
		self.ismasstransport   = False
		self.isstressbalance   = False
		self.isthermal         = False
		self.isgroundingline   = False
		self.isgia             = False
		self.isesa             = False
		self.isdamageevolution = False
		self.ismovingfront     = False
		self.ishydrology       = False
		self.isoceancoupling   = False
		self.isslr             = False
		self.iscoupler         = False
		self.amr_frequency	  = 0

		#default output
		self.requested_outputs=[]
		return self
	#}}}
	def setdefaultparameters(self): # {{{
		
		#full analysis: Stressbalance, Masstransport and Thermal but no groundingline migration for now
		self.issmb = True
		self.ismasstransport = True
		self.isstressbalance = True
		self.isthermal       = True
		self.isgroundingline = False
		self.isgia           = False
		self.isesa           = False
		self.isdamageevolution = False
		self.ismovingfront   = False
		self.ishydrology     = False
		self.isslr           = False
		self.isoceancoupling = False
		self.iscoupler       = False
		self.amr_frequency	= 1

		#default output
		self.requested_outputs=['default']
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if not solution=='TransientSolution':
			return md

		md = checkfield(md,'fieldname','transient.issmb','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.ismasstransport','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.isstressbalance','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.isthermal','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.isgroundingline','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.isgia','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.isesa','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.isdamageevolution','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.ishydrology','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.ismovingfront','numel',[1],'values',[0,1]);
		md = checkfield(md,'fieldname','transient.isslr','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.isoceancoupling','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.iscoupler','numel',[1],'values',[0,1])
		md = checkfield(md,'fieldname','transient.amr_frequency','numel',[1],'>=',0,'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','transient.requested_outputs','stringrow',1)

		if (solution!='TransientSolution') and (md.transient.iscoupling):
				md.checkmessage("Coupling with ocean can only be done in transient simulations!")

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'object',self,'fieldname','issmb','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','ismasstransport','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isstressbalance','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isthermal','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isgroundingline','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isgia','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isesa','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isdamageevolution','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','ishydrology','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','ismovingfront','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isslr','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','isoceancoupling','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','iscoupler','format','Boolean')
		WriteData(fid,prefix,'object',self,'fieldname','amr_frequency','format','Integer')

		#process requested outputs
		outputs = self.requested_outputs
		indices = [i for i, x in enumerate(outputs) if x == 'default']
		if len(indices) > 0:
			outputscopy=outputs[0:max(0,indices[0]-1)]+self.defaultoutputs(md)+outputs[indices[0]+1:]
			outputs    =outputscopy
		WriteData(fid,prefix,'data',outputs,'name','md.transient.requested_outputs','format','StringArray')
	# }}}
