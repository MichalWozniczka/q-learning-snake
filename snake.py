import curses, copy, sys, random, math, queue, time, collections
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN

x = 20
y = 40

def outOfBounds(coords, walls):
    if coords[0] < 1 or coords[0] > walls[0]-2 or coords[1] < 1 or coords[1] > walls[1]-2:
        return True
    return False

def manhattanDist(coord1, coord2):
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

def euclidDist(coord1, coord2):
    return math.sqrt(pow(coord1[0] - coord2[0], 2) + pow(coord1[1] - coord2[1], 2))

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

class FeatureExtractor:
    def getFeatures(self, state, action):
        features = Counter()

        dir_vec = []
	if action == Dirs.LEFT:
	    dir_vec = [0, -1]
	elif action == Dirs.RIGHT:
	    dir_vec = [0, 1]
	elif action == Dirs.UP:
	    dir_vec = [-1, 0]
	elif action == Dirs.DOWN:
	    dir_vec = [1, 0]
	nexty = state.snake[0][1] + (action == Dirs.LEFT and -1) + (action == Dirs.RIGHT and 1)
	nextx = state.snake[0][0] + (action == Dirs.UP and -1) + (action == Dirs.DOWN and 1)
	head = vectorAdd(state.snake[0], dir_vec)

        wall = 0
	head_i = head
	while not outOfBounds(head_i, state.walls):
	    wall += 1
	    head_i = vectorAdd(head_i, dir_vec)
	#features["dist-to-wall"] = pow(1 - (wall / float(max(state.walls))), 3)

        food = 0
	head_i = head
	while not outOfBounds(head_i, state.walls) and head_i != state.food:
	    food += 1
	    head_i = vectorAdd(head_i, dir_vec)
	#features["dist-to-food"] = food / float(max(state.walls))

        '''
        snake = 0
	head_i = head
	while not outOfBounds(head_i, state.walls) and head_i not in state.snake:
	    snake += 1
	    head_i = vectorAdd(head_i, dir_vec)
	if outOfBounds(head_i, state.walls):
	    features["dist-to-snake"] = 0
	else:
	    features["dist-to-snake"] = pow(1 - (snake / float(max(state.walls))), 3)'''


        
	#features["bias--"] = 1.0

	features["on-barrier"] = head in state.snake[0:-1] or outOfBounds(head, state.walls)

        dist = (abs(head[0] - state.food[0]) + abs(head[1] - state.food[1])) 
	#features["dist-to-food"] = dist / float(max(state.walls))
	scaledDist = dist / float(state.walls[0] + state.walls[1])
	features["dist-to-food"] = pow(scaledDist, .33)
	#features["not-near-food"] = dist / float(max(state.walls))

	#features["food-nearby"] = dist < 3
        
        #determines if there's a section of snake that's next to a wall
	#features["next-to-wall"] = head[0] == 1 or head[0] == state.walls[0]-2 or head[1] == 1 or head[1] == state.walls[1]-2

        #determines if there is a segment of snake that spans the entire board in the x or y direction
	spansBoard = True
	for i in range(1, x-1):
	    spansBoard = True
	    for j in range(1, y-1):
	        if state.board[i][j] < manhattanDist(head, [i, j]):
		    spansBoard = False
	    if spansBoard:
	        break

        if not spansBoard:
    	    for j in range(1, y-1):
	        spansBoard = True
	        for i in range(1, x-1):
	            if state.board[i][j] < manhattanDist(head, [i, j]):
		        spansBoard = False
	        if spansBoard:
	            break

	#features["spans-board"] = spansBoard

        min_x = head[1]
        max_x = head[1]+1
	min_y = head[0]
	max_y = head[0]+1
	max_list = [0 for a in range(0, 12)]
	for idx, seg in enumerate(state.snake[:-1]):
	    min_x = min(min_x, seg[1])
	    max_x = max(max_x, seg[1]+1)
	    min_y = min(min_y, seg[0])
	    max_y = max(max_y, seg[0]+1)
	    for i in range(2, 5):
	        if idx < pow(i, 2)-1:
	            max_list[(i-2)*4+0] = min_x
		    max_list[(i-2)*4+1] = max_x
		    max_list[(i-2)*4+2] = min_y
		    max_list[(i-2)*4+3] = max_y

	#features["perimiter"] = (max(max_x - min_x, max_y - min_y)) / float(max(state.walls))
	perims = []
	for i in range(0, 3):
	    perims.insert(i, (max(max_list[i*4+1] - max_list[i*4+0], max_list[i*4+3] - max_list[i*4+2]) - (i+2)) / float(pow(i+2, 2) - (i+2)))
	#if action == Dirs.LEFT:
	#    win.addch(min_y_10, min_x_10, 'X')
	#    win.addch(min_y_10, max_x_10, 'X')
	#    win.addch(max_y_10, min_x_10, 'X')
	#    win.addch(max_y_10, max_x_10, 'X')

	#features["s-perim-4"] = 0 if not features["spans-board"] else perim4


	#features["snake-len"] = len(state.snake) / float(state.walls[0] * state.walls[1])


	#features["dist-to-food-euclidian"] = math.sqrt(pow(abs(head[0] - state.food[0]), 2) + pow(abs(head[1] - state.food[1]), 2)) / float(max(state.walls))

        #performs BFS of 'search_size' # of positions to see if head is surrounded by walls
	
        search_size_s = min(pow(max(len(state.snake)/4, 1), 2), 100, state.walls[0] * state.walls[1] - 4 * len(state.snake))
        search_size_b = min(pow(max(len(state.snake)/4, 1), 2), (state.walls[0] * state.walls[1] - len(state.snake)) / 2)
	remaining_nodes_s = search_size_s
	remaining_nodes_b = search_size_b
	oldest_bar = (-1, -1)
	oldest_bar_age = len(state.snake)
        if head in state.snake or outOfBounds(head, state.walls):
	    remaining_nodes_s = 0
	    remaining_nodes_b = 0
	else:
            head_t = (head[0], head[1])
            visited_coords = set(head_t)
	    q = [head_t]
	    for i in range(0,search_size_b):
	        if q:
	            coord = q.pop(0)
                else:
		    if i < search_size_s:
	                remaining_nodes_s = i / 2
	            remaining_nodes_b = i / 2
		    break
	        for neighbor in self.getNeighbors(coord):
		    if state.board[neighbor[0]][neighbor[1]] > 0 and state.board[neighbor[0]][neighbor[1]] < oldest_bar_age:
		        oldest_bar_age = state.board[neighbor[0]][neighbor[1]]
			oldest_bar = neighbor
	            if outOfBounds(neighbor, state.walls) == False and state.board[neighbor[0]][neighbor[1]] < manhattanDist(neighbor, head) and neighbor not in visited_coords:
		        q.append(neighbor)
		        visited_coords.add(neighbor)
		        #win.addstr(neighbor[0], neighbor[1], '.')
        
        '''
        foodReachable = False
	if head not in state.snake and not outOfBounds(head, state.walls):
	    head_t = (head[0], head[1])
	    visited_coords = set(head_t)
	    curpos = head_t
	    q = queue.PriorityQueue()
	    q.put((0, 0, curpos))
	    for i in range(0, x * y / 4):
		if q.empty():
		    remaining_nodes = i
		    break
		curtup = q.get()
		curpos = curtup[2]
		if curpos == tuple(state.food):
		    foodReachable = True
		    dist = curtup[1]
		    break
		for neighbor in self.getNeighbors(curpos):
		    if outOfBounds(neighbor, state.walls) == False and state.board[neighbor[0]][neighbor[1]] < manhattanDist(neighbor, head) and neighbor not in visited_coords:
		        q.put((curtup[1]+1+manhattanDist(curpos, state.food), curtup[1]+1, neighbor))
		        visited_coords.add(neighbor)
			#win.addch(neighbor[0], neighbor[1], '.')'''

        features["trapped"] = (1 - (remaining_nodes_b / float(max(search_size_b, 1))))

        #features["a-star-dist"] = pow((dist if foodReachable else (state.walls[0] * state.walls[1])) / float(state.walls[0] * state.walls[1]), 0.33) if features["trapped"] == 0 else 0

        #features["trapped"] = (1 - (remaining_nodes / float(x*y/2)))


	#features["t-perim-4"] = 0 if features["trapped"] == 0 else perims[0]

	#features["t-perim-9"] = 0 if features["trapped"] == 0 else perims[1]

	#features["t-perim-16"] = 0 if features["trapped"] == 0 else perims[2]


	features["dist-bar"] = 1.0 / pow(euclidDist(head, oldest_bar), 2) if features["trapped"] != 0 else 0

	features["dist-to-food"] = 0 if features["trapped"] != 0 else features["dist-to-food"]

	#features["ts-dist-tail"] = 0 if features["trapped"] == 0 or features["spans-board"] == 0 else manhattanDist(state.snake[0], state.snake[-1]) - manhattanDist(head, state.snake[-1])

	#features["t-dist-tail"] = 0 if features["trapped"] == 0 or features["spans-board"] != 0 else manhattanDist(state.snake[0], state.snake[-1]) - manhattanDist(head, state.snake[-1])

	#features["dist-tail"] = 0 if features["trapped"] != 0 or features["spans-board"] != 0 else manhattanDist(state.snake[0], state.snake[-1]) - manhattanDist(head, state.snake[-1])

        '''
        if features["trapped"] != 0 and features["on-barrier"] == 0:
	    oldest_neighbor = 3 * len(state.snake) / 4
	    for neighbor in self.getNeighbors(head):
	        if(state.board[neighbor[0]][neighbor[1]]) > 0:
	            oldest_neighbor = min(oldest_neighbor, state.board[neighbor[0]][neighbor[1]])
	    features["t-old-ngbr"] = 1 - (oldest_neighbor / float(3 * len(state.snake) / 4))
	else:
	    features["t-old-ngbr"] = 0'''

        '''
	#features["true-dist"] = foodReachable'''



	return features

    #returns list of all positions directly adjacent to coords
    def getNeighbors(self, coords):
        return [(coords[0]-1, coords[1]), (coords[0]+1, coords[1]), (coords[0], coords[1]-1), (coords[0], coords[1]+1)]
	
