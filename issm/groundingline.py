import numpy as np
from fielddisplay import fielddisplay
from checkfield import checkfield
from WriteData import WriteData
import MatlabFuncs as m

class groundingline(object):
	"""
	GROUNDINGLINE class definition

	   Usage:
	      groundingline=groundingline();
	"""

	def __init__(self): # {{{
		self.migration=''

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   grounding line migration parameters:'

		string="%s\n%s"%(string,fielddisplay(self,'migration','type of grounding line migration: ''SoftMigration'',''AggressiveMigration'',''SubelementMigration'',''SubelementMigration2'',''Contact'',''None'''))
		return string
		#}}}	
	def setdefaultparameters(self): # {{{

		#Type of migration
		self.migration='None'

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		md = checkfield(md,'fieldname','groundingline.migration','values',['None','AggressiveMigration','SoftMigration','SubelementMigration','SubelementMigration2','Contact','GroundingOnly'])

		if not m.strcmp(self.migration,'None'):
			if np.any(np.isnan(md.geometry.bed)):
				md.checkmessage("requesting grounding line migration, but bathymetry is absent!")
			pos=np.nonzero(md.mask.groundedice_levelset>0.)[0]
			if any(np.abs(md.geometry.base[pos]-md.geometry.bed[pos])>10**-10):
				md.checkmessage("base not equal to bed on grounded ice!")
			if any(md.geometry.bed - md.geometry.base > 10**-9):
				md.checkmessage("bed superior to base on floating ice!")

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		WriteData(fid,prefix,'data',self.migration,'name','md.groundingline.migration','format','String')
	# }}}
