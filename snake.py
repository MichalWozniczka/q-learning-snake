import curses, copy, sys, random
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN

x = 10
y = 10

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

class FeatureExtractor:
    def getFeatures(self, state, action):
        features = Counter()

	nexty = state.snake[0][1] + (state.dir == Dirs.LEFT and -1) + (state.dir == Dirs.RIGHT and 1)
	nextx = state.snake[0][0] + (state.dir == Dirs.UP and -1) + (state.dir == Dirs.DOWN and 1)
	head = [nextx, nexty]

	features["barrier-1-away"] = head in state.snake[1:] or head[0] == 0 or head[0] == state.walls[0]-1 or head[1] == 0 or head[1] == state.walls[1]-1
	
	features["dist-to-food"] = (abs(head[0] - state.food[0]) + abs(head[1] - state.food[1])) / float(max(state.walls))

	return features

class LearningAgent:
    def __init__(self, eps = 0.0, alp = 0.5, disc = 0.9):
        self.weights = Counter()
	self.featExtractor = FeatureExtractor()
	self.epsilon = eps
	self.alpha = alp
	self.discount = disc

    def getQValue(self, state, action):
        return self.featExtractor.getFeatures(state, action) * self.weights

    def computeValueFromQValues(self, state):
        if state.isLoss():
	    return 0

        maxval = -sys.maxsize - 1
	actions = state.getLegalActions()
	for action in actions:
	    maxval = max(maxval, self.getQValue(state, action))

    def computeActionFromQValues(self, state):
        if state.isLoss():
	    return 0

        maxval = -sys.maxsize - 1
	actions = state.getLegalActions()
        argmax = Dirs.DOWN

	#for action in actions:
	#    qval = self.getQValue(state, action)
	#    if qval > maxval:
	#        argamx = action
	#	maxval = qval
	
	return argmax

    def getAction(self, state):
        if state.isLoss():
	    return Dirs.RIGHT

	actions = state.getLegalActions()
	
	if random.random() < self.epsilon:
	    action = random.choice(actions)
	else:
	    action = self.computeActionFromQValues(state)

        return action

    def update(self, state, action, nextState, reward):
        maxval = -sys.maxsize - 1
	nextActions = state.getLegalActions()

	if nextState.isLoss():
	    maxval = 0

	for nextAction in nextActions:
	    maxval = max(maxval, self.getQValue(nextState, nextAction))

	diff = (reward + self.discount * maxval) - self.getQValue(state, action)

	feats = self.featExtractor.getFeatures(state, action)

	for key in feats:
	    self.weights[key] = self.weights[key] + self.alpha * diff * feats[key]

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)

class GameState:
    def __init__(self, prevState = None):
        if prevState == None:
            self.snake = [[1, 1]]
    	    self.food = [2, 1]
	    self.walls = [x, y]
	    self.dir = Dirs.RIGHT
	    self.score = 0
	else:
	    self.snake = copy.deepcopy(prevState.snake)
	    self.food = copy.deepcopy(prevState.food)
	    self.walls = copy.deepcopy(prevState.walls)
	    self.dir = prevState.dir
	    self.score = prevState.score

    def getLegalActions(self):
        if self.isLoss(): return []
        actions = [Dirs.LEFT, Dirs.RIGHT, Dirs.UP, Dirs.DOWN]
	if self.dir == Dirs.LEFT:
	    actions.remove(Dirs.RIGHT)
	elif self.dir == Dirs.RIGHT:
	    actions.remove(Dirs.LEFT)
	elif self.dir == Dirs.UP:
	    actions.remove(Dirs.DOWN)
	elif self.dir == Dirs.DOWN:
	    actions.remove(Dirs.UP)
	return actions

    def generateSuccessor(self, action):
        state = GameState(self)

        #find pos of new head
        state.dir = action
        state.snake.insert(0, [state.snake[0][0] + (state.dir == Dirs.DOWN and 1) + (state.dir == Dirs.UP and -1), state.snake[0][1] + (state.dir == Dirs.LEFT and -1) + (state.dir == Dirs.RIGHT and 1)])

        #eat food if needed
	if state.snake[0] == state.food:
	    state.food = []
	    state.score += 1
	    while state.food == []:
	        state.food = [random.randint(1, state.walls[0]-2), random.randint(1, state.walls[1]-2)]
		if state.food in state.snake: 
		    state.food = []
	else:
	    state.snake.pop()

	if state.isLoss():
	    state.score -= 500

	return state

    def isLoss(self):
        if self.snake[0][0] == 0 or self.snake[0][0] == self.walls[0]-1 or self.snake[0][1] == 0 or self.snake[0][1] == self.walls[1]-1 or self.snake[0] in self.snake[1:]:
	    return True
	return False

def main():
    frameLen = 500

    #init values
    win.timeout(frameLen)
    i = 0
    loop = 0
    maxscore = 0
    agent = LearningAgent()

    #while esc not pressed, run game
    while loop != 27:
        state = GameState()
	nextState = state.generateSuccessor(Dirs.RIGHT)

	while loop != 27:
	    action = agent.getAction(state)
	    nextState = state.generateSuccessor(action)
	    agent.update(state, action, nextState, nextState.score - state.score)
	    state = GameState(nextState)
	    maxscore = max(maxscore, state.score)

            win.border(0)
            #win.addstr(0, 0, str(maxscore) + ', ' + str(state.score) + '   ')
	    win.addstr(0, 0, str(int(agent.getQValue(state, action))) + '   ')

            #generate successor state
            event = win.getch()
	    if event == -1:
	        loop = loop
	    else:
	        loop = event

            #print snake to screen
            for a in range(1, x-1):
	        for b in range(1, y-1):
	            win.addch(a, b, ' ')

	    win.addch(state.food[0], state.food[1], '*')

	    for coord in state.snake:
	        win.addch(coord[0], coord[1], 'o')

	    if state.isLoss():
	        break

    #terminate app
    #curses.echo()
    #curses.nocbreak()
    #win.keypad(0)

#generate app
curses.initscr()
win = curses.newwin(x, y, 0, 0)
curses.noecho()
curses.curs_set(0)
#curses.cbreak()
win.keypad(1)
win.nodelay(1)
win.border(0)

if __name__ == "__main__": main()
    
curses.endwin()
