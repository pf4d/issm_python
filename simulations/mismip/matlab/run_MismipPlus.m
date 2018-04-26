clear all;

gosolve=1;
istsai=0;
isweert=1;
isschoof=0;
load_data_Cornford_weert=1;
load_data_Cornford_tsai=0;
isquad=1;
cluster=0;
hmin=4000;

if(isquad==1);
    Lx=640000;
    Ly=80000;
    nx=Lx/(10000);
    ny=Ly/(4000);
    md=squaremesh(model,Lx,Ly,nx,ny);
else
    md=triangle(model,'./Exp/MismipDomain.exp',10000);
    h=NaN*ones(md.mesh.numberofvertices,1);
    in=ContourToNodes(md.mesh.x,md.mesh.y,'./Exp/MismipRefinedDomain.exp',1);
    h(find(in))=hmin;
    md=bamg(md,'hmin',hmin,'hmax',10000,'hVertices',h);%,'gradation',1.7);
end

% Parametrization
md=setmask(md,'','');
md=parameterize(md,'./Par/MismipPlus.m');
md = extrude(md,5,1);
md=setflowequation(md,'HO','all');
md.flowequation.fe_HO='P1bubble';


if (isweert==1);
    %frictionlaw set in para file
    md.miscellaneous.name='M+_weert';
elseif(istsai==1)
    md.friction=frictioncoulomb();
    md.friction.coefficient=sqrt(3.160e6)*ones(md.mesh.numberofvertices,1);
    md.friction.coefficientcoulomb=sqrt(0.5)*ones(md.mesh.numberofvertices,1);
    md.friction.p=3*ones(md.mesh.numberofelements,1);
    md.friction.q=zeros(md.mesh.numberofelements,1);
    md.miscellaneous.name='M+_tsai';
elseif(isschoof==1)
    %TODO
    md.miscellaneous.name='M+_schoof';
end

% tansient settings
md.transient.isgroundingline=1;
md.transient.ismasstransport=1;
md.transient.issmb=1;
md.timestepping.time_adapt=0;
md.timestepping.cfl_coefficient=0.5;
md.timestepping.time_step=hmin/1000.0*0.5;
md.timestepping.final_time=5000;
if(hmin==4000)
    md.settings.output_frequency=1;
elseif(hmin==2000)
    md.settings.output_frequency=10;
elseif(hmin==1000)
    md.settings.output_frequency=20;
elseif(hmin==500)
    md.settings.output_frequency=40;
end

md.balancethickness.stabilization=0;%2
md.masstransport.stabilization=0;%1

disp('   SOLVER');
md.transient.requested_outputs={'default','GroundedArea','FloatingArea','IceVolume','IceVolumeAboveFloatation'};
%% SOLVER
if (cluster==1);
    md.settings.waitonlock=Inf;
    md.verbose=verbose('solution',true,'control',true,'convergence',true);
    md.cluster=uv100('name','uv100.awi.de','login','mrueckam','np',96,'queue','plarge','time',21000);
    md.cluster=uv100('name','uv100.awi.de','login','mrueckam','np',96,'queue','plong');
    if(gosolve==1), md=solve(md,TransientSolutionEnum()); end;
    
else
    md.cluster=generic('name',oshostname,'np',4);
    md.verbose=verbose('solution',true,'control',true,'convergence',true);
    if(gosolve==1), md=solve(md,TransientSolutionEnum()); end;
end
