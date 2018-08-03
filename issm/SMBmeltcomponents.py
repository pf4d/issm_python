from issm.fielddisplay import fielddisplay
from issm.checkfield import *
from issm.project3d import *
from issm.WriteData import *

class SMBmeltcomponents(object):
	"""
	SMBmeltcomponents Class definition

	   Usage:
	      SMBmeltcomponents=SMBmeltcomponents();
	"""

	def __init__(self): # {{{
		self.accumulation = float('NaN')
		self.runoff = float('NaN')
		self.evaporation = float('NaN')
		self.requested_outputs      = []
		#}}}
	def __repr__(self): # {{{
		string="   surface forcings parameters with melt (SMB=accumulation-evaporation-melt+refreeze) :"
		string="%s\n%s"%(string,fielddisplay(self,'accumulation','accumulated snow [m/yr ice eq]'))
		string="%s\n%s"%(string,fielddisplay(self,'evaporation','mount of ice lost to evaporative processes [m/yr ice eq]'))
		string="%s\n%s"%(string,fielddisplay(self,'melt','amount of ice melt in the ice column [m/yr ice eq]'))
		string="%s\n%s"%(string,fielddisplay(self,'refreeze','amount of ice melt refrozen in the ice column [m/yr ice eq]'))
		string="%s\n%s"%(string,fielddisplay(self,'requested_outputs','additional outputs requested'))
		return string
		#}}}
	def extrude(self,md): # {{{

		self.mass_balance=project3d(md,'vector',self.accumulation,'type','node');
		self.mass_balance=project3d(md,'vector',self.evaporation,'type','node');
		self.mass_balance=project3d(md,'vector',self.melt,'type','node');
		self.mass_balance=project3d(md,'vector',self.refreeze,'type','node');
		return self
	#}}}
	def defaultoutputs(self,md): # {{{
		return []
	#}}}
	def initialize(self,md): # {{{

		if np.all(np.isnan(self.accumulation)):
			self.accumulation=np.zeros((md.mesh.numberofvertices))
			print "      no SMB.accumulation specified: values set as zero"

		if np.all(np.isnan(self.evaporation)):
			self.evaporation=np.zeros((md.mesh.numberofvertices))
			print "      no SMB.evaporation specified: values set as zero"

		if np.all(np.isnan(self.melt)):
			self.melt=np.zeros((md.mesh.numberofvertices))
			print "      no SMB.melt specified: values set as zero"

		if np.all(np.isnan(self.refreeze)):
			self.refreeze=np.zeros((md.mesh.numberofvertices))
			print "      no SMB.refreeze specified: values set as zero"

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		if 'MasstransportAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.accumulation','timeseries',1,'NaN',1,'Inf',1)

		if 'BalancethicknessAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.accumulation','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)

		if 'MasstransportAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.melt','timeseries',1,'NaN',1,'Inf',1)

		if 'BalancethicknessAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.melt','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)

		if 'MasstransportAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.refreeze','timeseries',1,'NaN',1,'Inf',1)

		if 'BalancethicknessAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.refreeze','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)

		if 'MasstransportAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.evaporation','timeseries',1,'NaN',1,'Inf',1)

		if 'BalancethicknessAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.evaporation','size',[md.mesh.numberofvertices],'NaN',1,'Inf',1)

		md = checkfield(md,'fieldname','masstransport.requested_outputs','stringrow',1)
		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'name','md.smb.model','data',3,'format','Integer');
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','accumulation','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','evaporation','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','melt','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','refreeze','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		
		#process requested outputs
		outputs = self.requested_outputs
		indices = [i for i, x in enumerate(outputs) if x == 'default']
		if len(indices) > 0:
			outputscopy=outputs[0:max(0,indices[0]-1)]+self.defaultoutputs(md)+outputs[indices[0]+1:]
			outputs    =outputscopy
		WriteData(fid,prefix,'data',outputs,'name','md.smb.requested_outputs','format','StringArray')

	# }}}
