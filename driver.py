'''
	Magic Square Solver.
	Author: Patrick Damery
'''
import random
import sys
import os
import time
import resource
import hashlib
import math

# Define the Node Class.
class Node:
	def __init__(self, parent, board, last_move, depth, cost, priority):
		self.parent = parent
		self.board = board
		self.checksum = board.getChecksum()
		self.last_move = last_move
		self.children = []
		self.depth = depth
		self.branch_cost = cost
		self.priority = priority

	def __cmp__(self, other):
		if hasattr(other, 'priority'):
			return self.priority.__cmp__(other.priority)

	def getParent(self):
		return self.parent

	def getChildren(self):
		return self.children

	def getPriority(self):
		return self.priority

	def getChecksum(self):
		return self.checksum

	def getBoard(self):
		return self.board

	def getLastMove(self):
		return self.last_move

	def getDepth(self):
		return self.depth

	def getBranchCost(self):
		return self.branch_cost

	def increasePriority(self):
		self.priority -= 1

	def addChild(self, child):
		self.children.append(child)

	def hasChildren(self):
		return self.children == []

# Define the Node Tree Class.
class NodeTree:
    def __init__(self, node):
        self.nodes = [node]

    def isEmpty(self):
        return self.nodes == []

    def enqueue(self, node):
        self.nodes.append(node)

    def pop(self):
        return self.nodes.pop(0)

    def sort(self):
    	self.nodes = sorted(self.nodes)

    def getTree(self):
    	return self.nodes

    def size(self):
        return len(self.nodes)

    def peek(self):
    	return self.nodes[len(self.nodes)-1]

# Define the Node Queue Class.
class NodeQueue:
    def __init__(self, node):
        self.nodes = [node]

    def isEmpty(self):
        return self.items == []

    def enqueue(self, node):
        self.nodes.insert(0,node)

    def pop(self):
        return self.nodes.pop()

    def getQueue(self):
    	return self.nodes

    def size(self):
        return len(self.nodes)

# Define the Node Stack Class.
class NodeStack:
    def __init__(self, node):
        self.nodes = [node]

    def isEmpty(self):
        return self.items == []

    def push(self, node):
        self.nodes.append(node)

    def pop(self):
        return self.nodes.pop()

    def getTree(self):
    	return self.nodes

    def size(self):
        return len(self.nodes)

    def peek(self):
    	return self.nodes[len(self.nodes)-1]

# Define the Board Class.
class Board:
	def __init__(self, size, moveInfo):
		self.board_layout = []
		for n in range(0, size):
			self.board_layout.append(n)
		self.move_info = moveInfo


	def updateBoard(self, board):
		for i in range(0, len(self.board_layout)):
			self.board_layout[i] = board[i]

	def getPosition(self, number):
		for i in range(0, len(self.board_layout)):
			if number == int(self.board_layout[i]):
				return i

	def getMovementOptions(self, position):
		return self.move_info[position]['movement_options']

	def moveTile(self, blank, tile):
		value_of_tile_to_replace = self.board_layout[tile]
		self.board_layout[tile] = 0
		self.board_layout[blank] = value_of_tile_to_replace

	def getValues(self):
		return self.board_layout

	def getChecksum(self):
		string_values = ''
		for x in range(0, len(self.board_layout)):
			string_values += str(self.board_layout[x])

		return hashlib.md5(string_values).hexdigest()

	def manhattan(self):
		cost = 0
		for x in range(0, len(self.board_layout)):
			desired_position = int(self.board_layout[x])
			row_diff = abs(self.move_info[x]['manhattan'][0]-self.move_info[desired_position]['manhattan'][0])
			col_diff = abs(self.move_info[x]['manhattan'][1]-self.move_info[desired_position]['manhattan'][1])
			cost += row_diff+col_diff

		return cost

