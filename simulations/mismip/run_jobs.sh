#!/bin/bash

# dx 1000, 32 nodes, 0.25 dt, 12 hours runtime:
#
# iteration 7212/80000  time [yr]: 1803 (time step: 0.25)
#
# dx 1000, 16 nodes, 0.25 dt, 12 hours runtime:
#
# iteration 10849/80000  time [yr]: 2712 (time step: 0.25)
#
# dx 1000, 8 nodes, 0.25 dt, 12 hours runtime:
#
# iteration 5787/80000  time [yr]: 1447 (time step: 0.25)

# for dx = 2000:
#dt     =  0.5         # [a] time step
#dt_sav =  10.0        # [a] time interval to save data
#cfl    =  0.5         # [--] CFL coefficient
#nodes  =  4           # [--] number of nodes to use
#ntpn   =  36          # [--] number of tasks per node
#ntasks =  nodes*ntpn  # [--] number of processor cores to use
#time   =  48*60       # [min] time to complete
#part   = 'mpp'        # [--] partition of ``ollie`` to use

# for dx = 4000:
#dt     =  1.0         # [a] time step
#dt_sav =  10.0        # [a] time interval to save data
#cfl    =  0.5         # [--] CFL coefficient
#nodes  =  1           # [--] number of nodes to use
#ntpn   =  36          # [--] number of tasks per node
#ntasks =  nodes*ntpn  # [--] number of processor cores to use
#time   =  12*60       # [min] time to complete
#part   = 'smp'        # [--] partition of ``ollie`` to use

# for dx = 8000:
#dt     =  1.0         # [a] time step
#dt_sav =  10.0        # [a] time interval to save data
#cfl    =  0.5         # [--] CFL coefficient
#nodes  =  1           # [--] number of nodes to use
#ntpn   =  9           # [--] number of tasks per node
#ntasks =  nodes*ntpn  # [--] number of processor cores to use
#time   =  12*60       # [min] time to complete
#part   = 'smp'        # [--] partition of ``ollie`` to use


for i in `seq 12000 1000 20000`; do
  python mismip.py $i;
done
