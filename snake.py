import gameState, learningAgents, util

try:
    from tkinter import *
except ImportError:
    from Tkinter import *

from PIL import ImageTk
from PIL import Image

class Gui():
    def __init__(self, w, h, x, y):
        self.window = Tk()
	self.canvas = Canvas(self.window, width=w, height=h, bg='#bdbdbd', relief=RIDGE)
	self.canvas.pack(side=LEFT)

	self.plot = Canvas(self.window, width=w/2, height=h/2, bg='#ffffff', relief=RIDGE)
	self.plot.pack(side=TOP)

	self.label = Label(self.window, justify=LEFT, font=('Courier New', 16))
	self.label.pack(side=TOP)

        self.tileSize = min(w/(x-2), h/(y-2))
	self.boardWidth = x
	self.boardHeight = y

	spritesheet = Image.open('assets/spritesheet.png')

	self.bg = ImageTk.PhotoImage(spritesheet.crop((0, 0, 8, 8)).resize((self.tileSize, self.tileSize)))
	self.snake = ImageTk.PhotoImage(spritesheet.crop((8, 0, 16, 8)).resize((self.tileSize, self.tileSize)))
	self.food = ImageTk.PhotoImage(spritesheet.crop((16, 0, 24, 8)).resize((self.tileSize, self.tileSize)))

	self.canvas.create_image(0, 0, image=self.bg)

    def draw(self, state):
        self.canvas.delete("all")
        for j in range(self.boardWidth-2):
	    for i in range(self.boardHeight-2):
	        if state.board[i+1][j+1] == -1:
		    self.canvas.create_image(j*self.tileSize, i*self.tileSize, image=self.food, anchor=NW)
		elif state.board[i+1][j+1] > 0:
		    self.canvas.create_image(j*self.tileSize, i*self.tileSize, image=self.snake, anchor=NW)
		else:
		    self.canvas.create_image(j*self.tileSize, i*self.tileSize, image=self.bg, anchor=NW)

    def changeLabelText(self, text):
        self.label['text'] = text

    def updateGraph(self, lengths):
        self.plot.delete("all")
	pointSep = self.plot.winfo_width()/(len(lengths)+1)
	plotHeight = self.plot.winfo_height()
	maxLen = max(lengths)
	for idx, length in enumerate(lengths):
	    pointHeight = plotHeight - (float(length)/maxLen * plotHeight)
	    pointHeight = int(pointHeight)
	    self.plot.create_oval(pointSep*(idx+1)-3, pointHeight-3, pointSep*(idx+1)+3, pointHeight+3)

def main():    
    #init values
    i = 0
    maxscore = 0
    total = 0
    maxlength = 0
    agent = learningAgents.ApproxQLearningAgent(0, 0.1, 0.99)
    lengths = []

    x = 20
    y = 20

    gui = Gui(800, 800, x, y)
    
    while True:
        state = gameState.GameState(None, x, y)
	nextState = state.generateSuccessor(util.Dirs.RIGHT)

        #one full game of snake
	while True:
	    #get optimal action, generate successor state, and update features with the reward
	    action = agent.getAction(state)
	    nextState = state.generateSuccessor(action)
	    agent.update(state, action, nextState, nextState.score - state.score)
	    feats = agent.feats
	    prevState = gameState.GameState(state)
	    state = gameState.GameState(nextState)
	    gui.draw(state)
	    gui.window.update()

	    maxscore = max(maxscore, state.score)
	    maxlength = max(maxlength, len(state.snake))

            labelText = ''
	    labelText += 'Length:\t\t' + str(len(state.snake)) + '\n'
	    labelText += 'Max Length:\t' + str(maxlength) + '\n'
	    labelText += 'Score:\t\t' + str(state.score) + '\n'
	    labelText += 'Max Score:\t' + str(maxscore) + '\n'
	    labelText += 'Average Score:\t' + str(total/max(i, 1)) + '\n'
	    labelText += 'Iteration:\t' + str(i+1) + '\n'
	    labelText += 'QValue:\t\t' + str(int(agent.getQValue(state, action))) + '\n'
	    labelText += 'Epsilon:\t' + str(agent.epsilon) + '\n'
	    labelText += 'Learning Rate:\t' + str(agent.alpha) + '\n'
	    labelText += 'Discount:\t' + str(agent.discount) + '\n\n'
	    labelText += 'Feature name\tValue\tWeight\n'
	    for key in feats:
	        labelText += key + ':\t' + str(round(feats[key], 4)) + "\t" + str(round(agent.weights[key], 4)) + '\n'
	    gui.changeLabelText(labelText)

	    if state.isLoss():
	        break

	agent.epsilon = max(agent.epsilon - 0.0005, 0)
	agent.alpha = max(agent.alpha - 0.0005, 0)
	total += state.score + 10000

        
	lengths.append(len(state.snake))
	i += 1
	gui.updateGraph(lengths)
         

if __name__ == "__main__": main()