# Define the State Class.
class State:
	def __init__(self, size, moves):
		# This is where we define what arrangement we want.
		self.result = 'working'
		self.desired_board = Board(size, moves)
		self.final_node = 0
		self.max_fringe = 0
		self.max_depth = 0
		self.time = time.time()
		self.ram = 0
		self.nodes_expanded = 0

	def setResult(self, result):
		self.result = result

	def setRAM(self):
		self.ram = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000

	def setFringe(self, fringe):
		self.max_fringe = fringe

	def setDepth(self, depth):
		self.max_depth = depth

	def setFinalNode(self, node):
		self.final_node = node

	def checkBoard(self, current_board):
		if self.desired_board.getValues() != current_board.getValues():
			return 0
		return 1

	def checkResult(self):
		return self.result

	def getFinalNode(self):
		return self.final_node

	def getTime(self):
		return self.time

	def getMaxFringe(self):
		return self.max_fringe

	def getMaxDepth(self):
		return self.max_depth

	def getRAM(self):
		return self.ram

# Define the Solver Class.
class Solver:
	def __init__(self, board, layout, method):

		self.method = method
		self.explored = set()
		self.movement_layout = layout
		self.state = State(len(board), self.movement_layout)
		self.board_size = len(board)
		temp_board = Board(len(board), self.movement_layout)
		temp_board.updateBoard(board)
		if method == 'bfs':
			node = Node(0, temp_board, 'Start', 0, 0, 0)
			self.queue = NodeQueue(node)
		elif method == 'dfs':
			node = Node(0, temp_board, 'Start', 0, 0, 0)
			self.stack = NodeStack(node)
		elif method == 'ast':
			manhattan = temp_board.manhattan()
			node = Node(0, temp_board, 'Start', 0, 0, manhattan)
			self.tree = NodeTree(node)
		else:
			manhattan = temp_board.manhattan()
			self.rootNode = Node(0, temp_board, 'Start', 0, 0, manhattan)
			self.priorityLimit = manhattan


	def nextMove(self):
		# Breadth-first search.
		if self.method == 'bfs':
			# Decide on next move.
			result = self.bfs()
			if result != 'working':
				self.state.setResult(result)
		# Depth first search.
		elif self.method == 'dfs':
			result = self.dfs()
			if result != 'working':
				self.state.setResult(result)
		# A-Star.
		elif self.method == 'ast':
			result = self.ast()
			if result != 'working':
				self.state.setResult(result)
		# Iterative deepening A-Star.
		else:
			result = self.ida()
			if result != 'working':
				self.state.setResult(result)

	# Breadth-first search method.
	def bfs(self):

		# Pop the next node.
		node = self.queue.pop()

		# Check if it is the desired board state.
		if self.state.checkBoard(node.getBoard()):
			self.state.setFinalNode(node)
			self.state.setRAM()
			return 'success'

		# Update state.
		self.state.nodes_expanded += 1

		# Explore the children of this node.
		current_board = node.getBoard()
		current_position = current_board.getPosition(0)

		# Get movements available and explore them.
		movements = current_board.getMovementOptions(current_position)
		for move in movements:

			move_text = move[0]
			move_position = move[1]
			temp_board = Board(self.board_size, self.movement_layout)
			temp_board.updateBoard(current_board.getValues())
			temp_board.moveTile(current_position, move_position)

			# Check if we have already explored this board result.
			if self.checkExplored(temp_board) != 1:
				# Create node and add it to parent node.
				temp_node = Node(node, temp_board, move_text, node.getDepth()+1, node.getBranchCost()+1, 0)
				node.addChild(temp_node)
				self.queue.enqueue(temp_node)
				if self.state.getMaxDepth() < temp_node.getDepth():
					self.state.setDepth(temp_node.getDepth())

		if self.state.getMaxFringe() < self.queue.size():
			self.state.setFringe(self.queue.size())

		# Add to explored list.
		self.explored.add(node.getChecksum())

		return 'working'

	# Depth first search method.
	def dfs(self):
		# Pop the next node.
		node = self.stack.pop()

		# Check if it is the desired board state.
		if self.state.checkBoard(node.getBoard()):
			self.state.setFinalNode(node)
			self.state.setRAM()
			return 'success'

		# Update state.
		self.state.nodes_expanded += 1

		# Explore the children of this node.
		current_board = node.getBoard()
		current_position = current_board.getPosition(0)

		# Get movements available and explore them.
		movements = current_board.getMovementOptions(current_position)
		for move in reversed(movements):
			move_text = move[0]
			move_position = move[1]
			temp_board = Board(self.board_size, self.movement_layout)
			temp_board.updateBoard(current_board.getValues())
			temp_board.moveTile(current_position, move_position)

			# Check if we have already explored this board result.
			if self.checkExplored(temp_board) != 1:
				# Create node and add it to parent node.
				temp_node = Node(node, temp_board, move_text, node.getDepth()+1, node.getBranchCost()+1, 0)
				node.addChild(temp_node)
				self.stack.push(temp_node)
				if self.state.getMaxDepth() < temp_node.getDepth():
					self.state.setDepth(temp_node.getDepth())

		if self.state.getMaxFringe() < self.stack.size():
			self.state.setFringe(self.stack.size())

		# Add to explored list.
		self.explored.add(node.getChecksum())

		return 'working'

	# A-Star method.
	def ast(self):
		# Pop the next node.
		node = self.tree.pop()

		# Check if it is the desired board state.
		if self.state.checkBoard(node.getBoard()):
			self.state.setFinalNode(node)
			self.state.setRAM()
			return 'success'

		# Update state.
		self.state.nodes_expanded += 1

		# Explore the children of this node.
		current_board = node.getBoard()
		current_position = current_board.getPosition(0)

		# Get movements available and explore them.
		movements = current_board.getMovementOptions(current_position)
		for move in reversed(movements):
			move_text = move[0]
			move_position = move[1]
			temp_board = Board(self.board_size, self.movement_layout)
			temp_board.updateBoard(current_board.getValues())
			temp_board.moveTile(current_position, move_position)

			# Check if we have already explored this board result.
			if self.checkExplored(temp_board) != 1:
				# Create node and add it to parent node.
				temp_node = Node(node, temp_board, move_text, node.getDepth()+1, node.getBranchCost()+1, node.getBranchCost()+temp_board.manhattan())
				node.addChild(temp_node)
				self.tree.enqueue(temp_node)
				if self.state.getMaxDepth() < temp_node.getDepth():
					self.state.setDepth(temp_node.getDepth())

		if self.state.getMaxFringe() < self.tree.size():
			self.state.setFringe(self.tree.size())

		# Sort Priority Tree
		self.tree.sort()

		# Add to explored list.
		self.explored.add(node.getChecksum())

		return 'working'

	# Iterative deepening A-Star method.
	def ida(self):

		# Get first node and current limit.
		node = self.rootNode
		priority = self.priorityLimit
		nextPriority = 9999999999999

		# Initialize a stack for Iterative Deepening.
		stack = NodeStack(node)

		# Reset node expansion tracker and explored set.
		self.state.nodes_expanded = 0
		self.state.max_fringe = 0
		self.explored = set()

		# Start IDA.
		while stack.size() != 0:
			n = stack.pop()

			# Check if it is the desired board state.
			if self.state.checkBoard(n.getBoard()):
				self.state.setFinalNode(n)
				self.state.setRAM()
				self.stack = stack
				return 'success'

			# Update state.
			self.state.nodes_expanded += 1

			# Explore the children of this node.
			current_board = n.getBoard()
			current_position = current_board.getPosition(0)

			# Get movements available and explore them.
			movements = current_board.getMovementOptions(current_position)
			for move in reversed(movements):
				move_text = move[0]
				move_position = move[1]
				temp_board = Board(self.board_size, self.movement_layout)
				temp_board.updateBoard(current_board.getValues())
				temp_board.moveTile(current_position, move_position)

				# Check if we have already explored this board result.
				if self.checkExplored(temp_board) != 1:
					# Check if it's within the current limit.
					currentPriority = n.getBranchCost()+temp_board.manhattan()
					if currentPriority > priority:
						if currentPriority < nextPriority:
							nextPriority = currentPriority
					else:
						# Create node and add it to parent node.
						temp_node = Node(n, temp_board, move_text, n.getDepth()+1, n.getBranchCost()+1, currentPriority)
						n.addChild(temp_node)
						stack.push(temp_node)
						if self.state.getMaxDepth() < temp_node.getDepth():
							self.state.setDepth(temp_node.getDepth())

			if self.state.getMaxFringe() < stack.size():
				self.state.setFringe(stack.size())

			# Add to explored list.
			self.explored.add(n.getChecksum())

		self.priorityLimit = nextPriority;
		return 'working'


	def finished(self):
		return self.state.checkResult()

	def checkExplored(self, node):
		l = len(self.explored)
		self.explored.add(node.getChecksum())
		if l == len(self.explored):
			return 1

		return 0

