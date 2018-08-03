import numpy as np
from issm.fielddisplay import fielddisplay
from issm.project3d import project3d
from issm.checkfield import checkfield
from issm.WriteData import WriteData
import issm.MatlabFuncs as m

class mask(object):
	"""
	MASK class definition

	   Usage:
	      mask=mask();
	"""

	def __init__(self): # {{{
		self.ice_levelset         = float('NaN')
		self.groundedice_levelset = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string="   masks:"

		string="%s\n%s"%(string,fielddisplay(self,"groundedice_levelset","is ice grounded ? grounded ice if > 0, grounding line position if = 0, floating ice if < 0"))
		string="%s\n%s"%(string,fielddisplay(self,"ice_levelset","presence of ice if < 0, icefront position if = 0, no ice if > 0"))
		return string
		#}}}
	def extrude(self,md): # {{{
		self.ice_levelset=project3d(md,'vector',self.ice_levelset,'type','node')
		self.groundedice_levelset=project3d(md,'vector',self.groundedice_levelset,'type','node')
		return self
	#}}}
	def setdefaultparameters(self): # {{{
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		md = checkfield(md,'fieldname','mask.ice_levelset'        ,'size',[md.mesh.numberofvertices])
		isice=np.array(md.mask.ice_levelset<=0,int)
		if np.sum(isice)==0:
			raise TypeError("no ice present in the domain")

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'object',self,'fieldname','groundedice_levelset','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','ice_levelset','format','DoubleMat','mattype',1)
	# }}}
