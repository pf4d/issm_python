#module imports {{{
import numpy as np
import copy
import sys
from issm.mesh2d import mesh2d
from issm.mesh3dprisms import mesh3dprisms
from issm.mask import mask
from issm.geometry import geometry
from issm.constants import constants
from issm.SMBforcing import SMBforcing
from issm.SMBpdd import SMBpdd
from issm.SMBd18opdd import SMBd18opdd
from issm.SMBgradients import SMBgradients
from issm.SMBcomponents import SMBcomponents
from issm.SMBmeltcomponents import SMBmeltcomponents
from issm.basalforcings import basalforcings
from issm.matice import matice
from issm.levelset import levelset 
from issm.calving import calving
from issm.calvinglevermann import calvinglevermann
#from issm.calvingpi import calvingpi
from issm.damage import damage
from issm.friction import friction
from issm.flowequation import flowequation
from issm.timestepping import timestepping
from issm.initialization import initialization
from issm.rifts import rifts
from issm.slr import slr
from issm.debug import debug
from issm.verbose import verbose
from issm.settings import settings
from issm.toolkits import toolkits
from issm.generic import generic
from issm.pfe import pfe
from issm.vilje import vilje
from issm.hexagon import hexagon
from issm.cyclone import cyclone
from issm.balancethickness import balancethickness
from issm.stressbalance import stressbalance
from issm.groundingline import groundingline
from issm.hydrologyshreve import hydrologyshreve
from issm.hydrologydc import hydrologydc
from issm.masstransport import masstransport
from issm.thermal import thermal
from issm.steadystate import steadystate
from issm.transient import transient
from issm.giaivins import giaivins
from issm.autodiff import autodiff
from issm.inversion import inversion
from issm.outputdefinition import outputdefinition
from issm.qmu import qmu
from issm.amr import amr
from issm.results import results
from issm.radaroverlay import radaroverlay
from issm.miscellaneous import miscellaneous
from issm.private import private
from issm.mumpsoptions import mumpsoptions
from issm.iluasmoptions import iluasmoptions
from issm.project3d import project3d
from issm.project2d import project2d
from issm.FlagElements import FlagElements
from issm.NodeConnectivity import NodeConnectivity
from issm.ElementConnectivity import ElementConnectivity
from issm.contourenvelope import contourenvelope
from issm.DepthAverage import DepthAverage
import issm.MatlabFuncs as m
#}}}

