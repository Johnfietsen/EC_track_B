FROM cigroup/gazebo:gazebo6-revolve

# Dependencies
RUN apt-get install -y build-essential      \
                       cmake                \
                       cppcheck             \
                       git                  \
                       xsltproc             \
                       python               \
                       python-pip           \
                       gsl-bin libgsl0-dev  \
                       mercurial

ADD . /revolve
RUN /revolve/docker/build_revolve.sh
