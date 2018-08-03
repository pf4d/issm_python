from issm.fielddisplay import fielddisplay
from issm.project3d import project3d
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class calving(object):
	"""
	CALVING class definition

	   Usage:
	      calving=calving();
	"""

	def __init__(self): # {{{

		self.calvingrate   = float('NaN')
		self.meltingrate   = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   Calving parameters:'
		string="%s\n%s"%(string,fielddisplay(self,'calvingrate','calving rate at given location [m/a]'))
		string="%s\n%s"%(string,fielddisplay(self,'meltingrate','melting rate at given location [m/a]'))

		return string
		#}}}
	def extrude(self,md): # {{{
		self.calvingrate=project3d(md,'vector',self.calvingrate,'type','node')
		self.meltingrate=project3d(md,'vector',self.meltingrate,'type','node')
		return self
	#}}}
	def setdefaultparameters(self): # {{{

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if (solution!='TransientSolution') or (not md.transient.ismovingfront):
			return md

		md = checkfield(md,'fieldname','calving.calvingrate','>=',0,'timeseries',1,'NaN',1,'Inf',1);
		md = checkfield(md,'fieldname','calving.meltingrate','>=',0,'timeseries',1,'NaN',1,'Inf',1);

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'name','md.calving.law','data',1,'format','Integer');
		WriteData(fid,prefix,'object',self,'fieldname','calvingrate','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','meltingrate','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts,'scale',1./yts)
	# }}}
