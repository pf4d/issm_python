from issm.MatlabFuncs import *
from issm.model import *
import numpy as np
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class mesh3dsurface(object):
#MESH3DSURFACE class definition
#
#   Usage:
#      mesh3dsurface=mesh3dsurface();
	def __init__(self,*args): # {{{
		self.x                           = np.nan
		self.y                           = np.nan
		self.z                           = np.nan
		self.elements                    = np.nan
		self.numberofelements            = 0
		self.numberofvertices            = 0
		self.numberofedges               = 0

		self.lat                         = np.nan
		self.long                        = np.nan
		self.r                           = np.nan

		self.vertexonboundary            = np.nan
		self.edges                       = np.nan
		self.segments                    = np.nan
		self.segmentmarkers              = np.nan
		self.vertexconnectivity          = np.nan
		self.elementconnectivity         = np.nan
		self.average_vertex_connectivity = 0

		self.extractedvertices           = np.nan
		self.extractedelements           = np.nan
		
		if not len(args):
			self.setdefaultparameters()
		elif len(args)==1:
			self=mesh3dsurface()
			arg=args[1]
			fields=fieldnames(arg)
			for i in range(len(fields)):
				field=fields[i]
				if ismember(field,properties('mesh3dsurface')):
					self.field=arg.field
		else:
			raise RuntimeError('constructor not supported')	

	# }}}
	def __repr__(self): # {{{
		string='   2D tria Mesh (horizontal):'
		
		string+='\n      Elements and vertices:'
		string="%s\n%s"%(string,fielddisplay(self,'numberofelements','number of elements'))
		string="%s\n%s"%(string,fielddisplay(self,'numberofvertices','number of vertices'))
		string="%s\n%s"%(string,fielddisplay(self,'elements','vertex indices of the mesh elements'))
		string="%s\n%s"%(string,fielddisplay(self,'x','vertices x coordinate [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'y','vertices y coordinate [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'z','vertices z coordinate [m]'))
		string="%s\n%s"%(string,fielddisplay(self,'lat','vertices latitude [degrees]'))
		string="%s\n%s"%(string,fielddisplay(self,'long','vertices longitude [degrees]'))
		string="%s\n%s"%(string,fielddisplay(self,'r','vertices radius [m]'))
		
		string="%s\n%s"%(string,fielddisplay(self,'edges','edges of the 2d mesh (vertex1 vertex2 element1 element2)'))
		string="%s\n%s"%(string,fielddisplay(self,'numberofedges','number of edges of the 2d mesh'))

		string+='\n      Properties:'
		string="%s\n%s"%(string,fielddisplay(self,'vertexonboundary','vertices on the boundary of the domain flag list'))
		string="%s\n%s"%(string,fielddisplay(self,'segments','edges on domain boundary (vertex1 vertex2 element)'))
		string="%s\n%s"%(string,fielddisplay(self,'segmentmarkers','number associated to each segment'))
		string="%s\n%s"%(string,fielddisplay(self,'vertexconnectivity','list of vertices connected to vertex_i'))
		string="%s\n%s"%(string,fielddisplay(self,'elementconnectivity','list of vertices connected to element_i'))
		string="%s\n%s"%(string,fielddisplay(self,'average_vertex_connectivity','average number of vertices connected to one vertex'))

		string+='\n      Extracted model():'
		string="%s\n%s"%(string,fielddisplay(self,'extractedvertices','vertices extracted from the model()'))
		string="%s\n%s"%(string,fielddisplay(self,'extractedelements','elements extracted from the model()')) 
		
		return string
	# }}}
	def loadobj(self): # {{{
		# This def is directly called by matlab when a model() selfect is
		# loaded. Update old properties here

		#2014 Oct. 1st
		if isstruct(self):
			oldself=self
			#Assign property values from struct
			self=structtoobj(mesh3dsurface(),oldself)
			if isfield(oldself,'hemisphere'):
				print ('md.mesh.hemisphere has been automatically converted to EPSG code')
				if strcmpi(oldself.hemisphere,'n'):
					self.epsg=3413
				else:
					self.epsg=3031
		return self
	# }}}
	def setdefaultparameters(self): # {{{

		#the connectivity is the averaged number of nodes linked to a
		#given node through an edge. This connectivity is used to initially
		#allocate memory to the stiffness matrix. A value of 16 seems to
		#give a good memory/time ration. This value can be checked in
		#trunk/test/Miscellaneous/runme.m
		self.average_vertex_connectivity=25
		return self
	# }}}
	def checkconsistency(self,md,solution,analyses): # {{{

		md = checkfield(md,'fieldname','mesh.x','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mesh.y','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mesh.z','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mesh.lat','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mesh.long','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mesh.r','NaN',1,'Inf',1,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mesh.elements','NaN',1,'Inf',1,'>',0,'values',np.arange(1,md.mesh.numberofvertices+1))
		md = checkfield(md,'fieldname','mesh.elements','size',[md.mesh.numberofelements,3])
		if np.any(np.logical_not(np.in1d(np.arange(1,md.mesh.numberofvertices+1),md.mesh.elements.flat))):
			md = checkmessage(md,'orphan nodes have been found. Check the mesh outline')
		
		md = checkfield(md,'fieldname','mesh.numberofelements','>',0)
		md = checkfield(md,'fieldname','mesh.numberofvertices','>',0)
		md = checkfield(md,'fieldname','mesh.average_vertex_connectivity','>=',9,'message','"mesh.average_vertex_connectivity" should be at least 9 in 2d')

		if (solution=='ThermalSolution'):
			md = checkmessage(md,'thermal not supported for 2d mesh');
			
		return md
	# }}}
	def marshall(self,prefix,md,fid): # {{{
		WriteData(fid,prefix,'name','md.mesh.domain_type','data','Domain' + self.domaintype(),'format','String')
		WriteData(fid,prefix,'name','md.mesh.domain_dimension','data',self.dimension(),'format','Integer')
		WriteData(fid,prefix,'name','md.mesh.elementtype','data',self.elementtype(),'format','String')
		WriteData(fid,prefix,'object',self,'fieldname','x','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','y','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','z','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','lat','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','long','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','r','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'name','md.mesh.z','data',np.zeros(md.mesh.numberofvertices),'format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'fieldname','elements','format','DoubleMat','mattype',2)
		WriteData(fid,prefix,'object',self,'fieldname','numberofelements','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','numberofvertices','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','average_vertex_connectivity','format','Integer')
		WriteData(fid,prefix,'object',self,'fieldname','vertexonboundary','format','DoubleMat','mattype',1)
	# }}}
	def domaintype(self): # {{{
		return '3Dsurface'
	# }}}
	def dimension(self): # {{{
		return 2
	# }}}
	def elementtype(self): # {{{
		return 'Tria'
	# }}}
	def processmesh(self,options): # {{{
	
		isplanet = 1
		is2d     = 0

		elements = self.elements
		x        = self.x
		y        = self.y
		z        = self.z
		return [x, y, z, elements, is2d, isplanet]
	# }}}
	def savemodeljs(self,fid,modelname): # {{{
	
		fid.write('#s.mesh=new mesh3dsurface()\n'%modelname)
		writejs1Darray(fid,[modelname, '.mesh.x'],self.x)
		writejs1Darray(fid,[modelname, '.mesh.y'],self.y)
		writejs1Darray(fid,[modelname, '.mesh.z'],self.z)
		writejs2Darray(fid,[modelname, '.mesh.elements'],self.elements)
		writejsdouble(fid,[modelname, '.mesh.numberofelements'],self.numberofelements)
		writejsdouble(fid,[modelname, '.mesh.numberofvertices'],self.numberofvertices)
		writejsdouble(fid,[modelname, '.mesh.numberofedges'],self.numberofedges)
		writejs1Darray(fid,[modelname, '.mesh.lat'],self.lat)
		writejs1Darray(fid,[modelname, '.mesh.long'],self.long)
		writejs1Darray(fid,[modelname, '.mesh.r'],self.r)
		writejs1Darray(fid,[modelname, '.mesh.vertexonboundary'],self.vertexonboundary)
		writejs2Darray(fid,[modelname, '.mesh.edges'],self.edges)
		writejs2Darray(fid,[modelname, '.mesh.segments'],self.segments)
		writejs2Darray(fid,[modelname, '.mesh.segmentmarkers'],self.segmentmarkers)
		writejs2Darray(fid,[modelname, '.mesh.vertexconnectivity'],self.vertexconnectivity)
		writejs2Darray(fid,[modelname, '.mesh.elementconnectivity'],self.elementconnectivity)
		writejsdouble(fid,[modelname, '.mesh.average_vertex_connectivity'],self.average_vertex_connectivity)
		writejs1Darray(fid,[modelname, '.mesh.extractedvertices'],self.extractedvertices)
		writejs1Darray(fid,[modelname, '.mesh.extractedelements'],self.extractedelements)

	# }}}
	
