# Author: Yiheng Zhou

'''
Class for tracking current states for FST
'''
class wfst:
	def __init__(self, filename="/projects/tir1/users/yihengz1/negotiation_robot/finite_state_machine/wfst_train/wfst_output/intents_0.5.wfst"):
		self.state_embedding = dict()
		self.current_state = 0
		self.transitions = dict()

		#initialize wfst
		print ("Initializing WFST...")
		current = -1
		for line in open(filename).read().split("\n"):
			line_split = line.split()
			if line.startswith("(("):
				current = line_split[0][2:]
				self.state_embedding[int(current)] = list()
				self.transitions[int(current)] = dict()
			elif line.startswith(")"):
				continue
			else:
				self.state_embedding[int(current)].append(float(line_split[-1][:-1]))
				self.transitions[int(current)][line_split[0][1:]] = int(line_split[-2])
		print ("Loaded "+ str(len(self.transitions))+ " states.")
		print ("Initialization complete.")

	#look up embedding of a state
	def look_up_state_embedding(self, state_index):
		if state_index not in self.state_embedding:
			print ("state:" + str(state_index) + " does not exist.")
			exit(0)
		return self.state_embedding[state_index]

	#step function returns the next state given action
	def step(self, action):
		next_state = self.transitions[self.current_state][action]
		self.current_state = next_state
		return next_state

# #testing
# fsm = wfst()
# print (fsm.current_state)
# fsm.step("1:counter-price")
# print (fsm.current_state)
# print (fsm.look_up_state_embedding(fsm.current_state))
