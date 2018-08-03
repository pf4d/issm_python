from collections import OrderedDict
from issm.pairoptions import pairoptions
from issm.IssmConfig import IssmConfig

def mumpsoptions(*args):
	"""
	MUMPSOPTIONS - return MUMPS direct solver  petsc options

	   Usage:
	      options=mumpsoptions;
	"""

	#retrieve options provided in varargin
	options=pairoptions(*args)
	mumps=OrderedDict()

	#default mumps options
	PETSC_VERSION=IssmConfig('_PETSC_MAJOR_')[0]
	if PETSC_VERSION==2.:
		mumps['toolkit']='petsc'
		mumps['mat_type']=options.getfieldvalue('mat_type','aijmumps')
		mumps['ksp_type']=options.getfieldvalue('ksp_type','preonly')
		mumps['pc_type']=options.getfieldvalue('pc_type','lu')
		mumps['mat_mumps_icntl_14']=options.getfieldvalue('mat_mumps_icntl_14',120)
		mumps['pc_factor_shift_positive_definite']=options.getfieldvalue('pc_factor_shift_positive_definite','true')
	if PETSC_VERSION==3.:
		mumps['toolkit']='petsc'
		mumps['mat_type']=options.getfieldvalue('mat_type','mpiaij')
		mumps['ksp_type']=options.getfieldvalue('ksp_type','preonly')
		mumps['pc_type']=options.getfieldvalue('pc_type','lu')
		mumps['pc_factor_mat_solver_package']=options.getfieldvalue('pc_factor_mat_solver_package','mumps')
		mumps['mat_mumps_icntl_14']=options.getfieldvalue('mat_mumps_icntl_14',120)
		mumps['pc_factor_shift_positive_definite']=options.getfieldvalue('pc_factor_shift_positive_definite','true')

	return mumps

