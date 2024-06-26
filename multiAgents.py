# multiAgents.py
# azhan zaheer
# css 382 a roger stanev
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.
    """
    
    def getAction(self, gameState):
        """
        getAction chooses among the best options according to the evaluation function.
        
        Just like in the previous project, getAction takes a GameState and returns some
        Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()
        
        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best
        
        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.
        
        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.
        """
        # Generate the successor game state after taking the action
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        # Heuristic components
        foodList = newFood.asList()
        ghostPositions = [ghostState.getPosition() for ghostState in newGhostStates]

        # Initialize score
        score = successorGameState.getScore()
        
        # Closest food distance
        if foodList:
            closestFoodDist = min(manhattanDistance(newPos, food) for food in foodList)
        else:
            closestFoodDist = 0

        # Reciprocal of the closest food distance to prioritize closer food
        if closestFoodDist > 0:
            foodScore = 1.0 / closestFoodDist
        else:
            foodScore = 0

        # Closest ghost distance
        ghostDistances = [manhattanDistance(newPos, ghostPos) for ghostPos in ghostPositions]
        if ghostDistances:
            closestGhostDist = min(ghostDistances)
        else:
            closestGhostDist = float('inf')

        # Penalty for being too close to a ghost
        if closestGhostDist > 0:
            ghostPenalty = -1.0 / closestGhostDist
        else:
            ghostPenalty = -float('inf')

        # Avoid ghosts
        if closestGhostDist <= 1:
            ghostPenalty = -10

        # Combine factors into a final score
        final_score = score + foodScore + ghostPenalty
        
        return final_score

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
            Returns the total number of agents in the game
        """

        def minimax(agentIndex, depth, gameState):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            if agentIndex == 0:  # Pacman's turn (Maximizer)
                return max_value(agentIndex, depth, gameState)
            else:  # Ghosts' turn (Minimizer)
                return min_value(agentIndex, depth, gameState)

        def max_value(agentIndex, depth, gameState):
            v = float('-inf')
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)

            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v = max(v, minimax(1, depth, successor))
            return v

        def min_value(agentIndex, depth, gameState):
            v = float('inf')
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)

            nextAgent = agentIndex + 1
            if nextAgent == gameState.getNumAgents():
                nextAgent = 0
                depth += 1

            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v = min(v, minimax(nextAgent, depth, successor))
            return v

        # Initial call from Pacman's perspective
        legalActions = gameState.getLegalActions(0)
        scores = [(action, minimax(1, 0, gameState.generateSuccessor(0, action))) for action in legalActions]
        bestAction = max(scores, key=lambda x: x[1])[0]

        return bestAction


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """

        def alphabeta(agentIndex, depth, gameState, alpha, beta):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            if agentIndex == 0:  # Pacman's turn (Maximizer)
                return max_value(agentIndex, depth, gameState, alpha, beta)
            else:  # Ghosts' turn (Minimizer)
                return min_value(agentIndex, depth, gameState, alpha, beta)

        def max_value(agentIndex, depth, gameState, alpha, beta):
            v = float('-inf')
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)

            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v = max(v, alphabeta(1, depth, successor, alpha, beta))
                if v > beta:
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(agentIndex, depth, gameState, alpha, beta):
            v = float('inf')
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)

            nextAgent = agentIndex + 1
            if nextAgent == gameState.getNumAgents():
                nextAgent = 0
                depth += 1

            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v = min(v, alphabeta(nextAgent, depth, successor, alpha, beta))
                if v < alpha:
                    return v
                beta = min(beta, v)
            return v

        # Initial call from Pacman's perspective
        alpha = float('-inf')
        beta = float('inf')
        legalActions = gameState.getLegalActions(0)
        bestAction = None
        v = float('-inf')

        for action in legalActions:
            successor = gameState.generateSuccessor(0, action)
            new_v = alphabeta(1, 0, successor, alpha, beta)
            if new_v > v:
                v = new_v
                bestAction = action
            alpha = max(alpha, v)
        
        return bestAction

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
    Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action from the current gameState using self.depth
        and self.evaluationFunction.
        """

        def expectimax(agentIndex, depth, gameState):
            if gameState.isWin() or gameState.isLose() or depth == self.depth:
                return self.evaluationFunction(gameState)
            
            if agentIndex == 0:  # Pacman's turn (Maximizer)
                return max_value(agentIndex, depth, gameState)
            else:  # Ghosts' turn (Chance nodes)
                return exp_value(agentIndex, depth, gameState)

        def max_value(agentIndex, depth, gameState):
            v = float('-inf')
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)

            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v = max(v, expectimax(1, depth, successor))
            return v

        def exp_value(agentIndex, depth, gameState):
            v = 0
            legalActions = gameState.getLegalActions(agentIndex)
            if not legalActions:
                return self.evaluationFunction(gameState)

            p = 1.0 / len(legalActions)
            nextAgent = agentIndex + 1
            if nextAgent == gameState.getNumAgents():
                nextAgent = 0
                depth += 1

            for action in legalActions:
                successor = gameState.generateSuccessor(agentIndex, action)
                v += p * expectimax(nextAgent, depth, successor)
            return v

        # Initial call from Pacman's perspective
        legalActions = gameState.getLegalActions(0)
        scores = [(action, expectimax(1, 0, gameState.generateSuccessor(0, action))) for action in legalActions]
        bestAction = max(scores, key=lambda x: x[1])[0]

        return bestAction

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: This evaluation function calculates the score based on the current game state.
    It considers the distance to the nearest food, the distance to the nearest ghost, the number
    of remaining food pellets, and the proximity to power pellets. The score is adjusted to prioritize
    getting closer to food while avoiding ghosts, and to incentivize clearing the board quickly.
    """
    # Useful information you can extract from a GameState (pacman.py)
    pacmanPosition = currentGameState.getPacmanPosition()
    food = currentGameState.getFood()
    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    capsules = currentGameState.getCapsules()
    
    # Score from the current game state
    score = currentGameState.getScore()
    
    # Distance to the nearest food
    foodList = food.asList()
    if foodList:
        minFoodDistance = min([util.manhattanDistance(pacmanPosition, food) for food in foodList])
    else:
        minFoodDistance = 0
    
    # Distance to the nearest ghost
    ghostDistances = [util.manhattanDistance(pacmanPosition, ghost.getPosition()) for ghost in ghostStates]
    minGhostDistance = min(ghostDistances) if ghostDistances else float('inf')
    
    # Distance to the nearest capsule
    if capsules:
        minCapsuleDistance = min([util.manhattanDistance(pacmanPosition, capsule) for capsule in capsules])
    else:
        minCapsuleDistance = float('inf')
    
    # Adjust score based on food and ghost distances
    if minGhostDistance > 0:
        score += 1.0 / minGhostDistance
    
    score -= 1.5 * minFoodDistance
    
    # Additional consideration for the number of remaining food pellets
    score -= 4 * len(foodList)
    
    # Additional consideration for proximity to capsules
    if minCapsuleDistance < float('inf'):
        score += 1.5 / minCapsuleDistance
    
    # Additional consideration for scared ghosts
    score += sum(scaredTimes)
    
    return score

# Abbreviation
better = betterEvaluationFunction


# Abbreviation
better = betterEvaluationFunction
