from issm.fielddisplay import fielddisplay
from issm.pairoptions import pairoptions
from issm.checkfield import checkfield
from issm.WriteData import WriteData
from issm.MeshProfileIntersection import MeshProfileIntersection
import os

class massfluxatgate(object):
	"""
	MASSFLUXATEGATE class definition

	   Usage:
		  massfluxatgate=massfluxatgate('GateName','PathToExpFile')
	"""

	def __init__(self,*args): # {{{

		self.name            = ''
		self.definitionstring  = ''
		self.profilename     = ''
		self.segments        = float('NaN')

		#set defaults
		self.setdefaultparameters()

		#use provided options to change fields
		options=pairoptions(*args)

		#OK get other fields
		self=options.AssignObjectFields(self)

		#}}}
	def __repr__(self): # {{{

		string="   Massfluxatgate:"
		string="%s\n%s"%(string,fielddisplay(self,'name','identifier for this massfluxatgate response'))
		string="%s\n%s"%(string,fielddisplay(self,'definitionstring','string that identifies this output definition uniquely, from Outputdefinition[1-10]'))
		string="%s\n%s"%(string,fielddisplay(self,'profilename','name of file (shapefile or argus file) defining a profile (or gate)'))
		return string
		#}}}
	def setdefaultparameters(self): # {{{
		return self
	#}}}
	def checkconsistency(self,md,solution,analyses):    # {{{
		
		if  not isinstance(self.name, basestring):
			raise RuntimeError("massfluxatgate error message: 'name' field should be a string!")
			
		if  not isinstance(self.profilename, basestring):
			raise RuntimeError("massfluxatgate error message: 'profilename' field should be a string!") 

			md = checkfield(md,'field',self.definitionstring,'values',['Outputdefinition1','Outputdefinition2','Outputdefinition3','Outputdefinition4','Outputdefinition5','Outputdefinition6','Outputdefinition7','Outputdefinition8','Outputdefinition9','Outputdefinition10'])
		
		#check the profilename points to a file!: 
		if not os.path.isfile(self.profilename):
			raise RuntimeError("massfluxatgate error message: file name for profile corresponding to gate does not point to a legitimate file on disk!")

		return md
	# }}}
	def marshall(self,prefix,md,fid):    # {{{
		
		#before marshalling, we need to create the segments out of the profilename: 
		self.segments=MeshProfileIntersection(md.mesh.elements,md.mesh.x,md.mesh.y,self.profilename)[0]

		#ok, marshall name and segments: 
		WriteData(fid,prefix,'data',self.name,'name','md.massfluxatgate.name','format','String');
		WriteData(fid,prefix,'data',self.definitionstring,'name','md.massfluxatgate.definitionstring','format','String');
		WriteData(fid,prefix,'data',self.segments,'name','md.massfluxatgate.segments','format','DoubleMat','mattype',1);

	# }}}
