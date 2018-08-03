from issm.project3d import project3d
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class geometry(object):
	"""
	GEOMETRY class definition

	   Usage:
	      geometry=geometry();
	"""

	def __init__(self): # {{{
		self.surface           = float('NaN')
		self.thickness         = float('NaN')
		self.base               = float('NaN')
		self.bed        = float('NaN')
		self.hydrostatic_ratio = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{

		string="   geometry parameters:"
		string="%s\n%s"%(string,fielddisplay(self,'surface','ice upper surface elevation [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'thickness','ice thickness [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'base','ice base elevation [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'bed','bed elevation [m]'))
		return string
		#}}}
	def extrude(self,md): # {{{
		self.surface=project3d(md,'vector',self.surface,'type','node')
		self.thickness=project3d(md,'vector',self.thickness,'type','node')
		self.hydrostatic_ratio=project3d(md,'vector',self.hydrostatic_ratio,'type','node')
		self.base=project3d(md,'vector',self.base,'type','node')
		self.bed=project3d(md,'vector',self.bed,'type','node')
		return self
	#}}}
	def setdefaultparameters(self): # {{{
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		if (solution=='TransientSolution' and md.transient.isgia) or (solution=='GiaSolution'):
			md = checkfield(md,'fieldname','geometry.thickness','NaN',1,'Inf',1,'>=',0,'timeseries',1)
		else:
			md = checkfield(md,'fieldname','geometry.surface'  ,'NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','geometry.base'      ,'NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','geometry.thickness','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices],'>',0,'timeseries',1)
			if any(abs(self.thickness-self.surface+self.base)>10**-9):
				md.checkmessage("equality thickness=surface-base violated")
			if solution=='TransientSolution' and md.transient.isgroundingline:
				md = checkfield(md,'fieldname','geometry.bed','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'object',self,'fieldname','surface','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','thickness','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'fieldname','base','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','bed','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','hydrostatic_ratio','format','DoubleMat','mattype',1)
	# }}}
