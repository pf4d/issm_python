%Ok, start defining model parameters here

load_data_Cornford_weert=1;
load_data_Cornford_tsai=0;

%Parameters
md.materials.rho_ice=918;
md.materials.rho_water=1028;
md.constants.g=9.81;
md.constants.yts=31556926; 
md.transient.isthermal=0;

md.stressbalance.isnewton=2; % 2 for standard sliding
md.stressbalance.maxiter=50;
%md.stressbalance.viscosity_overshoot=0.1;
md.stressbalance.restol=0.001;

disp('      creating geometry');
Lx=640000;
Ly=80000;
B0=-150;
B2=-728.8;
B4=343.91;
B6=-50.57;
x_quer=300000;
fc=4000;
dc=500;
wc=24000;
Bmax=720;

x_tilde=md.mesh.x/x_quer;
Bx = B0 + B2*x_tilde.^2 + B4*x_tilde.^4 + B6*x_tilde.^6;
By = (dc./(1+exp(-2*(md.mesh.y-Ly/2-wc)/fc)) + dc./(1+exp(2*(md.mesh.y-Ly/2+wc)/fc)));
md.geometry.bed=max(Bx+By,-Bmax);

if(load_data_Cornford_weert==1);
    ncdata=('./data_Cornford/weertman-A2.2e-17-ssa_thickness.nc');
    x = ncread(ncdata,'x');
    y = ncread(ncdata,'y');
    thck = ncread(ncdata,'thickness');
    md.geometry.thickness=InterpFromGridToMesh(x,y,thck',md.mesh.x,md.mesh.y,10);
    pos=find(md.geometry.thickness<10);
    md.geometry.thickness(pos)=10;
elseif(load_data_Cornford_tsai==1);
    ncdata=('../data_Cornford/tsai-A2.2e-17-ssa_thickness.nc');
    x = ncread(ncdata,'x');
    y = ncread(ncdata,'y');
    thck = ncread(ncdata,'thickness');
    md.geometry.thickness=InterpFromGridToMesh(x,y,thck',md.mesh.x,md.mesh.y,0);
else
    initial_thickness=100;
    md.geometry.thickness=initial_thickness*ones(md.mesh.numberofvertices,1);
end
md.mask.groundedice_levelset=md.geometry.thickness + md.materials.rho_water/md.materials.rho_ice*md.geometry.bed;
grounded=find(md.mask.groundedice_levelset>0);
floating=find(md.mask.groundedice_levelset<=0);
md.geometry.surface=md.geometry.bed+md.geometry.thickness;
%md.geometry.surface(floating)=initial_thickness*(1-md.materials.rho_ice/md.materials.rho_water);
md.geometry.surface(floating)=md.geometry.thickness(floating)*(1-md.materials.rho_ice/md.materials.rho_water);
md.geometry.base=md.geometry.surface-md.geometry.thickness;

disp('      creating drag');
md.friction.coefficient=sqrt(3.160*10^6)*ones(md.mesh.numberofvertices,1);
md.friction.p=3*ones(md.mesh.numberofelements,1);
md.friction.q=zeros(md.mesh.numberofelements,1);

disp('      creating flow law paramter');
md.materials.rheology_B=(6.338*10^-25)^(-1/3)*ones(md.mesh.numberofvertices,1);
%md.materials.rheology_B=paterson(253.15*ones(md.mesh.numberofvertices,1));
md.materials.rheology_n=3.*ones(md.mesh.numberofelements,1);
md.materials.rheology_law='None';

disp('      boundary conditions for diagnostic model');
%Create node on boundary fist (because we cannot use mesh)
md=SetIceShelfBC(md,'./Exp/MismipFront.exp');
% md.stressbalance.spcvx(:)=NaN;
% md.stressbalance.spcvy(:)=NaN;
% md.stressbalance.spcvz(:)=NaN;

pos_u=find(md.mesh.y<max(md.mesh.y)+0.1 & md.mesh.y>max(md.mesh.y)-0.1);
md.stressbalance.spcvx(pos_u)=NaN;
md.stressbalance.spcvy(pos_u)=0;
md.stressbalance.spcvz(pos_u)=0;

pos_l=find(md.mesh.y<0.1 & md.mesh.y>-0.1);
md.stressbalance.spcvx(pos_l)=NaN;
md.stressbalance.spcvy(pos_l)=0;
md.stressbalance.spcvz(pos_l)=0;

% %Create MPCs to have periodic boundary conditions
% posx=find(md.mesh.x==0.);
% posx2=find(md.mesh.x==max(md.mesh.x));
% 
% md.stressbalance.vertex_pairing=[posx,posx2];

pos2=find(md.mesh.x<0.1 & md.mesh.x>-0.1);
md.stressbalance.spcvx(pos2)=0;
md.stressbalance.spcvy(pos2)=0;
md.stressbalance.spcvz(pos2)=0;

disp('      forcing conditions');
md.smb.mass_balance=0.3*ones(md.mesh.numberofvertices,1);

md.thermal.spctemperature=NaN*ones(md.mesh.numberofvertices,1);
md.groundingline.migration='AggressiveMigration';
md.groundingline.migration='SoftMigration';
md.groundingline.migration='SubelementMigration2';

%md.groundingline.migration='None';
md.masstransport.hydrostatic_adjustment='Incremental';

%Initialization
md.initialization.vx=4000*ones(md.mesh.numberofvertices,1);
md.initialization.vy=0*ones(md.mesh.numberofvertices,1);
md.initialization.vz=0*ones(md.mesh.numberofvertices,1);
md.initialization.vel=0*sqrt(2)*ones(md.mesh.numberofvertices,1);
md.initialization.pressure=md.constants.g*md.materials.rho_ice*md.geometry.thickness;
md.initialization.temperature=273*ones(md.mesh.numberofvertices,1);
