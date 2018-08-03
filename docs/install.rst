Installation
=======================


Using Docker
------------------------

This the the preferred way to run this program.  Once you have `docker <https://www.docker.com/>`_ installed, you can install ISSM with::

  docker pull pf4d/issm

Then run it like this::

  docker run -it pf4d/issm

From source on Ubuntu 16.04 LTS
----------------------------------

If you prefer to install from source, the following method will get things working in Ubuntu 16.04 LTS; change the first environment variable ``$ISSM_GIT_DIR`` to a directory you prefer::

  function install_issm()
  {
    export ISSM_GIT_DIR="$HOME/software";
    export ISSM_DIR="$ISSM_GIT_DIR/issm/trunk";
    cd $ISSM_GIT_DIR;
    git clone https://github.com/pf4d/issm.git; 
    sudo apt-get install libtool cmake autotools-dev python python-numpy;
    cd $ISSM_DIR/externalpackages/m1qn3;
    ./install.sh;
    cd $ISSM_DIR/externalpackages/mpich;
    ./install-3.0-linux64.sh;
    cd $ISSM_DIR/externalpackages/petsc;
    ./install-3.6-linux64.sh;
    cd $ISSM_DIR/externalpackages/triangle;
    ./install-linux64.sh;
    source $ISSM_DIR/etc/environment.sh;
    cd $ISSM_DIR;
    autoreconf -ivf;
    ./configure \
      --prefix="$ISSM_DIR" \
      --with-python-dir="/usr" \
      --with-fortran-lib="-L/usr/lib/x86_64-linux-gnu/ -lgfortran" \
      --with-python-numpy-dir="/usr/lib/python2.7/dist-packages/numpy" \
      --with-triangle-dir="$ISSM_DIR/externalpackages/triangle/install" \
      --with-mpi-include="$ISSM_DIR/externalpackages/mpich/install/include"  \
      --with-mpi-libflags="-L$ISSM_DIR/externalpackages/mpich/install/lib -lmpich -lmpl" \
      --with-petsc-dir="$ISSM_DIR/externalpackages/petsc/install" \
      --with-scalapack-dir="$ISSM_DIR/externalpackages/petsc/install/" \
      --with-mumps-dir="$ISSM_DIR/externalpackages/petsc/install/" \
      --with-blas-lapack-dir="$ISSM_DIR/externalpackages/petsc/install" \
      --with-metis-dir="$ISSM_DIR/externalpackages/petsc/install/" \
      --with-m1qn3-dir="$ISSM_DIR/externalpackages/m1qn3/install" \
      --with-numthreads=2;
    make -j4;
    make install;
  }

You might like to add this function to your .bashrc file so that you can load the dependencies as needed in order to avoid package conflicts::
  
  function load_issm()
  {
    export ISSM_DIR="$HOME/software/issm/trunk"
    source $ISSM_DIR/etc/environment.sh 
    export PYTHONPATH="$HOME/software/issm/trunk/bin:$PYTHONPATH"
    export PYTHONPATH="$HOME/software/issm/trunk/lib:$PYTHONPATH"
  }

Test your installation by first loading the environment variables in bash::

  load_issm
  
then entering in an ``ipython`` terminal::

  import model



