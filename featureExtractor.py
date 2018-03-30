'''
Gets values of each feature based on state and action
'''

import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        features = util.Counter()

        dir_vec = []
	if action == util.Dirs.LEFT:
	    dir_vec = [0, -1]
	elif action == util.Dirs.RIGHT:
	    dir_vec = [0, 1]
	elif action == util.Dirs.UP:
	    dir_vec = [-1, 0]
	elif action == util.Dirs.DOWN:
	    dir_vec = [1, 0]
	nexty = state.snake[0][1] + (action == util.Dirs.LEFT and -1) + (action == util.Dirs.RIGHT and 1)
	nextx = state.snake[0][0] + (action == util.Dirs.UP and -1) + (action == util.Dirs.DOWN and 1)
	head = util.vectorAdd(state.snake[0], dir_vec)

        wall = 0
	head_i = head
	while not util.outOfBounds(head_i, state.walls):
	    wall += 1
	    head_i = util.vectorAdd(head_i, dir_vec)
	#features["dist-to-wall"] = pow(1 - (wall / float(max(state.walls))), 3)

        food = 0
	head_i = head
	while not util.outOfBounds(head_i, state.walls) and head_i != state.food:
	    food += 1
	    head_i = util.vectorAdd(head_i, dir_vec)
	#features["dist-to-food"] = food / float(max(state.walls))

        '''
        snake = 0
	head_i = head
	while not util.outOfBounds(head_i, state.walls) and head_i not in state.snake:
	    snake += 1
	    head_i = util.vectorAdd(head_i, dir_vec)
	if util.outOfBounds(head_i, state.walls):
	    features["dist-to-snake"] = 0
	else:
	    features["dist-to-snake"] = pow(1 - (snake / float(max(state.walls))), 3)'''


        
	#features["bias--"] = 1.0

	features["on-barrier"] = head in state.snake[0:-1] or util.outOfBounds(head, state.walls)

        dist = (abs(head[0] - state.food[0]) + abs(head[1] - state.food[1])) 
	#features["dist-to-food"] = dist / float(max(state.walls))
	scaledDist = dist / float(state.walls[0] + state.walls[1])
	features["dist-to-food"] = pow(scaledDist, .33)
	#features["not-near-food"] = dist / float(max(state.walls))

	#features["food-nearby"] = dist < 3
        
        #determines if there's a section of snake that's next to a wall
	#features["next-to-wall"] = head[0] == 1 or head[0] == state.walls[0]-2 or head[1] == 1 or head[1] == state.walls[1]-2

        #determines if there is a segment of snake that spans the entire board in the x or y direction
	'''
	spansBoard = True
	for i in range(1, state.walls[1]-1):
	    spansBoard = True
	    for j in range(1, state.walls[0]-1):
	        if state.board[i][j] < util.manhattanDist(head, [i, j]):
		    spansBoard = False
	    if spansBoard:
	        break

        if not spansBoard:
    	    for j in range(1, state.walls[0]-1):
	        spansBoard = True
	        for i in range(1, state.walls[1]-1):
	            if state.board[i][j] < util.manhattanDist(head, [i, j]):
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
	#if action == util.util.Dirs.LEFT:
	#    win.addch(min_y_10, min_x_10, 'X')
	#    win.addch(min_y_10, max_x_10, 'X')
	#    win.addch(max_y_10, min_x_10, 'X')
	#    win.addch(max_y_10, max_x_10, 'X')

	#features["s-perim-4"] = 0 if not features["spans-board"] else perim4


	#features["snake-len"] = len(state.snake) / float(state.walls[0] * state.walls[1])


	#features["dist-to-food-euclidian"] = math.sqrt(pow(abs(head[0] - state.food[0]), 2) + pow(abs(head[1] - state.food[1]), 2)) / float(max(state.walls))'''

        #performs BFS of 'search_size' # of positions to see if head is surrounded by walls
	
        search_size_s = min(pow(max(len(state.snake)/4, 1), 2), 100, state.walls[0] * state.walls[1] - 4 * len(state.snake))
        search_size_b = min(pow(max(len(state.snake)/4, 1), 2), (state.walls[0] * state.walls[1] - len(state.snake)) / 2)
	remaining_nodes_s = search_size_s
	remaining_nodes_b = search_size_b
	oldest_bar = (-1, -1)
	oldest_bar_age = len(state.snake)
        if head in state.snake or util.outOfBounds(head, state.walls):
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
	            if util.outOfBounds(neighbor, state.walls) == False and state.board[neighbor[0]][neighbor[1]] < util.manhattanDist(neighbor, head) and neighbor not in visited_coords:
		        q.append(neighbor)
		        visited_coords.add(neighbor)
		        #win.addstr(neighbor[0], neighbor[1], '.')
        
        '''
        foodReachable = False
	if head not in state.snake and not util.outOfBounds(head, state.walls):
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
		    if util.outOfBounds(neighbor, state.walls) == False and state.board[neighbor[0]][neighbor[1]] < manhattanDist(neighbor, head) and neighbor not in visited_coords:
		        q.put((curtup[1]+1+manhattanDist(curpos, state.food), curtup[1]+1, neighbor))
		        visited_coords.add(neighbor)
			#win.addch(neighbor[0], neighbor[1], '.')'''

        features["trapped"] = (1 - (remaining_nodes_b / float(max(search_size_b, 1))))

        #features["a-star-dist"] = pow((dist if foodReachable else (state.walls[0] * state.walls[1])) / float(state.walls[0] * state.walls[1]), 0.33) if features["trapped"] == 0 else 0

        #features["trapped"] = (1 - (remaining_nodes / float(x*y/2)))


	#features["t-perim-4"] = 0 if features["trapped"] == 0 else perims[0]

	#features["t-perim-9"] = 0 if features["trapped"] == 0 else perims[1]

	#features["t-perim-16"] = 0 if features["trapped"] == 0 else perims[2]


	features["dist-bar"] = 1.0 / pow(util.euclidDist(head, oldest_bar), 2) if features["trapped"] != 0 else 0

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