class QLearningAgent:
    def __init__(self, eps = 0.05, alp = 0.5, disc = 0.99):
        self.epsilon = eps
	self.alpha = alp
	self.discount = disc
	self.qvals = Counter()
	self.feats = None

    def stateToTuple(self, state):
        list_of_tuples = [tuple(list) for list in state.board]
        return tuple(list_of_tuples)

    def getQValue(self, state, action):
        return self.qvals[(self.stateToTuple(state), action)]

    #returns maximum q-value
    def computeValueFromQValues(self, state):
        if state.isLoss():
	    return 0

        maxval = -sys.maxsize - 1
	actions = state.getLegalActions()
	for action in actions:
	    maxval = max(maxval, self.getQValue(state, action))

	return maxval

    #selects action with maximum q-value
    def computeActionFromQValues(self, state):
        if state.isLoss():
	    return 0

        maxval = -sys.maxsize - 1
	actions = state.getLegalActions()
        argmax = Dirs.RIGHT

	for action in actions:
	    qval = self.getQValue(state, action)
	    if qval > maxval:
	        argmax = action
		maxval = qval
	
	return argmax

    #selects random action with epsilon probability, otherwise selects optimal action
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
	nextActions = nextState.getLegalActions()

        maxval = self.getValue(nextState)

	self.qvals[(self.stateToTuple(state), action)] = (1 - self.alpha) * self.getQValue(state, action) + self.alpha * (reward + self.discount * maxval)

        return

    def getPolicy(self, state):
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        return self.computeValueFromQValues(state)

