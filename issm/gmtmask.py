from issm.MatlabFuncs import *
from issm.model import *
import numpy as np
from os import getenv, putenv
import subprocess

def gmtmask(lat,long,*varargin):
#GMTMASK - figure out which lat,long points are on the ocean
#
#   Usage:
#      mask.ocean = gmtmask(md.mesh.lat,md.mesh.long);
#
	lenlat=len(lat)
	mask=np.empty(lenlat)
	
	#are we doing a recursive call? 
	if len(varargin)==3:
		recursive=1
	else:
		recursive=0

	if recursive:
		string='             recursing: num vertices #i'+str(lenlat)
	else:
		string='gmtmask: num vertices #i'+str(lenlat)
	
	#Check lat and long size is not more than 50,000 If so, recursively call gmtmask: 

	if lenlat>50000:
		for i in range(ceil(lenlat/50000)):
			j=(i+1)*50000-1
			if j>lenlat:
				j=lenlat
			mask[i:j]=gmtmask(lat[i:j],long[i:j],1)
		return mask
	
	
	#First, write our lat,long file for gmt:
	nv=lenlat
	np.savetxt('./all_vertices.txt',np.transpose([long, lat, np.arange(1,nv+1)]),delimiter='\t',fmt='%.10f')

	#Avoid bypassing of the ld library path by Matlab (:()
	try:
		issmdir
	except:
		issmdir=getenv('ISSM_DIR')
	try:
		ismac
	except:
		ismac=False	

	if ismac:
		dyld_library_path_old=getenv('DYLD_LIBRARY_PATH')
		putenv('DYLD_LIBRARY_PATH',issmdir+'/externalpackages/curl/install/lib:'+issmdir+'/externalpackages/hdf5/install/lib:'+issmdir+'/externalpackages/netcdf/install/lib')
		
	#figure out which vertices are on the ocean, which one on the continent:
	subprocess.call(issmdir+'/externalpackages/gmt/install/bin/gmt gmtselect ./all_vertices.txt -h0 -Df -R0/360/-90/90  -A0 -JQ180/200 -Nk/s/s/k/s > ./oce_vertices.txt',shell=True)

	#reset DYLD_LIBRARY_PATH to what it was: 
	if ismac:
		putenv('DYLD_LIBRARY_PATH',dyld_library_path_old)
	
	#read the con_vertices.txt file and flag our mesh vertices on the continent
	fid=open('./oce_vertices.txt','r')
	line=fid.readline()
	line=fid.readline()
	oce_vertices=[]
	while line:
		ind=int(float(line.split()[2]))-1;
		oce_vertices.append(ind)
		line=fid.readline()
	fid.close()

	mask=np.zeros([nv,1])
	mask[oce_vertices]=1
	
	subprocess.call('rm -rf ./all_vertices.txt ./oce_vertices.txt ./gmt.history',shell=True)
	if not recursive:
		string='gmtmask: done'
	return mask
