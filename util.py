'''
Helper functions and such
'''

import math

def outOfBounds(coords, walls):
    if coords[0] < 1 or coords[0] > walls[0]-2 or coords[1] < 1 or coords[1] > walls[1]-2:
        return True
    return False

def manhattanDist(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

def euclidDist(coord1, coord2):
    return math.sqrt(pow(coord1[0] - coord2[0], 2) + pow(coord1[1] - coord2[1], 2))

def sigmoid(x):
    return 80 / (1 + math.exp(-(x-400)/100.0))

def vectorAdd(coord1, coord2):
    return [coord1[0] + coord2[0], coord1[1] + coord2[1]]

class Dirs:
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'

class Counter(dict):
    def __getitem__(self, idx):
        self.setdefault(idx, 0)
	return dict.__getitem__(self, idx)

    def __mul__(self, y):
        sum = 0
        x = self
        if len(x) > len(y):
            x,y = y,x
        for key in x:
            if key not in y:
                continue
            sum += x[key] * y[key]
        return sum
