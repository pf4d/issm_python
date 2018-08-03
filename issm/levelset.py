from issm.fielddisplay import fielddisplay
from issm.project3d import project3d
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class levelset(object):
	"""
	LEVELSET class definition

	   Usage:
	      levelset=levelset();
	"""

	def __init__(self): # {{{

		self.stabilization    = 0
		self.spclevelset      = float('NaN')
		self.reinit_frequency = 0
		self.calving_max      = 0.

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   Level-set parameters:'
		string="%s\n%s"%(string,fielddisplay(self,'stabilization','0: no, 1: artificial_diffusivity, 2: streamline upwinding'))
		string="%s\n%s"%(string,fielddisplay(self,'spclevelset','levelset constraints (NaN means no constraint)'))
		string="%s\n%s"%(string,fielddisplay(self,'reinit_frequency','Amount of time steps after which the levelset function in re-initialized'))
		string="%s\n%s"%(string,fielddisplay(self,'calving_max','maximum allowed calving rate (m/a)'))

		return string
		#}}}
	def extrude(self,md): # {{{
		self.spclevelset=project3d(md,'vector',self.spclevelset,'type','node')
		return self
	#}}}
	def setdefaultparameters(self): # {{{

		#stabilization = 2 by default
		self.stabilization = 2
		self.reinit_frequency = 5
		self.calving_max      = 3000

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		#Early return
		if (solution!='TransientSolution') or (not md.transient.ismovingfront):
			return md

		md = checkfield(md,'fieldname','levelset.spclevelset','Inf',1,'timeseries',1)
		md = checkfield(md,'fieldname','levelset.stabilization','values',[0,1,2]);
		md = checkfield(md,'fieldname','levelset.calving_max','NaN',1,'Inf',1,'>',0);

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts;

		WriteData(fid,prefix,'object',self,'fieldname','stabilization','format','Integer');
		WriteData(fid,prefix,'object',self,'fieldname','spclevelset','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts);
		WriteData(fid,prefix,'object',self,'fieldname','reinit_frequency','format','Integer');
		WriteData(fid,prefix,'object',self,'fieldname','calving_max','format','Double','scale',1./yts);
	# }}}
