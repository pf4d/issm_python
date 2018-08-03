FROM phusion/baseimage:0.9.22
MAINTAINER pf4d <mail@cummings.evan@gmail.com>

USER root

ENV  ISSM_HOME /home/issm/
ENV  ISSM_DIR $ISSM_HOME/issm/trunk
ENV  ISSM_VERSION 4.12

# get ubuntu updates :
RUN apt-get update && \
    apt-get upgrade -y -o Dpkg::Options::="--force-confold" && \
    apt-get -y install locales sudo && \
    echo "C.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# get issm-required packages supplied by apt :
RUN apt-get update && \ 
    apt-get -y install git \
                       g++ \
                       gfortran \
                       unzip \
                       libtool \
                       cmake \
                       autoconf \
                       autotools-dev \
                       python \
                       python-numpy \
                       python-matplotlib \
                       python-scipy \
                       python-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# download ipython --- the latest version --- because it is best :
RUN pip install --upgrade pip
RUN pip install ipython

# Turn off forwarding of syslog messages to stdout
# https://github.com/phusion/baseimage-docker/issues/186
RUN touch /etc/service/syslog-forwarder/down

# set up user 'issm' :
RUN useradd -m -s /bin/bash -G sudo,docker_env issm && \
    echo "issm:docker" | chpasswd && \
    echo "issm ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers && \
    echo "cat $ISSM_HOME/WELCOME" >> /home/issm/.bashrc

# install issm :
USER issm

# git the repository :
RUN  cd $ISSM_HOME && git clone https://github.com/pf4d/issm
RUN  cd $ISSM_HOME && git clone https://github.com/pf4d/issm_python

# install dependencies shipped with issm :
RUN cd $ISSM_DIR/externalpackages/m1qn3 && \
    ./install.sh
RUN cd $ISSM_DIR/externalpackages/mpich && \
    ./install-3.0-linux64.sh
RUN cd $ISSM_DIR/externalpackages/petsc && \
    ./install-3.6-linux64.sh
RUN cd $ISSM_DIR/externalpackages/triangle && \
    ./install-linux64.sh

# configure issm :
RUN /bin/bash -c "source $ISSM_DIR/etc/environment.sh" && \
    cd $ISSM_DIR && \
    autoreconf -ivf && \
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
      --with-numthreads=2 && \
    make -j4 && \
    make install

RUN /bin/bash -c "source $ISSM_DIR/etc/environment.sh"

# make python packages available :
ENV PYTHONPATH $ISSM_DIR/bin:$PYTHONPATH
ENV PYTHONPATH $ISSM_DIR/lib:$PYTHONPATH

# add the welcome message :
COPY WELCOME $ISSM_HOME/WELCOME

# make sure that the issm evironment is loaded :
RUN echo "\nsource $ISSM_DIR/etc/environment.sh" >> /home/issm/.bashrc

# change to the user's directory :
WORKDIR $ISSM_HOME

USER root
ENTRYPOINT ["/sbin/my_init","--quiet","--","/sbin/setuser", \
            "issm", "/bin/bash", "-c", "/bin/bash","-l","-c"]
CMD ["/bin/bash", "-i"]



