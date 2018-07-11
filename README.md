# About

A reionforcement learning snake game that utilizes feature-based approximate q-learning. Because the complexity of a gamestate of snake is exponential, exact q-learning is practically impossible. Instead, feature-based q-learning aims to describe the gamestate using a set of "features", or functions that take aspects of the gamestate and return numerical values. These features comprise a feature vector, which is multiplied with a weight vector that is learned through reinforcement to find the optimal weight vector that maximizes rewards.

In the case of this application, the snake receives a large negative reward for "dying" (running into a wall or itself), a smaller positive reward for eating a food pellet, and a very small negative reward for simply transitioning states without dying or eating food. The snake starts with a learning rate of 0.1, and the learning rate is slowly turned down as more games are played in order to capitalize on previously learned information.

Read more about q-learning: https://en.wikipedia.org/wiki/Q-learning. 

# Features

Features are defined in featureExtractor.py. 

`on-barrier`: Boolean indicating whether head of snake is touching a wall or itself

`dist-oldest`: Euclidian distance to the oldest snake segment

`dist-food`: Manhattan distance to the food

`trapped`: Boolean indicating whether snake is surrounded by walls or its own body

# How to run

```
python snake.py
```

# Technologies

Written in Python

GUI created with TKinter
