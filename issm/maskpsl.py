import numpy as np
import issm.MatlabFuncs as m
from issm.model import *
from issm.fielddisplay import fielddisplay
from issm.checkfield import checkfield
from issm.WriteData import WriteData

class maskpsl(object):
#MASKPSL class definition
#
#   Usage:
#      maskpsl=maskpsl();

	def __init__(self,*args): # {{{
		self.groundedice_levelset = float('NaN')
		self.ice_levelset         = float('NaN')
		self.ocean_levelset = float('NaN')
		self.land_levelset = float('NaN')

		if not len(args):
			self.setdefaultparameters()
		else:
			raise RuntimeError('constructor not supported')
	# }}}
	def __repr__(self): # {{{
		string='   masks:'
		string="%s\n%s"%(string,fielddisplay(self,'groundedice_levelset','is ice grounded ? grounded ice if > 0, grounding line position if = 0, floating ice if < 0'))
		string="%s\n%s"%(string,fielddisplay(self,'ice_levelset','presence of ice if < 0, icefront position if = 0, no ice if > 0'))
		string="%s\n%s"%(string,fielddisplay(self,'ocean_levelset','is the vertex on the ocean ? yes if = 1, no if = 0'))
		string="%s\n%s"%(string,fielddisplay(self,'land_levelset','is the vertex on the land ? yes if = 1, no if = 0'))
		return string

	# }}}	
	def loadobj(self): # {{{
		# This def is directly called by matlab when a model object is
		# loaded. Update old properties here
		#2014 February 5th
		if numel(self.ice_levelset)>1 and all(self.ice_levelset>=0):
			print('WARNING: md.mask.ice_levelset>=0, you probably need to change the sign of this levelset')
		return self
	# }}}

	def setdefaultparameters(self): # {{{
		return self

	# }}}

	def checkconsistency(self,md,solution,analyses): # {{{
		md = checkfield(md,'fieldname','mask.groundedice_levelset','size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mask.ice_levelset'        ,'size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mask.ocean_levelset','size',[md.mesh.numberofvertices])
		md = checkfield(md,'fieldname','mask.land_levelset','size',[md.mesh.numberofvertices])
		isice=(md.mask.ice_levelset<=0)
		if sum(isice)==0:
			print('no ice present in the domain')

		if max(md.mask.ice_levelset)<0:
			print('no ice front provided')

		elements=md.mesh.elements-1; elements=elements.astype(np.int32, copy=False);
		icefront=np.sum(md.mask.ice_levelset[elements]==0,axis=1)
		if (max(icefront)==3 & m.strcmp(md.mesh.elementtype(),'Tria')) or (max(icefront==6) & m.strcmp(md.mesh.elementtype(),'Penta')):
			raise RuntimeError('At least one element has all nodes on ice front, change md.mask.ice_levelset to fix it')

		return md

	# }}}

	def extrude(self,md): # {{{
		self.groundedice_levelset=project3d(md,'vector',self.groundedice_levelset,'type','node')
		self.ice_levelset=project3d(md,'vector',self.ice_levelset,'type','node')
		self.ocean_levelset=project3d(md,'vector',self.ocean_levelset,'type','node')
		self.land_levelset=project3d(md,'vector',self.land_levelset,'type','node')
		return self
	# }}}

	def mask(*args): # {{{
		if not len(args):
			self.setdefaultparameters()
		else:
			raise RuntimeError('constructor not supported')
		return self

	# }}}

	def marshall(self,prefix,md,fid): # {{{
		WriteData(fid,prefix,'object',self,'class','mask','fieldname','groundedice_levelset','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'class','mask','fieldname','ice_levelset','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'class','mask','fieldname','ocean_levelset','format','DoubleMat','mattype',1)
		WriteData(fid,prefix,'object',self,'class','mask','fieldname','land_levelset','format','DoubleMat','mattype',1)
	# }}}
	def savemodeljs(self,fid,modelname): # {{{
		writejs1Darray(fid,[modelname, '.mask.groundedice_levelset'],self.groundedice_levelset)
		writejs1Darray(fid,[modelname, '.mask.ice_levelset'],self.ice_levelset)
		writejs1Darray(fid,[modelname, '.mask.ocean_levelset'],self.ocean_levelset)
		writejs1Darray(fid,[modelname, '.mask.land_levelset'],self.land_levelset)
	# }}}

