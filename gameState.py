'''
Gamestate for snake game
'''

import util, copy, random

class GameState:
    def __init__(self, prevState = None, x = 20, y = 40):
        if prevState == None:
            self.snake = [[1, 1]]
    	    self.food = [x/2, y/2]
	    self.walls = [x, y]
	    self.dir = util.Dirs.RIGHT
	    self.score = 0
	    self.board = [[0 for a in range(0, y+1)] for b in range(0, x+1)]
	    self.board[1][1] = 1
	else:
	    self.snake = copy.deepcopy(prevState.snake)
	    self.food = copy.deepcopy(prevState.food)
	    self.walls = copy.deepcopy(prevState.walls)
	    self.dir = prevState.dir
	    self.score = prevState.score
	    self.board = copy.deepcopy(prevState.board)

    def getLegalActions(self):
        if self.isLoss(): return []
        actions = [util.Dirs.LEFT, util.Dirs.RIGHT, util.Dirs.UP, util.Dirs.DOWN]
	if self.dir == util.Dirs.LEFT:
	    actions.remove(util.Dirs.RIGHT)
	elif self.dir == util.Dirs.RIGHT:
	    actions.remove(util.Dirs.LEFT)
	elif self.dir == util.Dirs.UP:
	    actions.remove(util.Dirs.DOWN)
	elif self.dir == util.Dirs.DOWN:
	    actions.remove(util.Dirs.UP)
	return actions

    def generateSuccessor(self, action):
        state = GameState(self)

        #find pos of new head
        state.dir = action
        state.snake.insert(0, [state.snake[0][0] + (state.dir == util.Dirs.DOWN and 1) + (state.dir == util.Dirs.UP and -1), state.snake[0][1] + (state.dir == util.Dirs.LEFT and -1) + (state.dir == util.Dirs.RIGHT and 1)])
	state.board[state.snake[0][0]][state.snake[0][1]] = len(state.snake)

        #eat food if needed
	if state.snake[0] == state.food:
	    state.food = []
	    state.score += 100
	    while state.food == []:
	        state.food = [random.randint(1, state.walls[0]-2), random.randint(1, state.walls[1]-2)]
		if state.food in state.snake: 
		    state.food = []
	    state.board[state.food[0]][state.food[1]] = -1
	else:
	    for coord in state.snake:
	        state.board[coord[0]][coord[1]] -= 1
	    oldpos = state.snake.pop()
	    state.score -= 1

	if state.isLoss():
	    state.score -= 500

	return state

    def isLoss(self):
        if util.outOfBounds(self.snake[0], self.walls) or self.snake[0] in self.snake[1:]:
	    return True
	return False
