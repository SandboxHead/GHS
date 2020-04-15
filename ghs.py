from queue import Queue
import math 
import sys
from operator import itemgetter, attrgetter

# Node states
sleep = 0
find = 1
found =2

# Edge states
basic = 0
branch = 1
reject = 2

# Message type number
connect = 0
initiate = 1
test = 2
reject = 3
accept = 4
report = 5
changeroot = 6
awake = 7

stop = 0
debug = 1

class Edge:
	def __init__(self, v, weight):
		self.v = v
		self.weight = weight
		self.state = basic

	# def __eq__(self, other):
	# 	return self.weight == other.weight

	def __gt__(self, other):
		if(other.state != basic):
			return False
		if(self.state != basic):
			return True

		return self.weight > other.weight

	def __lt__(self, other):
		if(other.state != basic):
			return True
		if(self.state != basic):
			return False

		return self.weight < other.weight

class Node:
	def __init__(self, nodeid, name):
		self.state = sleep
		self.name = name
		self.level = 0
		self.parent = None
		self.nodeid = nodeid
		self.queue = Queue()
		self.edges = {}
		self.stop = 0
		self.done = False

	def __str__(self):
		output = ''
		output += '[@] Node Id: {}\n'.format(self.nodeid)
		output += '[@] Node Name: {}\n'.format(self.name)
		output += '[@] Node Parent: {}\n'.format(self.parent)
		output += '[@] Node Level: {}\n'.format(self.level)
		output += '[@] Edges: \n'
		for key in self.edges:
			output += '{} {}\n'.format(self.edges[key].v.nodeid, self.edges[key].weight)
		output += "\n"
		return output

	def add_edge(self, neighbour, weight):
		self.edges[neighbour.nodeid] = Edge(neighbour, weight)

	def initialize(self):
		minnodeid = min(self.edges, key=self.edges.get)
		edge = self.edges[minnodeid]

		edge.state = branch
		self.level = 0
		self.state = found
		self.rec = 0
		if(debug):
			print('PUSH', self.nodeid, edge.v.nodeid, 'Connect', self.level, self.nodeid)
		edge.v.queue.put((connect, 0, self.nodeid))

	def process_connect(self, level, nodeid):
		if(self.state == sleep):
			self.initialize()
		edge = self.edges[nodeid]
		if(level < self.level):
			edge.state = branch
			if(debug):
				print('PUSH', self.nodeid, edge.v.nodeid, 'Initiate', self.level, self.name, self.state, self.nodeid)
			edge.v.queue.put((initiate, self.level,self.name, self.state, self.nodeid))
		elif edge.state == basic:
			# Wait. How to do it?
			if(debug):
				print('PUSH', self.nodeid, self.nodeid, 'Connect', level, nodeid)
			self.queue.put((connect, level, nodeid))

		else:
			if(debug):
				print('PUSH', self.nodeid, edge.v.nodeid, 'Initiate', self.level+1, edge.weight, self.state, self.nodeid)
			edge.v.queue.put((initiate, self.level+1, edge.weight, find, self.nodeid))

	def process_initiate(self, level, name, state, nodeid):
		if(self.state == sleep):
			self.initialize()
		self.level = level
		self.name = name
		self.state = state

		self.parent = nodeid
		self.bestNode = None
		self.bestWt = math.inf
		self.testNode = None

		for key in self.edges:
			edge = self.edges[key]
			if (edge.state == branch) and (key != nodeid):
				if(debug):
					print('PUSH', self.nodeid, edge.v.nodeid, 'Initiate', level, name, state, self.nodeid)
				edge.v.queue.put((initiate, level, name, state, self.nodeid))

		if self.state == find:
			self.rec = 0
			self.find_min()

	def find_min(self):
		minnodeid = min(self.edges, key=self.edges.get)
		minedge = self.edges[minnodeid]


		minedge = None

		for key in self.edges:
			edge = self.edges[key]
			if(edge.state != basic):
				continue
			if(minedge == None):
				minedge = edge
			elif(minedge.weight > edge.weight):
				minedge = edge


		if(minedge != None):
			self.testNode = minedge.v.nodeid
			if(debug):
				print('PUSH', self.nodeid, minedge.v.nodeid, 'Test', self.level, self.name, self.nodeid)
			minedge.v.queue.put((test, self.level, self.name, self.nodeid))
		else:
			self.testNode = None
			self.report()

	def process_test(self, level, name, nodeid):
		if(self.state == sleep):
			self.initialize()
		edge = self.edges[nodeid]
		if(level > self.level):
			if(debug):
				# print("Level: ", self.level)
				print('PUSH', self.nodeid, self.nodeid, 'Test', level, name,nodeid)
			self.queue.put((test, level, name, nodeid))

		elif(self.name == name):
			if edge.state == basic:
				edge.state = reject

			if nodeid != self.testNode:
				if(debug):
					print('PUSH', self.nodeid, edge.v.nodeid, 'Reject', self.nodeid)
				edge.v.queue.put((reject, self.nodeid))
			else:
				self.find_min()

		else:
			if(debug):
				print('PUSH', self.nodeid, edge.v.nodeid, 'Accept', self.nodeid)
			edge.v.queue.put((accept, self.nodeid))

	def process_accept(self, nodeid):
		if(self.state == sleep):
			self.initialize()
		self.testNode = None
		edge = self.edges[nodeid]
		if edge.weight < self.bestWt:
			self.bestWt = edge.weight
			self.bestNode = nodeid

		self.report()

	def process_reject(self, nodeid):
		if(self.state == sleep):
			self.initialize()
		edge = self.edges[nodeid]
		if edge.state == basic:
			edge.state = reject

		self.find_min()

	def report(self):
		if self.testNode != None:
			return

		qs = 0
		for key in self.edges:
			edge = self.edges[key]
			if(edge.state == branch and key!= self.parent):
				qs += 1

		if(self.rec == qs and self.testNode == None):
			self.state = found
			if(debug):
				print('PUSH', self.nodeid, self.edges[self.parent].v.nodeid, 'Report', self.bestWt, self.nodeid)
			self.edges[self.parent].v.queue.put((report, self.bestWt, self.nodeid))


		# for key in self.edges:
		# 	edge = self.edges[key]
		# 	if edge.state == branch and edge.v.nodeid != self.parent and edge.v.nodeid == self.rec:
		# 		self.state = found
		# 		if(debug):
		# 			print('PUSH', self.nodeid, self.edges[self.parent].v.nodeid, 'Report', self.bestWt, self.nodeid)
		# 		self.edges[self.parent].v.queue.put((report, self.bestWt, self.nodeid))


	def process_report(self, wt, nodeid):
		if(self.state == sleep):
			self.initialize()
		global stop
		if nodeid != self.parent:
			if(wt < self.bestWt):
				self.bestWt = wt
				self.bestNode = nodeid

			self.rec = self.rec + 1
			self.report()

		else:
			if self.state == find:
				if(debug):
					print('PUSH', self.nodeid, self.nodeid, 'Report', wt,nodeid)
				self.queue.put((report, wt, nodeid))
			elif wt > self.bestWt:
				self.change_root()
			elif wt == math.inf and self.bestWt	 == math.inf:
				print("STOP", self.nodeid)
				# sys.exit()
				stop = 1
				self.done = True

	def change_root(self):
		edge = self.edges[self.bestNode]
		if edge.state == branch:
			if(debug):
				print('PUSH', self.nodeid, edge.v.nodeid, 'Changeroot', self.nodeid)
			edge.v.queue.put((changeroot, self.nodeid))
		else:
			edge.state = branch
			if(debug):
				print('PUSH', self.nodeid, edge.v.nodeid, 'Connect', self.level, self.nodeid)
			edge.v.queue.put((connect, self.level, self.nodeid))


	def process_changeroot(self, nodeid):
		if(self.state == sleep):
			self.initialize()
		self.change_root()

	def parse_message(self):
		while(not self.stop):
			msg = self.queue.get()
			if(msg[0] == awake):
				self.initialize()
			elif(msg[0] == connect):
				level, nodeid = msg[1], msg[2]
				self.process_connect(level, nodeid)
			elif(msg[0] == initiate):
				level, name, state, nodeid = msg[1], msg[2], msg[3], msg[4]
				self.process_initiate(level, name, state, nodeid)
			elif(msg[0] == test):
				level, name, nodeid = msg[1], msg[2], msg[3]
				self.process_test(level, name, nodeid)
			elif(msg[0] == accept):
				nodeid = msg[1]
				self.process_accept(nodeid)
			elif(msg[0] == reject):
				nodeid = msg[1]
				self.process_reject(nodeid)
			elif(msg[0] == report):
				wt, nodeid = msg[1], msg[2]
				self.process_report(wt, nodeid)
			elif(msg[0] == changeroot):
				nodeid = msg[1]
				self.process_changeroot(nodeid)

	def parse_message_seq(self):
		if(self.queue.qsize() == 0):
			return
		msg = self.queue.get()
		if(msg[0] == awake):
			self.initialize()
		elif(msg[0] == connect):
			level, nodeid = msg[1], msg[2]
			self.process_connect(level, nodeid)
		elif(msg[0] == initiate):
			level, name, state, nodeid = msg[1], msg[2], msg[3], msg[4]
			self.process_initiate(level, name, state, nodeid)
		elif(msg[0] == test):
			level, name, nodeid = msg[1], msg[2], msg[3]
			self.process_test(level, name, nodeid)
		elif(msg[0] == accept):
			nodeid = msg[1]
			self.process_accept(nodeid)
		elif(msg[0] == reject):
			nodeid = msg[1]
			self.process_reject(nodeid)
		elif(msg[0] == report):
			wt, nodeid = msg[1], msg[2]
			self.process_report(wt, nodeid)
		elif(msg[0] == changeroot):
			nodeid = msg[1]
			self.process_changeroot(nodeid)

def read_file(filename):
	with open(filename, 'r') as f:
		inputs = f.readlines()

	inputs = [x.split() for x in inputs]
	num_node = int(inputs[0][0])
	output = []
	for x in inputs[1:]:
		output.append([int(x[0][1:-1]), int(x[1][:-1]), int(x[2][:-1])])

	return num_node, output


if __name__ == "__main__":
	filename = sys.argv[1]
	num_node, edges = read_file(filename)
	nodes = [Node(i, i) for i in range(num_node)]
	for x in edges:
		nodes[x[0]].add_edge(nodes[x[1]], x[2])
		nodes[x[1]].add_edge(nodes[x[0]], x[2])

	for node in nodes:
		print(node)


	# for node in nodes:
	nodes[0].queue.put((awake,))
	done = True
	while(stop == 0):
		for node in nodes:
			node.parse_message_seq()
		# input()

	output = set()
	for node in nodes:
		for key in node.edges:
			edge = node.edges[key]
			if(edge.state == branch):

				output.add((min(node.nodeid, edge.v.nodeid), max(node.nodeid, edge.v.nodeid), edge.weight))

	output = list(output)
	output=sorted(output, key=itemgetter(2))
	for edge in output:
		print(edge)
	