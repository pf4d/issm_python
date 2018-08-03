import shelve
import os.path
import numpy as  np
from netCDF4 import Dataset
from netCDF4 import chartostring
from re import findall
from os import path
from collections import OrderedDict
from whichdb import whichdb
from issm.model import *

def loadvars(*args):
	"""
	LOADVARS - function to load variables to a file.

	This function loads one or more variables from a file.  The names of the variables
	must be supplied.  If more than one variable is specified, it may be done with
	a list of names or a dictionary of name as keys.  The output type will correspond
	to the input type.  All the variables in the file may be loaded by specifying only
	the file name.

	Usage:
	   a=loadvars('shelve.dat','a')
	   [a,b]=loadvars('shelve.dat',['a','b'])
	   nvdict=loadvars('shelve.dat',{'a':None,'b':None})
	   nvdict=loadvars('shelve.dat')

	"""

	filename=''
	nvdict={}

	if len(args) >= 1 and isinstance(args[0],(str,unicode)):
		filename=args[0]
		if not filename:
			filename='/tmp/shelve.dat'

	else:
		raise TypeError("Missing file name.")

	if   len(args) >= 2 and isinstance(args[1],(str,unicode)):    # (filename,name)
		for name in args[1:]:
			nvdict[name]=None

	elif len(args) == 2 and isinstance(args[1],list):    # (filename,[names])
		for name in args[1]:
			nvdict[name]=None

	elif len(args) == 2 and isinstance(args[1],dict):    # (filename,{names:values})
		nvdict=args[1]

	elif len(args) == 1:    #  (filename)
		pass

	else:
		raise TypeError("Unrecognized input arguments.")

	if whichdb(filename):
		print "Loading variables from file '%s'." % filename
		
		my_shelf = shelve.open(filename,'r') # 'r' for read-only
		if nvdict:
			for name in nvdict.iterkeys():
				try:
					nvdict[name] = my_shelf[name]
					print "Variable '%s' loaded." % name
				except KeyError:
					value = None
					print "Variable '%s' not found." % name

		else:
			for name in my_shelf.iterkeys():
				nvdict[name] = my_shelf[name]
				print "Variable '%s' loaded." % name

		my_shelf.close()

	else:
		try:
			NCFile=Dataset(filename,mode='r')
			NCFile.close()
		except RuntimeError:
			raise IOError("File '%s' not found." % filename)

		classtype,classtree=netCDFread(filename)
		nvdict['md']=model()
		NCFile=Dataset(filename,mode='r')
		for mod in dict.keys(classtype):
			if np.size(classtree[mod])>1:
				curclass=NCFile.groups[classtree[mod][0]].groups[classtree[mod][1]]
				if classtype[mod][0]=='list':
					keylist=[key for key in curclass.groups]
					try:
						steplist=[int(key) for key in curclass.groups]
					except ValueError:
						steplist=[int(findall(r'\d+',key)[0]) for key in keylist]
					indexlist=[index*(len(curclass.groups)-1)/max(1,max(steplist)) for index in steplist]
					listtype=curclass.groups[keylist[0]].classtype
					if listtype=='dict':
						nvdict['md'].__dict__[classtree[mod][0]].__dict__[classtree[mod][1]] = [OrderedDict() for i in range(max(1,len(curclass.groups)))]
					else:
						nvdict['md'].__dict__[classtree[mod][0]].__dict__[classtree[mod][1]] = [getattr(__import__(listtype),listtype)() for i in range(max(1,len(curclass.groups)))]
					Tree=nvdict['md'].__dict__[classtree[mod][0]].__dict__[classtree[mod][1]][:]
				else:
					nvdict['md'].__dict__[classtree[mod][0]].__dict__[classtree[mod][1]] = getattr(classtype[mod][1],classtype[mod][0])()
					Tree=nvdict['md'].__dict__[classtree[mod][0]].__dict__[classtree[mod][1]]
			else:
				curclass=NCFile.groups[classtree[mod][0]]
				nvdict['md'].__dict__[mod] = getattr(classtype[mod][1],classtype[mod][0])()
				Tree=nvdict['md'].__dict__[classtree[mod][0]]
			#treating groups that are lists
			for i in range(0,max(1,len(curclass.groups))):
				if len(curclass.groups)>0:
					listclass=curclass.groups[keylist[i]]
				else:
					listclass=curclass
				for var in listclass.variables:
					if var not in ['errlog','outlog']:
						varval=listclass.variables[str(var)]
						vardim=varval.ndim
						try:
							val_type=str(varval.dtype)
						except AttributeError:
							val_type=type(varval)
						if vardim==0:
							if type(Tree)==list:
								t=indexlist[i]
								if listtype=='dict':
									Tree[t][str(var)]=varval[0]
								else:
									Tree[t].__dict__[str(var)]=varval[0]
							else:
								if str(varval[0])=='':
									Tree.__dict__[str(var)]=[]
								elif varval[0]=='True':
									Tree.__dict__[str(var)]=True
								elif varval[0]=='False':
									Tree.__dict__[str(var)]=False
								else:
									Tree.__dict__[str(var)]=varval[0]

						elif vardim==1:
							if varval.dtype==str:
								if varval.shape[0]==1:
									Tree.__dict__[str(var)]=[str(varval[0]),]
								elif 'True' in varval[:] or 'False' in varval[:]:
									Tree.__dict__[str(var)]=np.asarray([V=='True' for V in varval[:]],dtype=bool)
								else:
									Tree.__dict__[str(var)]=[str(vallue) for vallue in varval[:]]
							else:
								if type(Tree)==list:
									t=indexlist[i]
									if listtype=='dict':
										Tree[t][str(var)]=varval[:]
									else:
										Tree[t].__dict__[str(var)]=varval[:]
								else:
									try:
										#some thing specifically require a list
										mdtype=type(Tree.__dict__[str(var)])
									except KeyError:
										mdtype=float
									if mdtype==list:
										Tree.__dict__[str(var)]=[mdval for mdval in varval[:]]
									else:
										Tree.__dict__[str(var)]=varval[:]
						elif vardim==2:
							#dealling with dict
							if varval.dtype==str:
								Tree.__dict__[str(var)]=OrderedDict(zip(varval[:,0], varval[:,1]))
							else:
								if type(Tree)==list:
									#t=int(keylist[i][-1])-1
									t=indexlist[i]
									if listtype=='dict':
										Tree[t][str(var)]=varval[:,:]
									else:
										Tree[t].__dict__[str(var)]=varval[:,:]
								else:
									Tree.__dict__[str(var)]=varval[:,:]
						elif vardim==3:
							if type(Tree)==list:
								t=indexlist[i]
								if listtype=='dict':
									Tree[t][str(var)]=varval[:,:,:]
								else:
									Tree[t].__dict__[str(var)]=varval[:,:,:]
							else:
								Tree.__dict__[str(var)]=varval[:,:,:]
						else:
							print 'table dimension greater than 3 not implemented yet'
				for attr in listclass.ncattrs():
					if  attr!='classtype': #classtype is for treatment, don't get it back
						if type(Tree)==list:
							t=indexlist[i]
							if listtype=='dict':
								Tree[t][str(attr).swapcase()]=str(listclass.getncattr(attr))
							else:
								Tree[t].__dict__[str(attr).swapcase()]=str(listclass.getncattr(attr))
						else:
							Tree.__dict__[str(attr).swapcase()]=str(listclass.getncattr(attr))
							if listclass.getncattr(attr)=='True':
								Tree.__dict__[str(attr).swapcase()]=True
							elif listclass.getncattr(attr)=='False':
								Tree.__dict__[str(attr).swapcase()]=False
		NCFile.close()
	if   len(args) >= 2 and isinstance(args[1],(str,unicode)):    # (value)
		value=[nvdict[name] for name in args[1:]]
		return value

	elif len(args) == 2 and isinstance(args[1],list):    # ([values])
		value=[nvdict[name] for name in args[1]]
		return value

	elif (len(args) == 2 and isinstance(args[1],dict)) or (len(args) == 1):    # ({names:values})
		return nvdict


def netCDFread(filename):
	print ('Opening {} for reading '.format(filename))
	NCData=Dataset(filename, 'r')
	class_dict={}
	class_tree={}

	for group in NCData.groups:
		if len(NCData.groups[group].groups)>0:
			for subgroup in NCData.groups[group].groups:
				classe=str(group)+'.'+str(subgroup)
				class_dict[classe]=[str(getattr(NCData.groups[group].groups[subgroup],'classtype')),]
				if class_dict[classe][0] not in ['dict','list','cell']:
					class_dict[classe].append(__import__(class_dict[classe][0]))
				class_tree[classe]=[group,subgroup]
		else:
			classe=str(group)
			try:
				class_dict[classe]=[str(getattr(NCData.groups[group],'classtype')),]
				if class_dict[classe][0] not in ['dict','list','cell']:
					class_dict[classe].append(__import__(class_dict[classe][0]))
					class_tree[classe]=[group,]
			except AttributeError:
				print('group {} is empty'.format(group))
	NCData.close()
	return class_dict,class_tree
