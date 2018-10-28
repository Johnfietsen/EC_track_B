# Descriptor translator
# Author: Ozzy Ulger

import yaml
import numpy as np

# M_MAX = 20

def calculate_rotation(arity, parent_slot, parent_rotation):
    if (arity == 4):
        if (parent_slot == 0):
          return (parent_rotation + 2) % 4
        if (parent_slot == 1):
          return parents_rotation
        if (parent_slot == 2):
          return (parents_rotation + 3) % 4
        if (parent_slot == 3):
          return (parents_rotation + 1) % 4


def parse_offspring(offspring_dict, x, y, rotation):
    # print('foo', children)
    print(offspring_dict)
    print("\n")

def parse_core(robot):
    arity = 4
    x = y = rotation = 0
    offspring_dict = robot['body']['children']
    for child in offspring_dict:
        offspring_rotation = calculate_rotation(arity, parent_slot, rotation)
        # parse_offspring(offspring_dict[child], x, y, rotation)
    print(x)
    print(y)
    print(rotation)


def open_robot(filename):
    with open(filename, 'r') as stream:
        try:
            robot = yaml.safe_load(stream)
            return robot
        except yaml.YAMLError as exc:
            print(exc)

robot = open_robot("revolve/models/robot_150.yaml")
parse_core(robot)
