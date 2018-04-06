'''
Gets values of each feature based on state and action
'''

import util, snake

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
	head = util.vectorAdd(state.snake[0], dir_vec)

	features["on-barrier"] = state.board[head[0]][head[1]] > 0 or util.outOfBounds(head, state.walls)

        #performs BFS of 'search_size' # of positions to see if head is surrounded by walls
        search_size = min(pow(max(len(state.snake)/4, 1), 2), int((state.walls[0] * state.walls[1] - len(state.snake)) * 0.75))
	remaining_nodes = search_size
	oldest_bar = (-1, -1)
	oldest_bar_age = len(state.snake)
        if head in state.snake or util.outOfBounds(head, state.walls):
	    remaining_nodes = 0
	else:
            head_t = (head[0], head[1])
            visited_coords = set(head_t)
	    q = [head_t]
	    for i in range(0,search_size):
	        if q:
	            coord = q.pop(0)
                else:
	            remaining_nodes = i
		    break
	        for neighbor in self.getNeighbors(coord):
		    if state.board[neighbor[0]][neighbor[1]] > 0 and state.board[neighbor[0]][neighbor[1]] < oldest_bar_age:
		        oldest_bar_age = state.board[neighbor[0]][neighbor[1]]
			oldest_bar = neighbor
	            if util.outOfBounds(neighbor, state.walls) == False and state.board[neighbor[0]][neighbor[1]] < util.manhattanDist(neighbor, head) and neighbor not in visited_coords:
		        q.append(neighbor)
		        visited_coords.add(neighbor)

        len_bin = int(util.sigmoid(len(state.snake)))

        features["trapped-" + str(len_bin)] = (1 - (remaining_nodes / 2.0 / float(max(search_size, 1)))) if remaining_nodes < search_size else 0

	features["trapped"] = features["trapped-" + str(len_bin)]

	features["t-bar-" + str(len_bin)] = 1.0 / pow(util.euclidDist(head, oldest_bar), 2) if features["trapped-" + str(len_bin)] != 0 else 0

	features["t-old-bar"] = features["t-bar-" + str(len_bin)]

	features["dist-food-" + str(len_bin)] = pow(util.manhattanDist(head, state.food) / float(state.walls[0] + state.walls[1]), .33) if features["trapped-" + str(len_bin)] == 0 else 0

        features["dist-food"] = features["dist-food-" + str(len_bin)]

	features["t-exp-bar"] = oldest_bar_age > remaining_nodes if features["trapped-" + str(len_bin)] != 0 else 0

	return features

    #returns list of all positions directly adjacent to coords
    def getNeighbors(self, coords):
        return [(coords[0]-1, coords[1]), (coords[0]+1, coords[1]), (coords[0], coords[1]-1), (coords[0], coords[1]+1)]
