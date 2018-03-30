'''
Provides classes for q-learning routines
'''

import util, featureExtractor, random, sys

class QLearningAgent:
    def __init__(self, eps = 0.05, alp = 0.5, disc = 0.99):
        self.epsilon = eps
	self.alpha = alp
	self.discount = disc
	self.qvals = util.Counter()
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
        argmax = util.Dirs.RIGHT

	for action in actions:
	    qval = self.getQValue(state, action)
	    if qval > maxval:
	        argmax = action
		maxval = qval
	
	return argmax

    #selects random action with epsilon probability, otherwise selects optimal action
    def getAction(self, state):
        if state.isLoss():
	    return util.Dirs.RIGHT

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
        self.weights = util.Counter()
	self.featExtractor = featureExtractor.FeatureExtractor()
	self.feats = util.Counter()

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