class ApproxQLearningAgent(QLearningAgent):
    def __init__(self, eps = 0.05, alp = 0.5, disc = 0.99):
        QLearningAgent.__init__(self, eps, alp, disc)
        self.weights = Counter()
	self.featExtractor = FeatureExtractor()
	self.feats = Counter()

    def getQValue(self, state, action):
        self.feats = self.featExtractor.getFeatures(state, action)
	return self.feats * self.weights

    #update features based on reward
    def update(self, state, action, nextState, reward):
        maxval = -sys.maxsize - 1
	nextActions = state.getLegalActions()

	#if nextState.isLoss():
	    #maxval = 0

	#for nextAction in nextActions:
	#    maxval = max(maxval, self.getQValue(nextState, nextAction))

	maxval = self.getValue(nextState)

	diff = (reward + self.discount * maxval) - self.getQValue(state, action)

	#feats = self.featExtractor.getFeatures(state, action)

	for key in self.feats:
	    self.weights[key] = self.weights[key] + self.alpha * diff * self.feats[key]

class GameState:
    def __init__(self, prevState = None):
        if prevState == None:
            self.snake = [[1, 1]]
    	    self.food = [x/2, y/2]
	    self.walls = [x, y]
	    self.dir = Dirs.RIGHT
	    self.score = 0
	    self.board = [[0 for a in range(0, y)] for b in range(0, x)]
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
        if outOfBounds(self.snake[0], self.walls) or self.snake[0] in self.snake[1:]:
	    return True
	return False