# Get the arguments.
method = sys.argv[1]
temp_board = sys.argv[2].split(',')
board = []

# Sanitize board so we have a normal array.
for x in temp_board:
		board.append(int(x))

board_size = len(temp_board)
root = math.sqrt(board_size)
row_count = 0
col_count = 0
rows = board_size/root
layout = {}
for i in range (0, board_size):

	# Next Column.
	col_count += 1
	# Check if next row.
	if (i % root) == 0:
		row_count += 1
		col_count = 1

	# Check if it's the first row.
	if row_count == 1:
		# Check if we are on the left side.
		if i == 0:
			layout[i] = {'movement_options': [['Down', int(i+root)], ['Right', i+1]], 'manhattan': [row_count, col_count]}
		# Check if we are on the right side.
		elif i == (root - 1):
			layout[i] = {'movement_options': [['Down', int(i+root)], ['Left', i-1]], 'manhattan': [row_count, col_count]}
		else:
			layout[i] = {'movement_options': [['Down', int(i+root)], ['Left', i-1], ['Right', i+1]], 'manhattan': [row_count, col_count]}
	# Check if it's the last row.
	elif row_count == rows:
		# Check if we are on the left side.
		if i == board_size-root:
			layout[i]  ={'movement_options': [['Up', int(i-root)], ['Right', i+1]], 'manhattan': [row_count, col_count]}
		# Check if we are on the right side.
		elif i == (board_size-1):
			layout[i] = {'movement_options': [['Up', int(i-root)], ['Left', i-1]], 'manhattan': [row_count, col_count]}
		else:
			layout[i] = {'movement_options': [['Up', int(i-root)], ['Left', i-1], ['Right', i+1]], 'manhattan': [row_count, col_count]}
	# We must be in the middle somewhere.
	else:
		# Check if we are on the left side.
		if (i % root) == 0:
			layout[i] = {'movement_options': [['Up', int(i-root)], ['Down', int(i+root)], ['Right', i+1]], 'manhattan': [row_count, col_count]}
		# Check if we are on the right side.
		elif (i+1) % root == 0:
			layout[i] = {'movement_options': [['Up', int(i-root)], ['Down', int(i+root)], ['Left', i-1]], 'manhattan': [row_count, col_count]}
		else:
			layout[i] = {'movement_options': [['Up', int(i-root)], ['Down', int(i+root)], ['Left', i-1], ['Right', i+1]], 'manhattan': [row_count, col_count]}


