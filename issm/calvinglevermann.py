from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class calvinglevermann(object):
	"""
	CALVINGLEVERMANN class definition

	   Usage:
	      calvinglevermann=calvinglevermann();
	"""

	def __init__(self): # {{{

		self.coeff         = float('NaN')
		self.meltingrate   = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   Calving Levermann parameters:'
		string="%s\n%s"%(string,fielddisplay(self,'coeff','proportionality coefficient in Levermann model'))
		string="%s\n%s"%(string,fielddisplay(self,'meltingrate','melting rate at given location [m/a]'))

		return string
		#}}}
	def extrude(self,md): # {{{
		self.coeff=project3d(md,'vector',self.coeff,'type','node')
		self.meltingrate=project3d(md,'vector',self.meltingrate,'type','node')
		return self
	#}}}
	def setdefaultparameters(self): # {{{

		#Proportionality coefficient in Levermann model
		self.coeff=2e13;
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if (solution!='TransientSolution') or (not md.transient.ismovingfront):
			return md

		md = checkfield(md,'fieldname','calving.coeff','size',[md.mesh.numberofvertices],'>',0)
		md = checkfield(md,'fieldname','calving.meltingrate','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices],'>=',0)
		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		yts=md.constants.yts
		WriteData(fid,prefix,'name','md.calving.law','data',3,'format','Integer');
		WriteData(fid,prefix,'object',self,'fieldname','coeff','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','meltingrate','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts,'scale',1./yts)
	# }}}
