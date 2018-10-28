import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
rvpath = os.path.abspath(os.path.join(here, '..', 'revolve'))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from revolve.util import Supervisor

if __name__ == "__main__":
    supervisor = Supervisor(
            manager_cmd=os.path.join(here, "tutorial4_speed.py"),
            world_file="worlds/gait-learning.world",
            gazebo_cmd="gzserver",
            gazebo_args=["--verbose"],
            plugins_dir_path=os.path.join(rvpath, 'build', 'lib'),
            models_dir_path=os.path.join(rvpath, 'models')
    )

    ret = supervisor.launch()
    sys.exit(ret)