# Now initiate the Solver class and get it to work.
solver = Solver(board, layout, method)

while solver.finished() == 'working':
	solver.nextMove()


moves = []
node = solver.state.getFinalNode()
cost = node.getBranchCost()
depth = node.getDepth()

while node.getLastMove() != 'Start':
	moves.append(node.getLastMove())
	node = node.getParent()

moves.reverse()

# Create file.
file = open('output.txt', 'w+')

file.write('path_to_goal: [')
n = 0
for m in moves:
	if n == len(moves)-1:
		file.write("'"+m+"'")
	else:
		file.write("'"+m+"', ")
	n += 1
file.write(']')
file.write('\n')
file.write('cost_of_path: ' + str(cost))
file.write('\n')
file.write('nodes_expanded: ' + str(solver.state.nodes_expanded))
file.write('\n')
if method == 'bfs':
	file.write('fringe_size: ' + str(solver.queue.size()))
elif method == 'dfs':
	file.write('fringe_size: ' + str(solver.stack.size()))
elif method == 'ast':
	file.write('fringe_size: ' + str(solver.tree.size()))
else:
	file.write('fringe_size: ' + str(solver.stack.size()))
file.write('\n')
file.write('max_fringe_size: ' + str(solver.state.getMaxFringe()))
file.write('\n')
file.write('search_depth: ' + str(depth))
file.write('\n')
file.write('max_search_depth: ' + str(solver.state.getMaxDepth()))
file.write('\n')
file.write('running_time: ' + str((time.time()) - solver.state.getTime()))
file.write('\n')
file.write('max_ram_usage: ' + str(solver.state.getRAM()))
