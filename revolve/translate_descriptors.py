# Descriptor translator
# Author: Ozzy Ulger

import yaml
import numpy as np

M_MAX = 20

with open("models/robot_150.yaml", 'r') as stream:
    try:
        file = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

childs = len(file['body']['children'])
modules_amt = 1 + childs

def get_children(yaml_file, grid, loc):
    for i in yaml_file:
        if (i == 0):
            loc[1] -= 1
            grid = np.append(grid, [loc], axis=0)
        if (i == 1):
            loc[1] += 1
            grid = np.append(grid, [loc], axis=0)
        if (i == 2):
            loc[0] += 1
            grid = np.append(grid, [loc], axis=0)
        if (i == 3):
            loc[0] -= 1
            grid = np.append(grid, [loc], axis=0)
    return grid

core_module = np.array([[0,0]])
grid = core_module

for i in file['body']['children']:
    if (i == 0):
        loc = [0, -1]
        grid = np.append(grid, [loc], axis=0)
        try:
            grid = get_children(file['body']['children'][i]['children'], grid, loc)
        except:
            pass
    if (i == 1):
        loc = [0, 1]
        grid = np.append(grid, [loc], axis=0)
        try:
            grid = get_children(file['body']['children'][i]['children'], grid, loc)
        except:
            pass
    if (i == 2):
        loc = [1, 0]
        grid = np.append(grid, [loc], axis=0)
        try:
            grid = get_children(file['body']['children'][i]['children'], grid, loc)
        except:
            pass
    if (i == 3):
        loc = [-1, 0]
        grid = np.append(grid, [loc], axis=0)
        try:
            grid = get_children(file['body']['children'][i]['children'], grid, loc)
        except:
            pass

def make_grid(grid):
    maximas = np.amax(grid, axis=0)
    minimas = np.amin(grid, axis=0)
    x_length = maximas[0] - minimas[0]
    y_length = maximas[1] - minimas[1]
    x = np.arange(minimas[0], maximas[0] + 1)
    y = np.arange(minimas[1], maximas[1] + 1)
    X,Y = np.meshgrid(x,y)
    XY = np.array([X.flatten(),Y.flatten()]).T
    return XY, x_length, y_length

grid, x_length, y_length = make_grid(grid)

def calc_size(modules_amt):
    return float(modules_amt)/float(M_MAX)

def calc_proportion(x_length, y_length):
    if (x_length == y_length):
        return 1
    elif (x_length < y_length):
        return float(x_length)/float(y_length)
    else:
        return float(y_length)/float(x_length)


print("Size = ", calc_size(modules_amt))
print("Proportion = ", calc_proportion(x_length, y_length))
print("Grid = ", grid)
