import pairoptions
from IssmConfig import IssmConfig

def stokesoptions(*args):
	#STOKESOPTIONS - return STOKES multi-physics solver petsc options
	#
	#   Usage:
	#      options=stokesoptions;
	
	#retrieve options provided in varargin
	arguments=pairoptions.pairoptions(*args) 


	#default stokes options
	PETSC_VERSION=IssmConfig('_PETSC_MAJOR_')[0]

	if PETSC_VERSION==2.:
		raise RuntimeError('stokesoptions error message: multi-physics options not supported in Petsc 2')
	if PETSC_VERSION==3.:
		options=[['toolkit','petsc'],['mat_type','mpiaij'],['ksp_max_it',1000],['ksp_type','gmres'],['pc_type','fieldsplit'],['pc_field_split_type','schur'],\
	['fieldsplit_0_pc_type','hypre'],['fieldsplit_0_ksp_type','gmres'],['fieldsplit_0_pc_hypre_type','boomerang'],\
	['fieldsplit_1_pc_type','jacobi'],['fieldsplit_1_ksp_type','preonly'],['issm_option_solver','stokes']]

	#now, go through our arguments, and write over default options.
	for i in range(len(arguments.list)):
		arg1=arguments.list[i][0]
		arg2=arguments.list[i][1]
		found=0;
		for j in range(len(options)):
			joption=options[j][0]
			if joption==arg1:
				joption[1]=arg2;
				options[j]=joption;
				found=1;
				break
		if not found:
			#this option did not exist, add it: 
			options.append([arg1,arg2])
	return options
