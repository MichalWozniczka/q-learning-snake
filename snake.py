import curses, gameState, learningAgents, util

x = 20
y = 40

def main():    
    frameLen = 1

    #init values
    win.timeout(frameLen)
    i = 0
    loop = 0
    maxscore = 0
    total = 0
    maxlength = 0
    agent = learningAgents.ApproxQLearningAgent(.0, 0.1, 0.99)
    lengths = []

    #while esc not pressed, run game
    while loop != 27:
        state = gameState.GameState(None, x, y)
	nextState = state.generateSuccessor(util.Dirs.RIGHT)

        #one full game of snake
	while loop != 27:
	    #get optimal action, generate successor state, and update features with the reward
	    action = agent.getAction(state)
	    nextState = state.generateSuccessor(action)
	    agent.update(state, action, nextState, nextState.score - state.score)
	    feats = agent.feats
	    prevState = gameState.GameState(state)
	    state = gameState.GameState(nextState)

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
