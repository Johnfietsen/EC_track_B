#!/usr/bin/env python2

import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from pygazebo.pygazebo import DisconnectError
from trollius.py33_exceptions import ConnectionResetError

import trollius
from trollius import From

from revolve.tol.manage import World
from revolve.tol.config import parser

from sdfbuilder import Pose
from sdfbuilder.math import Vector3

from revolve.convert.yaml import yaml_to_robot
from revolve.angle import Tree
from revolve.util import wait_for

from revolve.logging import logger



@trollius.coroutine
def run():

    which_robots = ['260']
    # ['21', '22', '23', '24', '25', '26', '27', '28', '29', '30']

    # Parse command line / file input arguments
    conf = parser.parse_args()

    conf.output_directory = "output"
    conf.restore_directory = "restore"


    bot_yaml = []

    for robot in which_robots:
        with open("models/robot_" + robot + ".yaml", 'r') as yamlfile:
            bot_yaml.append(yamlfile.read())


    # Create the world, this connects to the Gazebo world
    world = yield From(World.create(conf))

    # These are useful when working with YAML
    body_spec = world.builder.body_builder.spec
    brain_spec = world.builder.brain_builder.spec

    # Create a robot from YAML

    protobot = []

    for robot in bot_yaml:
        protobot.append(yaml_to_robot(
                        body_spec=body_spec,
                        nn_spec=brain_spec,
                        yaml=robot))

    # Create a revolve.angle `Tree` representation from the robot, which
    # is what is used in the world manager.

    robot_tree = []

    for robot in protobot:
        robot_tree.append(Tree.from_body_brain(
                            body=robot.body,
                            brain=robot.brain,
                            body_spec=body_spec))

    # Insert the robot into the world. `insert_robot` resolves when the insert
    # request is sent, the future it returns resolves when the robot insert
    # is actually confirmed and a robot manager object has been created


    pose = []

    middle = len(which_robots) / 2

    for i in range(0, len(robot_tree)):
        pose.append(Pose(position=Vector3(i - middle, i - middle, 1)))


    for i in range(0, len(robot_tree)):
        future = yield From(world.insert_robot(
            tree=robot_tree[i],
            pose=pose[i],
    ))

    robot_manager = yield From(future)
    yield From(wait_for(world.pause(True)))

    # Start a run loop to do some stuff
    while True:
        # Print robot fitness every second
        print ("Robot fitness is {fitness}".format(
                fitness=robot_manager.fitness()))
        yield From(trollius.sleep(1.0))


def main():
    def handler(loop, context):
        exc = context['exception']
        if isinstance(exc, DisconnectError) \
                or isinstance(exc, ConnectionResetError):
            print("Got disconnect / connection reset - shutting down.")
            sys.exit(0)
        raise context['exception']

    try:
        loop = trollius.get_event_loop()
        loop.set_exception_handler(handler)
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Got CtrlC, shutting down.")


if __name__ == '__main__':
    main()
