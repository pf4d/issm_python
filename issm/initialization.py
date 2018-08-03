import numpy as np
from issm.project3d import project3d
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData
import issm.MatlabFuncs as m

class initialization(object):
	"""
	INITIALIZATION class definition
	
	Usage:
	initialization=initialization();
	"""

	def __init__(self): # {{{
					
		self.vx            = float('NaN')
		self.vy            = float('NaN')
		self.vz            = float('NaN')
		self.vel           = float('NaN')
		self.pressure      = float('NaN')
		self.temperature   = float('NaN')
		self.waterfraction = float('NaN')
		self.watercolumn   = float('NaN')
		self.sediment_head = float('NaN')
		self.epl_head      = float('NaN')
		self.epl_thickness = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#}}}
	def __repr__(self): # {{{
		string='   initial field values:'
		string="%s\n%s"%(string,fielddisplay(self,'vx','x component of velocity [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'vy','y component of velocity [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'vz','z component of velocity [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'vel','velocity norm [m/yr]'))
		string="%s\n%s"%(string,fielddisplay(self,'pressure','pressure [Pa]'))
		string="%s\n%s"%(string,fielddisplay(self,'temperature','temperature [K]'))
		string="%s\n%s"%(string,fielddisplay(self,'waterfraction','fraction of water in the ice'))
		string="%s\n%s"%(string,fielddisplay(self,'watercolumn','thickness of subglacial water [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'sediment_head','sediment water head of subglacial system [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'epl_head','epl water head of subglacial system [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'epl_thickness','thickness of the epl [m]'))

		return string
		#}}}
	def extrude(self,md): # {{{
		self.vx=project3d(md,'vector',self.vx,'type','node')
		self.vy=project3d(md,'vector',self.vy,'type','node')
		self.vz=project3d(md,'vector',self.vz,'type','node')
		self.vel=project3d(md,'vector',self.vel,'type','node')
		self.temperature=project3d(md,'vector',self.temperature,'type','node')
		self.waterfraction=project3d(md,'vector',self.waterfraction,'type','node')
		self.watercolumn=project3d(md,'vector',self.watercolumn,'type','node')
		self.sediment_head=project3d(md,'vector',self.sediment_head,'type','node','layer',1)
		self.epl_head=project3d(md,'vector',self.epl_head,'type','node','layer',1)
		self.epl_thickness=project3d(md,'vector',self.epl_thickness,'type','node','layer',1)

		#Lithostatic pressure by default
		#		self.pressure=md.constants.g*md.materials.rho_ice*(md.geometry.surface[:,0]-md.mesh.z)
		#self.pressure=md.constants.g*md.materials.rho_ice*(md.geometry.surface-md.mesh.z.reshape(-1,))

		if np.ndim(md.geometry.surface)==2:
			print('Reshaping md.geometry.surface for you convenience but you should fix it in you files')
			self.pressure=md.constants.g*md.materials.rho_ice*(md.geometry.surface.reshape(-1,)-md.mesh.z)
		else:
			self.pressure=md.constants.g*md.materials.rho_ice*(md.geometry.surface-md.mesh.z)

		return self
	#}}}
	def setdefaultparameters(self): # {{{
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{
		if 'StressbalanceAnalysis' in analyses:
			if not np.any(np.logical_or(np.isnan(md.initialization.vx),np.isnan(md.initialization.vy))):
				md = checkfield(md,'fieldname','initialization.vx','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
				md = checkfield(md,'fieldname','initialization.vy','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		if 'MasstransportAnalysis' in analyses:
			md = checkfield(md,'fieldname','initialization.vx','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','initialization.vy','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		if 'BalancethicknessAnalysis' in analyses:
			md = checkfield(md,'fieldname','initialization.vx','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','initialization.vy','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			#Triangle with zero velocity
			if np.any(np.logical_and(np.sum(np.abs(md.initialization.vx[md.mesh.elements-1]),axis=1)==0,\
			                               np.sum(np.abs(md.initialization.vy[md.mesh.elements-1]),axis=1)==0)):
				md.checkmessage("at least one triangle has all its vertices with a zero velocity")
		if 'ThermalAnalysis' in analyses:
			md = checkfield(md,'fieldname','initialization.vx','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','initialization.vy','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','initialization.temperature','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			if md.mesh.dimension()==3:
				md = checkfield(md,'fieldname','initialization.vz','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			md = checkfield(md,'fieldname','initialization.pressure','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
			if ('EnthalpyAnalysis' in analyses and md.thermal.isenthalpy):
				md = checkfield(md,'fieldname','initialization.waterfraction','>=',0,'size',[md.mesh.numberofvertices])
				md = checkfield(md,'fieldname','initialization.watercolumn'  ,'>=',0,'size',[md.mesh.numberofvertices])
				pos = np.nonzero(md.initialization.waterfraction > 0.)[0]
				if(pos.size):
					md = checkfield(md,'fieldname', 'delta Tpmp', 'field', np.absolute(md.initialization.temperature[pos]-(md.materials.meltingpoint-md.materials.beta*md.initialization.pressure[pos])),'<',1e-11,	'message','set temperature to pressure melting point at locations with waterfraction>0');
		if 'HydrologyShreveAnalysis' in analyses:
			if hasattr(md.hydrology,'hydrologyshreve'):
				md = checkfield(md,'fieldname','initialization.watercolumn','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		if 'HydrologyDCInefficientAnalysis' in analyses:
			if hasattr(md.hydrology,'hydrologydc'):
				md = checkfield(md,'fieldname','initialization.sediment_head','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		if 'HydrologyDCEfficientAnalysis' in analyses:
			if hasattr(md.hydrology,'hydrologydc'):
				if md.hydrology.isefficientlayer==1:
					md = checkfield(md,'fieldname','initialization.epl_head','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
					md = checkfield(md,'fieldname','initialization.epl_thickness','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{

		yts=md.constants.yts

		WriteData(fid,prefix,'object',self,'fieldname','vx','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','vy','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','vz','format','DoubleMat','mattype',1,'scale',1./yts)
		WriteData(fid,prefix,'object',self,'fieldname','pressure','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','temperature','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','waterfraction','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','sediment_head','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','epl_head','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','epl_thickness','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','watercolumn','format','DoubleMat','mattype',1)
		
		if md.thermal.isenthalpy:
			tpmp = md.materials.meltingpoint - md.materials.beta*md.initialization.pressure;
			pos  = np.nonzero(md.initialization.waterfraction > 0.)[0]
			enthalpy      = md.materials.heatcapacity*(md.initialization.temperature-md.constants.referencetemperature);
			enthalpy[pos] = md.materials.heatcapacity*(tpmp[pos].reshape(-1,) - md.constants.referencetemperature) + md.materials.latentheat*md.initialization.waterfraction[pos].reshape(-1,)
			WriteData(fid,prefix,'data',enthalpy,'format','DoubleMat','mattype',1,'name','md.initialization.enthalpy');

	# }}}
