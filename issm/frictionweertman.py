from issm.fielddisplay import fielddisplay
from issm.project3d import project3d
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class frictionweertman(object):
	"""
	FRICTIONWEERTMAN class definition

	   Usage:
	      frictionweertman=frictionweertman();
	"""

	def __init__(self): # {{{
		self.C = float('NaN')
		self.m = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string="Weertman sliding law parameters: Sigma_b = C^(-1/m) * |u_b|^(1/m-1) * u_b"

		string="%s\n%s"%(string,fielddisplay(self,"C","friction coefficient [SI]"))
		string="%s\n%s"%(string,fielddisplay(self,"m","m exponent"))
		return string
		#}}}
	def setdefaultparameters(self): # {{{
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if 'StressbalanceAnalysis' not in analyses and 'ThermalAnalysis' not in analyses:
			return md

		md = checkfield(md,'fieldname','friction.C','timeseries',1,'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','friction.m','NaN',1,'Inf',1,'size',[md.mesh.numberofelements])

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'name','md.friction.law','data',2,'format','Integer')
		WriteData(fid,prefix,'class','friction','object',self,'fieldname','C','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'class','friction','object',self,'fieldname','m','format','DoubleMat','mattype',2)
	# }}}
