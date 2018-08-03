from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData
from issm.project3d import project3d

class SMBgradients(object):
	"""
	SMBgradients Class definition

	   Usage:
	      SMBgradients=SMBgradients();
	"""

	def __init__(self): # {{{
		self.href    = float('NaN')
		self.smbref  = float('NaN')
		self.b_pos   = float('NaN')
		self.b_neg   = float('NaN')
		self.requested_outputs      = []
		#}}}
	def __repr__(self): # {{{
		string="   surface forcings parameters:"

		string="%s\n%s"%(string,fielddisplay(self,'issmbgradients','is smb gradients method activated (0 or 1, default is 0)'))
		string="%s\n%s"%(string,fielddisplay(self,'href',' reference elevation from which deviation is used to calculate SMB adjustment in smb gradients method'))
		string="%s\n%s"%(string,fielddisplay(self,'smbref',' reference smb from which deviation is calculated in smb gradients method'))
		string="%s\n%s"%(string,fielddisplay(self,'b_pos',' slope of hs - smb regression line for accumulation regime required if smb gradients is activated'))
		string="%s\n%s"%(string,fielddisplay(self,'b_neg',' slope of hs - smb regression line for ablation regime required if smb gradients is activated'))
		string="%s\n%s"%(string,fielddisplay(self,'requested_outputs','additional outputs requested'))

		return string
		#}}}
	def extrude(self,md): # {{{

		#Nothing for now
		return self
	#}}}
	def defaultoutputs(self,md): # {{{
		return []
	#}}}
	def initialize(self,md): # {{{

		#Nothing for now

		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		if 'MasstransportAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.href','timeseries',1,'NaN',1,'Inf',1)
			md = checkfield(md,'fieldname','smb.smbref','timeseries',1,'NaN',1,'Inf',1)
			md = checkfield(md,'fieldname','smb.b_pos','timeseries',1,'NaN',1,'Inf',1)
			md = checkfield(md,'fieldname','smb.b_neg','timeseries',1,'NaN',1,'Inf',1)

		md = checkfield(md,'fieldname','masstransport.requested_outputs','stringrow',1)
		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'name','md.smb.model','data',6,'format','Integer');
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','href','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','smbref','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','b_pos','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','b_neg','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
		
		#process requested outputs
		outputs = self.requested_outputs
		indices = [i for i, x in enumerate(outputs) if x == 'default']
		if len(indices) > 0:
			outputscopy=outputs[0:max(0,indices[0]-1)]+self.defaultoutputs(md)+outputs[indices[0]+1:]
			outputs    =outputscopy
		WriteData(fid,prefix,'data',outputs,'name','md.smb.requested_outputs','format','StringArray')

	# }}}
