from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class balancethickness(object):
	"""
	BALANCETHICKNESS class definition

	   Usage:
	      balancethickness=balancethickness();
	"""

	def __init__(self): # {{{
		self.spcthickness      = float('NaN')
		self.thickening_rate   = float('NaN')
		self.stabilization     = 0

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		
		string='   balance thickness solution parameters:' 
		
		string="%s\n%s"%(string,fielddisplay(self,'spcthickness','thickness constraints (NaN means no constraint) [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'thickening_rate','ice thickening rate used in the mass conservation (dh/dt) [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'stabilization',"0: None, 1: SU, 2: SSA's artificial diffusivity, 3:DG"))
		return string
		#}}}
	def setdefaultparameters(self): # {{{
		
		#Type of stabilization used
		self.stabilization=1

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{
		#Early return
		if not solution=='BalancethicknessSolution':
			return md

		md = checkfield(md,'fieldname','balancethickness.spcthickness')
		md = checkfield(md,'fieldname','balancethickness.thickening_rate','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)
		md = checkfield(md,'fieldname','balancethickness.stabilization','size',[1],'values',[0,1,2,3])

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'object',self,'fieldname','spcthickness','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','thickening_rate','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','stabilization','format','Integer')
	# }}}
