#!/bin/bash

export PYTHONPATH=/opt/coevolution/l-system/build/lib:${PYTHONPATH}
export LD_LIBRARY_PATH=/opt/coevolution/tol-revolve/build:${LD_LIBRARY_PATH}
export GAZEBO_MODEL_PATH=${GAZEBO_MODEL_PATH}:/opt/coevolution/tol-revolve/tools/models:/opt/coevolution/gzmodels

# https://stackoverflow.com/questions/10987246/xvfb-multiple-displays-for-parallel-processing
# use -audit 4 to debug xvfb
sudo Xvfb :0 -ac -noreset -listen tcp -maxclients 2048 &

sudo sh -c "echo 'DISPLAY=:0' >> /etc/environment"
export DISPLAY=:0 


until xset -q >/dev/null 2>&1; do echo "Waiting for xserver..."; sleep 1; done


cd /opt/coevolution/l-system/build/bin
#./lsystem_proto || { echo "Error."; sleep 10000; }
cd /opt/coevolution/tol-revolve/scripts/offline-evolve

python start.py

