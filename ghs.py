from queue import Queue
import math 

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

class Edge:
	def __init__(self, v, weight):
		self.v = v
		self.weight = weight
		self.state = basic

	def __eq__(self, other):
		return self == other

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

	def add_edge(self, neighbour, weight):
		self.edges[neighbour.nodeid] = Edge(neighbour, weight)

	def initialize(self):
		minnodeid = min(self.edges, key=self.edges.get)
		edge = self.edges[minnodeid]

		edge.state = branch
		self.level = 0
		self.state = found
		self.rec = 0

		edge.v.queue.put((connect, self.level, self.nodeid))

	def process_connect(self, level, nodeid):
		edge = self.edges[nodeid]
		if(level < self.level):
			edge.state = branch
			edge.v.queue.put((initiate, self.level,self.name, self.state, self.nodeid))
		elif edge.nodeid == basic:
			# Wait. How to do it?
			self.queue.put((connect, level, nodeid))

		else:
			edge.v.queue.put((initiate, self.level+1, edge.weight, find, self.nodeid))

	def process_initiate(self, level, name, state, nodeid):
		self.level = level
		self.name = name
		self.state = state

		self.parent = nodeid
		self.bestNode = None
		self.bestWt = Edge(None, math.inf)
		self.testNode = None

		for key in self.edges:
			edge = self.edges[key]
			if (edge.state == branch) and (key != nodeid):
				edge.v.queue.put((initiate, level, name, state, self.nodeid))

		if self.state == find:
			self.rec = 0
			self.find_min()

	def find_min():
		minnodeid = min(self.edges, key=self.edges.get)
		minedge = self.edges[minnodeid]

		if(minedge.state == basic):
			self.testNode = minnodeid
			edge.v.queue.put((test, self.level, self.name, self.nodeid))
		else:
			self.testNode = None
			self.report()

	def process_test(self, level, name, nodeid):
		edge = self.edges[nodeid]
		if(level > self.level):
			self.queue.put((test, level, name, nodeid))

		elif(self.name == name):
			if edge.status == basic:
				edge.status = reject

			if nodeid != self.testNode:
				edge.v.queue.put((reject, self.nodeid))
			else:
				self.find_min()

		else:
			edge.v.queue.put((accept, self.nodeid))

	def process_accept(self, nodeid):
		self.testNode = None
		edge = self.edges[nodeid]
		if edge < self.bestWt:
			self.bestWt = edge
			self.bestNode = nodeid

		self.report()

	def process_reject(self, nodeid):
		edge = self.edges[nodeid]
		if edge.state == basic:
			edge.state = reject

		self.find_min()

	def report(self):
		if self.testNode != None:
			return

		for key in self.edges:
			edge = self.edges[key]
			if edge.state == branch and edge.v.nodeid != self.parent and edge.v.nodeid == self.rec:
				self.state = found
				self.edges[parent].v.queue.put((report, self.bestWt, self.nodeid))


	def process_report(self, wt, nodeid):
		if nodeid != self.parent:
			if(wt < self.bestWt):
				self.bestWt = wt
				self.bestNode = nodeid

			self.rec = self.rec + 1
			self.report()

		else:
			if self.state == find:
				self.queue.put((report, wt, nodeid))
			elif wt > self.bestWt:
				self.change_root()
			elif wt == math.inf and self.bestWt == math.inf:
				self.stop = 1

	def change_root():
		edge = self.edges[self.bestNode]
		if edge.state == branch:
			edge.v.queue.put((changeroot, self.nodeid))
		else:
			edge.state = branch
			edge.v.queue.put((connect, self.level, self.nodeid))


	def process_changeroot(self, nodeid):
		self.changeroot()

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
				self.process_test(level, name)
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




if __name__ == "__main__":
	filename = sys.argv[1]


	