class model(object):
	#properties
	def __init__(self):#{{{

		# classtype=model.properties
				
		# for classe in dict.keys(classtype):
		# 	print classe
		# 	self.__dict__[classe] = classtype[str(classe)]

		self.mesh             = mesh2d()
		self.mask             = mask()
		self.geometry         = geometry()
		self.constants        = constants()
		self.smb              = SMBforcing()
		self.basalforcings    = basalforcings()
		self.materials        = matice()
		self.damage           = damage()
		self.friction         = friction()
		self.flowequation     = flowequation()
		self.timestepping     = timestepping()
		self.initialization   = initialization()
		self.rifts            = rifts()
		self.slr              = slr()

		self.debug            = debug()
		self.verbose          = verbose()
		self.settings         = settings()
		self.toolkits         = toolkits()
		self.cluster          = generic()

		self.balancethickness = balancethickness()
		self.stressbalance    = stressbalance()
		self.groundingline    = groundingline()
		self.hydrology        = hydrologyshreve()
		self.masstransport    = masstransport()
		self.thermal          = thermal()
		self.steadystate      = steadystate()
		self.transient        = transient()
		self.levelset         = levelset()
		self.calving          = calving()
		self.gia              = giaivins()

		self.autodiff         = autodiff()
		self.inversion        = inversion()
		self.qmu              = qmu()
		self.amr					 = amr()

		self.results          = results()
		self.outputdefinition = outputdefinition()
		self.radaroverlay     = radaroverlay()
		self.miscellaneous    = miscellaneous()
		self.private          = private()
		#}}}
	def properties(self):    # {{{
		# ordered list of properties since vars(self) is random
		return ['mesh',\
		        'mask',\
		        'geometry',\
		        'constants',\
		        'smb',\
		        'basalforcings',\
		        'materials',\
		        'damage',\
		        'friction',\
		        'flowequation',\
		        'timestepping',\
		        'initialization',\
		        'rifts',\
		        'slr',\
		        'debug',\
		        'verbose',\
		        'settings',\
		        'toolkits',\
		        'cluster',\
		        'balancethickness',\
		        'stressbalance',\
		        'groundingline',\
		        'hydrology',\
		        'masstransport',\
		        'thermal',\
		        'steadystate',\
		        'transient',\
		        'levelset',\
		        'calving',\
					'gia',\
		        'autodiff',\
		        'inversion',\
		        'qmu',\
		        'amr',\
		        'outputdefinition',\
		        'results',\
		        'radaroverlay',\
		        'miscellaneous',\
		        'private']
	# }}}
	def __repr__(obj): #{{{
		#print "Here %s the number: %d" % ("is", 37)
		string="%19s: %-22s -- %s" % ("mesh","[%s,%s]" % ("1x1",obj.mesh.__class__.__name__),"mesh properties")
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("mask","[%s,%s]" % ("1x1",obj.mask.__class__.__name__),"defines grounded and floating elements"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("geometry","[%s,%s]" % ("1x1",obj.geometry.__class__.__name__),"surface elevation, bedrock topography, ice thickness,..."))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("constants","[%s,%s]" % ("1x1",obj.constants.__class__.__name__),"physical constants"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("smb","[%s,%s]" % ("1x1",obj.smb.__class__.__name__),"surface mass balance"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("basalforcings","[%s,%s]" % ("1x1",obj.basalforcings.__class__.__name__),"bed forcings"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("materials","[%s,%s]" % ("1x1",obj.materials.__class__.__name__),"material properties"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("damage","[%s,%s]" % ("1x1",obj.damage.__class__.__name__),"damage propagation laws"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("friction","[%s,%s]" % ("1x1",obj.friction.__class__.__name__),"basal friction/drag properties"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("flowequation","[%s,%s]" % ("1x1",obj.flowequation.__class__.__name__),"flow equations"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("timestepping","[%s,%s]" % ("1x1",obj.timestepping.__class__.__name__),"time stepping for transient models"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("initialization","[%s,%s]" % ("1x1",obj.initialization.__class__.__name__),"initial guess/state"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("rifts","[%s,%s]" % ("1x1",obj.rifts.__class__.__name__),"rifts properties"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("slr","[%s,%s]" % ("1x1",obj.slr.__class__.__name__),"slr forcings"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("debug","[%s,%s]" % ("1x1",obj.debug.__class__.__name__),"debugging tools (valgrind, gprof)"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("verbose","[%s,%s]" % ("1x1",obj.verbose.__class__.__name__),"verbosity level in solve"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("settings","[%s,%s]" % ("1x1",obj.settings.__class__.__name__),"settings properties"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("toolkits","[%s,%s]" % ("1x1",obj.toolkits.__class__.__name__),"PETSc options for each solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("cluster","[%s,%s]" % ("1x1",obj.cluster.__class__.__name__),"cluster parameters (number of cpus...)"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("balancethickness","[%s,%s]" % ("1x1",obj.balancethickness.__class__.__name__),"parameters for balancethickness solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("stressbalance","[%s,%s]" % ("1x1",obj.stressbalance.__class__.__name__),"parameters for stressbalance solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("groundingline","[%s,%s]" % ("1x1",obj.groundingline.__class__.__name__),"parameters for groundingline solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("hydrology","[%s,%s]" % ("1x1",obj.hydrology.__class__.__name__),"parameters for hydrology solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("masstransport","[%s,%s]" % ("1x1",obj.masstransport.__class__.__name__),"parameters for masstransport solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("thermal","[%s,%s]" % ("1x1",obj.thermal.__class__.__name__),"parameters for thermal solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("steadystate","[%s,%s]" % ("1x1",obj.steadystate.__class__.__name__),"parameters for steadystate solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("transient","[%s,%s]" % ("1x1",obj.transient.__class__.__name__),"parameters for transient solution"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("levelset","[%s,%s]" % ("1x1",obj.levelset.__class__.__name__),"parameters for moving boundaries (level-set method)"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("calving","[%s,%s]" % ("1x1",obj.calving.__class__.__name__),"parameters for calving"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("autodiff","[%s,%s]" % ("1x1",obj.autodiff.__class__.__name__),"automatic differentiation parameters"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("inversion","[%s,%s]" % ("1x1",obj.inversion.__class__.__name__),"parameters for inverse methods"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("qmu","[%s,%s]" % ("1x1",obj.qmu.__class__.__name__),"dakota properties"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("amr","[%s,%s]" % ("1x1",obj.amr.__class__.__name__),"adaptive mesh refinement properties"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("outputdefinition","[%s,%s]" % ("1x1",obj.outputdefinition.__class__.__name__),"output definition"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("results","[%s,%s]" % ("1x1",obj.results.__class__.__name__),"model results"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("radaroverlay","[%s,%s]" % ("1x1",obj.radaroverlay.__class__.__name__),"radar image for plot overlay"))
		string="%s\n%s" % (string,"%19s: %-22s -- %s" % ("miscellaneous","[%s,%s]" % ("1x1",obj.miscellaneous.__class__.__name__),"miscellaneous fields"))
		return string
	# }}}
	def checkmessage(self,string):    # {{{
		print "model not consistent: ", string
		self.private.isconsistent=False
		return self
	# }}}
	def extract(md,area):    # {{{
		"""
		extract - extract a model according to an Argus contour or flag list

		   This routine extracts a submodel from a bigger model with respect to a given contour
		   md must be followed by the corresponding exp file or flags list
		   It can either be a domain file (argus type, .exp extension), or an array of element flags. 
		   If user wants every element outside the domain to be 
		   extract2d, add '~' to the name of the domain file (ex: '~HO.exp')
		   an empty string '' will be considered as an empty domain
		   a string 'all' will be considered as the entire domain

		   Usage:
		      md2=extract(md,area)

		   Examples:
		      md2=extract(md,'Domain.exp')

		   See also: EXTRUDE, COLLAPSE
		"""

		#copy model
		md1=copy.deepcopy(md)

		#get elements that are inside area
		flag_elem=FlagElements(md1,area)
		if not np.any(flag_elem):
			raise RuntimeError("extracted model is empty")

		#kick out all elements with 3 dirichlets
		spc_elem=np.nonzero(np.logical_not(flag_elem))[0]
		spc_node=np.unique(md1.mesh.elements[spc_elem,:])-1
		flag=np.ones(md1.mesh.numberofvertices)
		flag[spc_node]=0
		pos=np.nonzero(np.logical_not(np.sum(flag[md1.mesh.elements-1],axis=1)))[0]
		flag_elem[pos]=0

		#extracted elements and nodes lists
		pos_elem=np.nonzero(flag_elem)[0]
		pos_node=np.unique(md1.mesh.elements[pos_elem,:])-1

		#keep track of some fields
		numberofvertices1=md1.mesh.numberofvertices
		numberofelements1=md1.mesh.numberofelements
		numberofvertices2=np.size(pos_node)
		numberofelements2=np.size(pos_elem)
		flag_node=np.zeros(numberofvertices1)
		flag_node[pos_node]=1

		#Create Pelem and Pnode (transform old nodes in new nodes and same thing for the elements)
		Pelem=np.zeros(numberofelements1,int)
		Pelem[pos_elem]=np.arange(1,numberofelements2+1)
		Pnode=np.zeros(numberofvertices1,int)
		Pnode[pos_node]=np.arange(1,numberofvertices2+1)

		#renumber the elements (some node won't exist anymore)
		elements_1=copy.deepcopy(md1.mesh.elements)
		elements_2=elements_1[pos_elem,:]
		elements_2[:,0]=Pnode[elements_2[:,0]-1]
		elements_2[:,1]=Pnode[elements_2[:,1]-1]
		elements_2[:,2]=Pnode[elements_2[:,2]-1]
		if md1.mesh.__class__.__name__=='mesh3dprisms':
			elements_2[:,3]=Pnode[elements_2[:,3]-1]
			elements_2[:,4]=Pnode[elements_2[:,4]-1]
			elements_2[:,5]=Pnode[elements_2[:,5]-1]

		#OK, now create the new model!

		#take every field from model
		md2=copy.deepcopy(md1)

		#automatically modify fields

		#loop over model fields
		model_fields=vars(md1)
		for fieldi in model_fields:
			#get field
			field=getattr(md1,fieldi)
			fieldsize=np.shape(field)
			if hasattr(field,'__dict__') and not m.ismember(fieldi,['results'])[0]:    #recursive call
				object_fields=vars(field)
				for fieldj in object_fields:
					#get field
					field=getattr(getattr(md1,fieldi),fieldj)
					fieldsize=np.shape(field)
					if len(fieldsize):
						#size = number of nodes * n
						if   fieldsize[0]==numberofvertices1:
							setattr(getattr(md2,fieldi),fieldj,field[pos_node])
						elif fieldsize[0]==numberofvertices1+1:
							setattr(getattr(md2,fieldi),fieldj,np.vstack((field[pos_node],field[-1,:])))
						#size = number of elements * n
						elif fieldsize[0]==numberofelements1:
							setattr(getattr(md2,fieldi),fieldj,field[pos_elem])
			else:
				if len(fieldsize):
					#size = number of nodes * n
					if   fieldsize[0]==numberofvertices1:
						setattr(md2,fieldi,field[pos_node])
					elif fieldsize[0]==numberofvertices1+1:
						setattr(md2,fieldi,np.hstack((field[pos_node],field[-1,:])))
					#size = number of elements * n
					elif fieldsize[0]==numberofelements1:
						setattr(md2,fieldi,field[pos_elem])

		#modify some specific fields

		#Mesh
		md2.mesh.numberofelements=numberofelements2
		md2.mesh.numberofvertices=numberofvertices2
		md2.mesh.elements=elements_2

		#mesh.uppervertex mesh.lowervertex
		if md1.mesh.__class__.__name__=='mesh3dprisms':
			md2.mesh.uppervertex=md1.mesh.uppervertex[pos_node]
			pos=np.where(~np.isnan(md2.mesh.uppervertex))[0]
			md2.mesh.uppervertex[pos]=Pnode[md2.mesh.uppervertex[pos].astype(int)-1]

			md2.mesh.lowervertex=md1.mesh.lowervertex[pos_node]
			pos=np.where(~np.isnan(md2.mesh.lowervertex))[0]
			md2.mesh.lowervertex[pos]=Pnode[md2.mesh.lowervertex[pos].astype(int)-1]

			md2.mesh.upperelements=md1.mesh.upperelements[pos_elem]
			pos=np.where(~np.isnan(md2.mesh.upperelements))[0]
			md2.mesh.upperelements[pos]=Pelem[md2.mesh.upperelements[pos].astype(int)-1]

			md2.mesh.lowerelements=md1.mesh.lowerelements[pos_elem]
			pos=np.where(~np.isnan(md2.mesh.lowerelements))[0]
			md2.mesh.lowerelements[pos]=Pelem[md2.mesh.lowerelements[pos].astype(int)-1]

		#Initial 2d mesh 
		if md1.mesh.__class__.__name__=='mesh3dprisms':
			flag_elem_2d=flag_elem[np.arange(0,md1.mesh.numberofelements2d)]
			pos_elem_2d=np.nonzero(flag_elem_2d)[0]
			flag_node_2d=flag_node[np.arange(0,md1.mesh.numberofvertices2d)]
			pos_node_2d=np.nonzero(flag_node_2d)[0]

			md2.mesh.numberofelements2d=np.size(pos_elem_2d)
			md2.mesh.numberofvertices2d=np.size(pos_node_2d)
			md2.mesh.elements2d=md1.mesh.elements2d[pos_elem_2d,:]
			md2.mesh.elements2d[:,0]=Pnode[md2.mesh.elements2d[:,0]-1]
			md2.mesh.elements2d[:,1]=Pnode[md2.mesh.elements2d[:,1]-1]
			md2.mesh.elements2d[:,2]=Pnode[md2.mesh.elements2d[:,2]-1]

			md2.mesh.x2d=md1.mesh.x[pos_node_2d]
			md2.mesh.y2d=md1.mesh.y[pos_node_2d]

		#Edges
		if m.strcmp(md.mesh.domaintype(),'2Dhorizontal'):
			if np.ndim(md2.mesh.edges)>1 and np.size(md2.mesh.edges,axis=1)>1:    #do not use ~isnan because there are some np.nans...
				#renumber first two columns
				pos=np.nonzero(md2.mesh.edges[:,3]!=-1)[0]
				md2.mesh.edges[:  ,0]=Pnode[md2.mesh.edges[:,0]-1]
				md2.mesh.edges[:  ,1]=Pnode[md2.mesh.edges[:,1]-1]
				md2.mesh.edges[:  ,2]=Pelem[md2.mesh.edges[:,2]-1]
				md2.mesh.edges[pos,3]=Pelem[md2.mesh.edges[pos,3]-1]
				#remove edges when the 2 vertices are not in the domain.
				md2.mesh.edges=md2.mesh.edges[np.nonzero(np.logical_and(md2.mesh.edges[:,0],md2.mesh.edges[:,1]))[0],:]
				#Replace all zeros by -1 in the last two columns
				pos=np.nonzero(md2.mesh.edges[:,2]==0)[0]
				md2.mesh.edges[pos,2]=-1
				pos=np.nonzero(md2.mesh.edges[:,3]==0)[0]
				md2.mesh.edges[pos,3]=-1
				#Invert -1 on the third column with last column (Also invert first two columns!!)
				pos=np.nonzero(md2.mesh.edges[:,2]==-1)[0]
				md2.mesh.edges[pos,2]=md2.mesh.edges[pos,3]
				md2.mesh.edges[pos,3]=-1
				values=md2.mesh.edges[pos,1]
				md2.mesh.edges[pos,1]=md2.mesh.edges[pos,0]
				md2.mesh.edges[pos,0]=values
				#Finally remove edges that do not belong to any element
				pos=np.nonzero(np.logical_and(md2.mesh.edges[:,1]==-1,md2.mesh.edges[:,2]==-1))[0]
				md2.mesh.edges=np.delete(md2.mesh.edges,pos,axis=0)

		#Penalties
		if np.any(np.logical_not(np.isnan(md2.stressbalance.vertex_pairing))):
			for i in xrange(np.size(md1.stressbalance.vertex_pairing,axis=0)):
				md2.stressbalance.vertex_pairing[i,:]=Pnode[md1.stressbalance.vertex_pairing[i,:]]
			md2.stressbalance.vertex_pairing=md2.stressbalance.vertex_pairing[np.nonzero(md2.stressbalance.vertex_pairing[:,0])[0],:]
		if np.any(np.logical_not(np.isnan(md2.masstransport.vertex_pairing))):
			for i in xrange(np.size(md1.masstransport.vertex_pairing,axis=0)):
				md2.masstransport.vertex_pairing[i,:]=Pnode[md1.masstransport.vertex_pairing[i,:]]
			md2.masstransport.vertex_pairing=md2.masstransport.vertex_pairing[np.nonzero(md2.masstransport.vertex_pairing[:,0])[0],:]

		#recreate segments
		if md1.mesh.__class__.__name__=='mesh2d':
			md2.mesh.vertexconnectivity=NodeConnectivity(md2.mesh.elements,md2.mesh.numberofvertices)[0]
			md2.mesh.elementconnectivity=ElementConnectivity(md2.mesh.elements,md2.mesh.vertexconnectivity)[0]
			md2.mesh.segments=contourenvelope(md2)
			md2.mesh.vertexonboundary=np.zeros(numberofvertices2,bool)
			md2.mesh.vertexonboundary[md2.mesh.segments[:,0:2]-1]=True
		else:
			#First do the connectivity for the contourenvelope in 2d
			md2.mesh.vertexconnectivity=NodeConnectivity(md2.mesh.elements2d,md2.mesh.numberofvertices2d)[0]
			md2.mesh.elementconnectivity=ElementConnectivity(md2.mesh.elements2d,md2.mesh.vertexconnectivity)[0]
			segments=contourenvelope(md2)
			md2.mesh.vertexonboundary=np.zeros(numberofvertices2/md2.mesh.numberoflayers,bool)
			md2.mesh.vertexonboundary[segments[:,0:2]-1]=True
			md2.mesh.vertexonboundary=np.tile(md2.mesh.vertexonboundary,md2.mesh.numberoflayers)
			#Then do it for 3d as usual
			md2.mesh.vertexconnectivity=NodeConnectivity(md2.mesh.elements,md2.mesh.numberofvertices)[0]
			md2.mesh.elementconnectivity=ElementConnectivity(md2.mesh.elements,md2.mesh.vertexconnectivity)[0]

		#Boundary conditions: Dirichlets on new boundary
		#Catch the elements that have not been extracted
		orphans_elem=np.nonzero(np.logical_not(flag_elem))[0]
		orphans_node=np.unique(md1.mesh.elements[orphans_elem,:])-1
		#Figure out which node are on the boundary between md2 and md1
		nodestoflag1=np.intersect1d(orphans_node,pos_node)
		nodestoflag2=Pnode[nodestoflag1].astype(int)-1
		if np.size(md1.stressbalance.spcvx)>1 and np.size(md1.stressbalance.spcvy)>2 and np.size(md1.stressbalance.spcvz)>2:
			if np.size(md1.inversion.vx_obs)>1 and np.size(md1.inversion.vy_obs)>1:
				md2.stressbalance.spcvx[nodestoflag2]=md2.inversion.vx_obs[nodestoflag2] 
				md2.stressbalance.spcvy[nodestoflag2]=md2.inversion.vy_obs[nodestoflag2]
			else:
				md2.stressbalance.spcvx[nodestoflag2]=np.nan
				md2.stressbalance.spcvy[nodestoflag2]=np.nan
				print "\n!! extract warning: spc values should be checked !!\n\n"
			#put 0 for vz
			md2.stressbalance.spcvz[nodestoflag2]=0
		if np.any(np.logical_not(np.isnan(md1.thermal.spctemperature))):
			md2.thermal.spctemperature[nodestoflag2]=1

		#Results fields
		if md1.results:
			md2.results=results()
			for solutionfield,field in md1.results.__dict__.iteritems():
				if   isinstance(field,list):
					setattr(md2.results,solutionfield,[])
					#get time step
					for i,fieldi in enumerate(field):
						if isinstance(fieldi,results) and fieldi:
							getattr(md2.results,solutionfield).append(results())
							fieldr=getattr(md2.results,solutionfield)[i]
							#get subfields
							for solutionsubfield,subfield in fieldi.__dict__.iteritems():
								if   np.size(subfield)==numberofvertices1:
									setattr(fieldr,solutionsubfield,subfield[pos_node])
								elif np.size(subfield)==numberofelements1:
									setattr(fieldr,solutionsubfield,subfield[pos_elem])
								else:
									setattr(fieldr,solutionsubfield,subfield)
						else:
							getattr(md2.results,solutionfield).append(None)
				elif isinstance(field,results):
					setattr(md2.results,solutionfield,results())
					if isinstance(field,results) and field:
						fieldr=getattr(md2.results,solutionfield)
						#get subfields
						for solutionsubfield,subfield in field.__dict__.iteritems():
							if   np.size(subfield)==numberofvertices1:
								setattr(fieldr,solutionsubfield,subfield[pos_node])
							elif np.size(subfield)==numberofelements1:
								setattr(fieldr,solutionsubfield,subfield[pos_elem])
							else:
								setattr(fieldr,solutionsubfield,subfield)

		#Keep track of pos_node and pos_elem
		md2.mesh.extractedvertices=pos_node+1
		md2.mesh.extractedelements=pos_elem+1

		return md2
	# }}}
	def extrude(md,*args):    # {{{
		"""
		EXTRUDE - vertically extrude a 2d mesh

		   vertically extrude a 2d mesh and create corresponding 3d mesh.
		   The vertical distribution can:
		    - follow a polynomial law
		    - follow two polynomial laws, one for the lower part and one for the upper part of the mesh
		    - be discribed by a list of coefficients (between 0 and 1)
 

		   Usage:
		      md=extrude(md,numlayers,extrusionexponent)
		      md=extrude(md,numlayers,lowerexponent,upperexponent)
		      md=extrude(md,listofcoefficients)

		   Example:
				md=extrude(md,15,1.3);
				md=extrude(md,15,1.3,1.2);
				md=extrude(md,[0 0.2 0.5 0.7 0.9 0.95 1])

		   See also: MODELEXTRACT, COLLAPSE
		"""

		#some checks on list of arguments
		if len(args)>3 or len(args)<1:
			raise RuntimeError("extrude error message")

		#Extrude the mesh
		if   len(args)==1:    #list of coefficients
			clist=args[0]
			if any(clist<0) or any(clist>1):
				raise TypeError("extrusioncoefficients must be between 0 and 1")
			clist.extend([0.,1.])
			clist.sort()
			extrusionlist=list(set(clist))
			numlayers=len(extrusionlist)

		elif len(args)==2:    #one polynomial law
			if args[1]<=0:
				raise TypeError("extrusionexponent must be >=0")
			numlayers=args[0]
			extrusionlist=(np.arange(0.,float(numlayers-1)+1.,1.)/float(numlayers-1))**args[1]

		elif len(args)==3:    #two polynomial laws
			numlayers=args[0]
			lowerexp=args[1]
			upperexp=args[2]

			if args[1]<=0 or args[2]<=0:
				raise TypeError("lower and upper extrusionexponents must be >=0")

			lowerextrusionlist=(np.arange(0.,1.+2./float(numlayers-1),2./float(numlayers-1)))**lowerexp/2.
			upperextrusionlist=(np.arange(0.,1.+2./float(numlayers-1),2./float(numlayers-1)))**upperexp/2.
			extrusionlist=np.unique(np.concatenate((lowerextrusionlist,1.-upperextrusionlist)))

		if numlayers<2:
			raise TypeError("number of layers should be at least 2")
		if md.mesh.__class__.__name__=='mesh3dprisms':
			raise TypeError("Cannot extrude a 3d mesh (extrude cannot be called more than once)")

		#Initialize with the 2d mesh
		mesh2d = md.mesh
		md.mesh=mesh3dprisms()
		md.mesh.x                           = mesh2d.x
		md.mesh.y                           = mesh2d.y
		md.mesh.elements                    = mesh2d.elements
		md.mesh.numberofelements            = mesh2d.numberofelements
		md.mesh.numberofvertices            = mesh2d.numberofvertices

		md.mesh.lat                         = mesh2d.lat
		md.mesh.long                        = mesh2d.long
		md.mesh.epsg                        = mesh2d.epsg

		md.mesh.vertexonboundary            = mesh2d.vertexonboundary
		md.mesh.vertexconnectivity          = mesh2d.vertexconnectivity
		md.mesh.elementconnectivity         = mesh2d.elementconnectivity
		md.mesh.average_vertex_connectivity = mesh2d.average_vertex_connectivity

		md.mesh.extractedvertices           = mesh2d.extractedvertices
		md.mesh.extractedelements           = mesh2d.extractedelements

		x3d=np.empty((0))
		y3d=np.empty((0))
		z3d=np.empty((0))    #the lower node is on the bed
		thickness3d=md.geometry.thickness    #thickness and bed for these nodes
		bed3d=md.geometry.base

		#Create the new layers
		for i in xrange(numlayers):
			x3d=np.concatenate((x3d,md.mesh.x))
			y3d=np.concatenate((y3d,md.mesh.y))
			#nodes are distributed between bed and surface accordingly to the given exponent
			z3d=np.concatenate((z3d,(bed3d+thickness3d*extrusionlist[i]).reshape(-1)))
		number_nodes3d=np.size(x3d)    #number of 3d nodes for the non extruded part of the mesh

		#Extrude elements 
		elements3d=np.empty((0,6),int)
		for i in xrange(numlayers-1):
			elements3d=np.vstack((elements3d,np.hstack((md.mesh.elements+i*md.mesh.numberofvertices,md.mesh.elements+(i+1)*md.mesh.numberofvertices))))    #Create the elements of the 3d mesh for the non extruded part
		number_el3d=np.size(elements3d,axis=0)    #number of 3d nodes for the non extruded part of the mesh

		#Keep a trace of lower and upper nodes
		lowervertex=np.nan*np.ones(number_nodes3d,int)
		uppervertex=np.nan*np.ones(number_nodes3d,int)
		lowervertex[md.mesh.numberofvertices:]=np.arange(1,(numlayers-1)*md.mesh.numberofvertices+1)
		uppervertex[:(numlayers-1)*md.mesh.numberofvertices]=np.arange(md.mesh.numberofvertices+1,number_nodes3d+1)
		md.mesh.lowervertex=lowervertex
		md.mesh.uppervertex=uppervertex

		#same for lower and upper elements
		lowerelements=np.nan*np.ones(number_el3d,int)
		upperelements=np.nan*np.ones(number_el3d,int)
		lowerelements[md.mesh.numberofelements:]=np.arange(1,(numlayers-2)*md.mesh.numberofelements+1)
		upperelements[:(numlayers-2)*md.mesh.numberofelements]=np.arange(md.mesh.numberofelements+1,(numlayers-1)*md.mesh.numberofelements+1)
		md.mesh.lowerelements=lowerelements
		md.mesh.upperelements=upperelements

		#Save old mesh 
		md.mesh.x2d=md.mesh.x
		md.mesh.y2d=md.mesh.y
		md.mesh.elements2d=md.mesh.elements
		md.mesh.numberofelements2d=md.mesh.numberofelements
		md.mesh.numberofvertices2d=md.mesh.numberofvertices

		#Build global 3d mesh 
		md.mesh.elements=elements3d
		md.mesh.x=x3d
		md.mesh.y=y3d
		md.mesh.z=z3d
		md.mesh.numberofelements=number_el3d
		md.mesh.numberofvertices=number_nodes3d
		md.mesh.numberoflayers=numlayers

		#Ok, now deal with the other fields from the 2d mesh:

		#bedinfo and surface info
		md.mesh.vertexonbase=project3d(md,'vector',np.ones(md.mesh.numberofvertices2d,bool),'type','node','layer',1)
		md.mesh.vertexonsurface=project3d(md,'vector',np.ones(md.mesh.numberofvertices2d,bool),'type','node','layer',md.mesh.numberoflayers)
		md.mesh.vertexonboundary=project3d(md,'vector',md.mesh.vertexonboundary,'type','node')

		#lat long
		md.mesh.lat=project3d(md,'vector',md.mesh.lat,'type','node')
		md.mesh.long=project3d(md,'vector',md.mesh.long,'type','node')

		md.geometry.extrude(md)
		md.friction.extrude(md)
		md.inversion.extrude(md)
		md.smb.extrude(md)
		md.initialization.extrude(md)
		md.flowequation.extrude(md)

		md.stressbalance.extrude(md)
		md.thermal.extrude(md)
		md.masstransport.extrude(md)

		# Calving variables
		md.hydrology.extrude(md)
		md.levelset.extrude(md)
		md.calving.extrude(md)

		#connectivity
		md.mesh.elementconnectivity=np.tile(md.mesh.elementconnectivity,(numlayers-1,1))
		md.mesh.elementconnectivity[np.nonzero(md.mesh.elementconnectivity==0)]=-sys.maxint-1
		if not np.isnan(md.mesh.elementconnectivity).all():
			for i in xrange(1,numlayers-1):
				md.mesh.elementconnectivity[i*md.mesh.numberofelements2d:(i+1)*md.mesh.numberofelements2d,:] \
						=md.mesh.elementconnectivity[i*md.mesh.numberofelements2d:(i+1)*md.mesh.numberofelements2d,:]+md.mesh.numberofelements2d
				md.mesh.elementconnectivity[np.nonzero(md.mesh.elementconnectivity<0)]=0

		md.materials.extrude(md)
		md.damage.extrude(md)
		md.gia.extrude(md)
		md.mask.extrude(md)
		md.qmu.extrude(md)
		md.basalforcings.extrude(md)

		#increase connectivity if less than 25:
		if md.mesh.average_vertex_connectivity<=25:
			md.mesh.average_vertex_connectivity=100

		return md
		# }}}
	def collapse(md): #{{{
		'''
		collapses a 3d mesh into a 2d mesh
			
		This routine collapses a 3d model into a 2d model and collapses all
		the fileds of the 3d model by taking their depth-averaged values
			
		Usage:
			md=collapse(md)
		'''	

		#Check that the model is really a 3d model
		if md.mesh.domaintype().lower() != '3d':
			raise StandardError("only a 3D model can be collapsed")
		
		#drag is limited to nodes that are on the bedrock.
		md.friction.coefficient=project2d(md,md.friction.coefficient,1)

		#p and q (same deal, except for element that are on the bedrock: )
		md.friction.p=project2d(md,md.friction.p,1)
		md.friction.q=project2d(md,md.friction.q,1)

		#observations
		if not np.isnan(md.inversion.vx_obs).all(): md.inversion.vx_obs=project2d(md,md.inversion.vx_obs,md.mesh.numberoflayers) 
		if not np.isnan(md.inversion.vy_obs).all(): md.inversion.vy_obs=project2d(md,md.inversion.vy_obs,md.mesh.numberoflayers) 
		if not np.isnan(md.inversion.vel_obs).all(): md.inversion.vel_obs=project2d(md,md.inversion.vel_obs,md.mesh.numberoflayers) 
		if not np.isnan(md.inversion.cost_functions_coefficients).all(): md.inversion.cost_functions_coefficients=project2d(md,md.inversion.cost_functions_coefficients,md.mesh.numberoflayers) 
                if isinstance(md.inversion.min_parameters,np.ndarray):
                    if md.inversion.min_parameters.size>1: md.inversion.min_parameters=project2d(md,md.inversion.min_parameters,md.mesh.numberoflayers) 
                if isinstance(md.inversion.max_parameters,np.ndarray):
		    if md.inversion.max_parameters.size>1: md.inversion.max_parameters=project2d(md,md.inversion.max_parameters,md.mesh.numberoflayers) 
		if not np.isnan(md.smb.mass_balance).all():
			md.smb.mass_balance=project2d(md,md.smb.mass_balance,md.mesh.numberoflayers) 
		
		#results
		if not np.isnan(md.initialization.vx).all(): md.initialization.vx=DepthAverage(md,md.initialization.vx)
		if not np.isnan(md.initialization.vy).all(): md.initialization.vy=DepthAverage(md,md.initialization.vy)
		if not np.isnan(md.initialization.vz).all(): md.initialization.vz=DepthAverage(md,md.initialization.vz)
		if not np.isnan(md.initialization.vel).all(): md.initialization.vel=DepthAverage(md,md.initialization.vel)
		if not np.isnan(md.initialization.temperature).all(): md.initialization.temperature=DepthAverage(md,md.initialization.temperature)
                if not np.isnan(md.initialization.pressure).all(): md.initialization.pressure=project2d(md,md.initialization.pressure,1)
                if not np.isnan(md.initialization.sediment_head).all(): md.initialization.sediment_head=project2d(md,md.initialization.sediment_head,1)
                if not np.isnan(md.initialization.epl_head).all(): md.initialization.epl_head=project2d(md,md.initialization.epl_head,1)
                if not np.isnan(md.initialization.epl_thickness).all(): md.initialization.epl_thickness=project2d(md,md.initialization.epl_thickness,1)

		#giaivins
		if not np.isnan(md.gia.mantle_viscosity).all(): md.gia.mantle_viscosity=project2d(md,md.gia.mantle_viscosity,1) 
		if not np.isnan(md.gia.lithosphere_thickness).all(): md.gia.lithosphere_thickness=project2d(md,md.gia.lithosphere_thickness,1) 

		#elementstype
		if not np.isnan(md.flowequation.element_equation).all():
			md.flowequation.element_equation=project2d(md,md.flowequation.element_equation,1)
			md.flowequation.vertex_equation=project2d(md,md.flowequation.vertex_equation,1)
			md.flowequation.borderSSA=project2d(md,md.flowequation.borderSSA,1)
			md.flowequation.borderHO=project2d(md,md.flowequation.borderHO,1)
			md.flowequation.borderFS=project2d(md,md.flowequation.borderFS,1)


                # Hydrologydc variables
                if hasattr(md.hydrology,'hydrologydc'):
                    md.hydrology.spcsediment_head=project2d(md,md.hydrology.spcsediment_head,1)
                    md.hydrology.mask_eplactive_node=project2d(md,md.hydrology.mask_eplactive_node,1)
                    md.hydrology.sediment_transmitivity=project2d(md,md.hydrology.sediment_transmitivity,1)
                    md.hydrology.basal_moulin_input=project2d(md,md.hydrology.basal_moulin_input,1)
                    if md.hydrology.isefficientlayer == 1:
                        md.hydrology.spcepl_head=project2d(md,md.hydrology.spcepl_head,1)

		#boundary conditions
		md.stressbalance.spcvx=project2d(md,md.stressbalance.spcvx,md.mesh.numberoflayers)
		md.stressbalance.spcvy=project2d(md,md.stressbalance.spcvy,md.mesh.numberoflayers)
		md.stressbalance.spcvz=project2d(md,md.stressbalance.spcvz,md.mesh.numberoflayers)
		md.stressbalance.referential=project2d(md,md.stressbalance.referential,md.mesh.numberoflayers)
		md.stressbalance.loadingforce=project2d(md,md.stressbalance.loadingforce,md.mesh.numberoflayers)
		md.masstransport.spcthickness=project2d(md,md.masstransport.spcthickness,md.mesh.numberoflayers)
		if not np.isnan(md.damage.spcdamage).all(): md.damage.spcdamage=project2d(md,md.damage.spcdamage,md.mesh.numberoflayers-1)
		md.thermal.spctemperature=project2d(md,md.thermal.spctemperature,md.mesh.numberoflayers-1)

		#materials
		md.materials.rheology_B=DepthAverage(md,md.materials.rheology_B)
		md.materials.rheology_n=project2d(md,md.materials.rheology_n,1)
		
		#damage: 
		if md.damage.isdamage:
			md.damage.D=DepthAverage(md,md.damage.D)

		#special for thermal modeling:
		md.basalforcings.groundedice_melting_rate=project2d(md,md.basalforcings.groundedice_melting_rate,1) 
		md.basalforcings.floatingice_melting_rate=project2d(md,md.basalforcings.floatingice_melting_rate,1) 
		md.basalforcings.geothermalflux=project2d(md,md.basalforcings.geothermalflux,1) #bedrock only gets geothermal flux

		#update of connectivity matrix
		md.mesh.average_vertex_connectivity=25

		#Collapse the mesh
		nodes2d=md.mesh.numberofvertices2d
		elements2d=md.mesh.numberofelements2d

		#parameters
		md.geometry.surface=project2d(md,md.geometry.surface,1)
		md.geometry.thickness=project2d(md,md.geometry.thickness,1)
		md.geometry.base=project2d(md,md.geometry.base,1)
                if isinstance(md.geometry.bed,np.ndarray):
                    md.geometry.bed=project2d(md,md.geometry.bed,1)
		md.mask.groundedice_levelset=project2d(md,md.mask.groundedice_levelset,1)
		md.mask.ice_levelset=project2d(md,md.mask.ice_levelset,1)

		#Initialize with the 2d mesh
		mesh=mesh2d()
		mesh.x=md.mesh.x2d
		mesh.y=md.mesh.y2d
		mesh.numberofvertices=md.mesh.numberofvertices2d
		mesh.numberofelements=md.mesh.numberofelements2d
		mesh.elements=md.mesh.elements2d
		if not np.isnan(md.mesh.vertexonboundary).all(): mesh.vertexonboundary=project2d(md,md.mesh.vertexonboundary,1)
		if not np.isnan(md.mesh.elementconnectivity).all(): mesh.elementconnectivity=project2d(md,md.mesh.elementconnectivity,1)
		if isinstance(md.mesh.lat,np.ndarray):
			if md.mesh.lat.size==md.mesh.numberofvertices:  mesh.lat=project2d(md,md.mesh.lat,1) 
		if isinstance(md.mesh.long,np.ndarray):
			if md.mesh.long.size==md.mesh.numberofvertices: mesh.long=project2d(md,md.mesh.long,1) 
		mesh.epsg=md.mesh.epsg
		md.mesh=mesh

		return md

#}}}