def main():
    frameLen = 1

    #init values
    win.timeout(frameLen)
    i = 0
    loop = 0
    maxscore = 0
    total = 0
    maxlength = 0
    agent = ApproxQLearningAgent(.0, 0.1, 0.99)
    lengths = []

    #while esc not pressed, run game
    while loop != 27:
        state = GameState()
	nextState = state.generateSuccessor(Dirs.RIGHT)

        #one full game of snake
	while loop != 27:
	    #get optimal action, generate successor state, and update features with the reward
	    action = agent.getAction(state)
	    nextState = state.generateSuccessor(action)
	    agent.update(state, action, nextState, nextState.score - state.score)
	    feats = agent.feats
	    prevState = GameState(state)
	    state = GameState(nextState)

	    maxscore = max(maxscore, state.score)
	    maxlength = max(maxlength, len(state.snake))

            #print info
            win.border(0)
	    for a in range(1, max(y-1, 39)):
	        win.addstr(x-1, a, '_')
		win.addstr(x+10, a, '_')
		win.addstr(x+29, a, '_')
	    if y < 40:
	        for a in range(1, x):
		    win.addstr(a, y, '|')
	    win.addstr(x, 1, 'Length:\t' + str(len(state.snake)) + '     ')
	    win.addstr(x+1, 1, 'Max Length:\t' + str(maxlength) + '     ')
	    win.addstr(x+2, 1, 'Score:\t\t' + str(state.score) + '     ')
	    win.addstr(x+3, 1, 'Max Score:\t' + str(maxscore) + '     ')
	    win.addstr(x+4, 1, 'Average Score:\t' + str(total/max(i, 1)) + '     ')
	    win.addstr(x+5, 1, 'Iteration:\t' + str(i+1) + '     ')
	    win.addstr(x+6, 1, 'QValue:\t' + str(int(agent.getQValue(state, action))))
	    win.addstr(x+7, 1, 'Epsilon:\t' + str(agent.epsilon) + '       ')
	    win.addstr(x+8, 1, 'Learning Rate:\t' + str(agent.alpha) + '       ')
	    win.addstr(x+9, 1, 'Discount:\t' + str(agent.discount) + '       ')
	    win.addstr(x+30, 1, 'Feature name\tValue\tWeight')
	    ofs = 31
	    if feats:
	        for key in feats:
	            win.addstr(x+ofs, 1, key + ':\t' + str(round(feats[key], 4)) + "\t" + str(round(agent.weights[key], 4)))
		    ofs += 1
            #generate successor state
            event = win.getch()
	    if event == -1:
	        loop = loop
	    else:
	        loop = event

            #if feats["trapped"] > 0:
	        #loop = ord(' ')
	    if loop == ord(' '):
	        loop = -1
		nxt = False
		while loop != ord(' '):
		    loop = win.getch()
		    if loop == ord('n'):
		        loop = ord(' ')
			nxt = True
			break
		if not nxt:
		    loop = -1

	    if state.isLoss():
	        break

            #print snake to screen
            for b in range(0, y):
	        for a in range(0, x+10):
	            win.addch(a, b, ' ')
		for a in range(x+33, x+39):
		    win.addch(a, b, ' ')

	    win.addch(state.food[0], state.food[1], '*')

	    for idx, coord in enumerate(state.snake):
	        win.addch(coord[0], coord[1], 'o')

            '''
	    for a in range(1, x):
	        for b in range(0, y):
		    win.addch(a, b, str(state.board[a][b]%10))'''

	agent.epsilon = max(agent.epsilon - 0.0002, 0)
	agent.alpha = max(agent.alpha - 0.0002, 0)
	total += state.score + 10000

	lengths.append(len(state.snake))
	i += 1

	#print graph of snake lengths
	for a in range(x+11, x+29):
	    for b in range(0, max(y, 40)):
	        win.addch(a, b, ' ')
	if i > 0:
	    step = i / float(max(y, 40)-1.999999)
	    for j in range(1, max(y, 40)-1):
		win.addstr(x+28-(lengths[int(step * j)]*16/maxlength), j, 'o')

	'''ofs = 34
	for key in feats:
	    win.addstr(x+ofs, 1, key + ':\t' + str(round(feats[key], 4)) + "\t" + str(round(agent.weights[key], 4)))
	    ofs += 1'''

        fps = 1000 / frameLen
	if loop != 27:
	    #for t in range(0, fps*0.1):
	    for t in range(0, 0):
	        key = win.getch()
	        if key == ord(' '):
	            key = -1
		    while key != ord(' '):
		        key = win.getch()

	if agent.epsilon == 0 and agent.alpha == 0:
	    frameLen = 5

#generate app
curses.initscr()
win = curses.newwin(x+44, max(y, 40), 0, 0)
curses.noecho()
curses.curs_set(0)
win.keypad(1)
win.nodelay(1)
win.border(0)

if __name__ == "__main__": main()
    
curses.endwin()
