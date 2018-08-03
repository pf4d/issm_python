import numpy as np
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData
from issm.project3d import project3d

class SMBd18opdd(object):
	"""
	SMBd18opdd Class definition

	   Usage:
	      SMBd18opdd=SMBd18opdd();
	"""

	def __init__(self): # {{{
		self.desfac                    = 0.
		self.s0p                       = float('NaN')
		self.s0t                       = float('NaN')
		self.rlaps                     = 0.
		self.rlapslgm                  = 0.
		self.dpermil                   = 0.
		self.f                         = 0.
		self.Tdiff                     = float('NaN')
		self.sealev                    = float('NaN')
		self.ismungsm                  = 0
		self.isd18opd                  = 0
		self.delta18o                  = float('NaN')
		self.delta18o_surface          = float('NaN')
		self.temperatures_presentday   = float('NaN')
		self.precipitations_presentday = float('NaN')

		#set defaults
		self.setdefaultparameters()
		self.requested_outputs      = []
		#}}}
	def __repr__(self): # {{{
		string="   surface forcings parameters:"

		string="%s\n%s"%(string,fielddisplay(self,'isd18opd','is delta18o parametrisation from present day temperature and precipitation activated (0 or 1, default is 0)'))
		string="%s\n%s"%(string,fielddisplay(self,'desfac','desertification elevation factor (between 0 and 1, default is 0.5) [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'s0p','should be set to elevation from precip source (between 0 and a few 1000s m, default is 0) [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'s0t','should be set to elevation from temperature source (between 0 and a few 1000s m, default is 0) [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'rlaps','present day lapse rate [degree/km]'))
		if self.isd18opd:
			string="%s\n%s"%(string,fielddisplay(self,'temperatures_presentday','monthly present day surface temperatures [K], required if delta18o/mungsm is activated'))
			string="%s\n%s"%(string,fielddisplay(self,'precipitations_presentday','monthly surface precipitation [m/yr water eq], required if delta18o or mungsm is activated'))
			string="%s\n%s"%(string,fielddisplay(self,'delta18o','delta18o [per mil], required if pdd is activated and delta18o activated'))
			string="%s\n%s"%(string,fielddisplay(self,'dpermil','degree per mil, required if d18opd is activated'))
		string="%s\n%s"%(string,fielddisplay(self,'requested_outputs','additional outputs requested'))

		return string
		#}}}
	def extrude(self,md): # {{{

		if self.isd18opd: self.temperatures_presentday=project3d(md,'vector',self.temperatures_presentday,'type','node')
		if self.isd18opd: self.precipitations_presentday=project3d(md,'vector',self.precipitations_presentday,'type','node')
		self.s0p=project3d(md,'vector',self.s0p,'type','node')
		self.s0t=project3d(md,'vector',self.s0t,'type','node')

		return self
	#}}}
	def defaultoutputs(self,md): # {{{
		return []
	#}}}
	def initialize(self,md): # {{{

		if np.all(np.isnan(self.s0p)):
			self.s0p=np.zeros((md.mesh.numberofvertices))
			print "      no SMBd18opdd.s0p specified: values set as zero"

		if np.all(np.isnan(self.s0t)):
			self.s0t=np.zeros((md.mesh.numberofvertices))
			print "      no SMBd18opdd.s0t specified: values set as zero"
			
		return self
	# }}}
	def setdefaultparameters(self): # {{{

		#pdd method not used in default mode
		self.ismungsm   = 0
		self.isd18opd   = 1
		self.desfac     = 0.5
		self.rlaps      = 6.5 
		self.rlapslgm   = 6.5
		self.dpermil    = 2.4
		self.f          = 0.169
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{

		if 'MasstransportAnalysis' in analyses:
			md = checkfield(md,'fieldname','smb.desfac','<=',1,'numel',[1])
			md = checkfield(md,'fieldname','smb.s0p','>=',0,'NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','smb.s0t','>=',0,'NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','smb.rlaps','>=',0,'numel',[1])
			md = checkfield(md,'fieldname','smb.rlapslgm','>=',0,'numel',[1])

			if self.isd18opd:
				md = checkfield(md,'fieldname','smb.temperatures_presentday','size',[md.mesh.numberofvertices+1,12],'NaN',1,'Inf',1,'timeseries',1)
				md = checkfield(md,'fieldname','smb.precipitations_presentday','size',[md.mesh.numberofvertices+1,12],'NaN',1,'Inf',1,'timeseries',1)
				md = checkfield(md,'fieldname','smb.delta18o','NaN',1,'Inf',1,'size',[2,np.nan],'singletimeseries',1)
				md = checkfield(md,'fieldname','smb.dpermil','>=',0,'numel',[1])
				md = checkfield(md,'fieldname','smb.f','>=',0,'numel',[1])

		md = checkfield(md,'fieldname','masstransport.requested_outputs','stringrow',1)

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'name','md.smb.model','data',5,'format','Integer')

		WriteData(fid,prefix,'object',self,'class','smb','fieldname','ismungsm','format','Boolean')
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','isd18opd','format','Boolean')
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','desfac','format','Double')
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','s0p','format','DoubleMat','mattype',1);
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','s0t','format','DoubleMat','mattype',1);
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','rlaps','format','Double')
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','rlapslgm','format','Double')
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','Tdiff','format','DoubleMat','mattype',1,'timeserieslength',2,'yts',md.constants.yts)
		WriteData(fid,prefix,'object',self,'class','smb','fieldname','sealev','format','DoubleMat','mattype',1,'timeserieslength',2,'yts',md.constants.yts)

		if self.isd18opd:
			WriteData(fid,prefix,'object',self,'class','smb','fieldname','temperatures_presentday','format','DoubleMat','mattype',1,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
			WriteData(fid,prefix,'object',self,'class','smb','fieldname','precipitations_presentday','format','DoubleMat','mattype',1,'scale',1./yts,'timeserieslength',md.mesh.numberofvertices+1,'yts',md.constants.yts)
			WriteData(fid,prefix,'object',self,'class','smb','fieldname','delta18o','format','DoubleMat','mattype',1,'timeserieslength',2,'yts',md.constants.yts)
			WriteData(fid,prefix,'object',self,'class','smb','fieldname','dpermil','format','Double')
			WriteData(fid,prefix,'object',self,'class','smb','fieldname','f','format','Double')
		#process requested outputs
		outputs = self.requested_outputs
		indices = [i for i, x in enumerate(outputs) if x == 'default']
		if len(indices) > 0:
			outputscopy=outputs[0:max(0,indices[0]-1)]+self.defaultoutputs(md)+outputs[indices[0]+1:]
			outputs    =outputscopy
		WriteData(fid,prefix,'data',outputs,'name','md.smb.requested_outputs','format','StringArray')

	# }}}
