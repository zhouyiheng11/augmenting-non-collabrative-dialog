import sys
sys.path.insert(0, "../cocoa/craigslistbargain/")
from parse_dialogue import *
import json
from collections import Counter
import csv
import io
import re

class State:
	def __init__(self, name, transitions):
		self.name = name
		self.transitions = transitions
		self.visits = 0
		self.transitions_history = Counter()

	def step(self, action, next_state):
		if (action not in self.transitions):
			#print ("<action: " + action + "> is not valid from state: <"+str(self.name)+">")
			return None
		
		ret = None
		for state in self.transitions[action]:
			if state.startswith(next_state):
				ret = state
				next_state = state
				break

		if not ret:
			pass
			#print ("<action: " + action + "> is not valid from state: <"+str(self.name) + "> to state: <" + next_state+">")
		else:
			self.visits += 1
			self.transitions_history[action + "@" + next_state] += 1

		return ret


def parse_each_utterance(path, price_tracker_path):
	price_tracker = PriceTracker(price_tracker_path)
	examples = read_examples(path, 1000000, Scenario)
	templates = Templates()
	prices = Counter()

	seq_dialog_acts = dict()
	for example in examples:
		current_id = example.uuid + "@" + example.ex_id
		kb_info = example.scenario.to_dict()
		utterances = parse_example(example, price_tracker, templates)
		seq_dialog_acts[current_id] = list()

		for k in kb_info["kbs"]:
			if k['personal']["Role"] == "seller":
				listing_price = k['personal']["Target"]
			else:
				budget = k['personal']["Target"]

		if listing_price < budget:
			print ("listing price is smaller than buyer budget, exit.")
			exit()

		for u in utterances:
			tmp_dict = u.lf.to_dict()
			if u.agent == 1:
				if "price" in tmp_dict and tmp_dict["price"] and tmp_dict["intent"] != "agree":
					tmp_price = round(tmp_dict["price"]*1.0/listing_price, 1)
					if tmp_price > 2.0:
						tmp_price = "2.0+"
					seq_dialog_acts[current_id].append("1:" + tmp_dict["intent"])# + "_" + str(tmp_price))
				else:	
					seq_dialog_acts[current_id].append("1:" + tmp_dict["intent"])
			else:
				if "price" in tmp_dict and tmp_dict["price"] and tmp_dict["intent"] != "agree":
					tmp_price = round(tmp_dict["price"]*1.0/listing_price, 1)
					if tmp_price > 2.0:
						tmp_price = "2.0+"
					prices[round(tmp_dict["price"]*1.0/listing_price, 1)] += 1
					seq_dialog_acts[current_id].append("0:" + tmp_dict["intent"])# + "_" + str(tmp_price))
				else:
					seq_dialog_acts[current_id].append("0:" + tmp_dict["intent"])
	with open("seq_of_intents_dev", "w") as output:
		json.dump(seq_dialog_acts, output)


def construct_finite_state_machine(filename="fss_2.csv"):
	csvfile = io.open(filename, newline='')
	csv_reader = csv.reader(csvfile, delimiter=',')
	raw_rows = list()	

	for row in csv_reader:
		raw_rows.append(row)

	actions = raw_rows[0][1:]
	raw_rows = raw_rows[1:]
	states = dict()

	for i in range(len(raw_rows)):
		transitions = dict()
		for t in range(1, len(raw_rows[i])):
			if raw_rows[i][t] != "{}":
				transitions[actions[t-1]] = re.split(",[\s]*",raw_rows[i][t].replace("{","").replace("}",""))
		states[raw_rows[i][0]] = State(raw_rows[i][0], transitions)
	
	return states



def calculate_distribution(filename="seq_of_intents_train"):
	seq_dialog_acts = json.load(open(filename))
	states = construct_finite_state_machine()	
	for key in seq_dialog_acts:
		index = 2
		current_state = "start"

		print "----------------------"
		print seq_dialog_acts[key]
		print key
		while True:
			if not current_state or (index+2) >= len(seq_dialog_acts[key]):
				break
			if index + 1 < len(seq_dialog_acts[key]):
				agent = int(seq_dialog_acts[key][index+1].split(":")[0])
				intent = seq_dialog_acts[key][index+1].split(":")[1]

			if index == 2:
				agent = int(seq_dialog_acts[key][index].split(":")[0])
				intent = seq_dialog_acts[key][index].split(":")[1]
				if agent == 1:	
					current_state = states["start"].step(intent, seq_dialog_acts[key][index+1].split(":")[1])
					index += 1
					if not current_state:
						break
					continue
				else:
					if intent not in states:
						current_state = states[intent + "1"].name
					else:
						current_state = states[intent].name
					intent = seq_dialog_acts[key][index+1].split(":")[1]
					current_state = states[current_state].step(intent, seq_dialog_acts[key][index+2].split(":")[1])
					index += 2
			else:
				current_state = states[current_state].step(intent, seq_dialog_acts[key][index+2].split(":")[1])
				index += 2
	
	return states




if __name__ == '__main__':
	parse_each_utterance(["/projects/tir1/users/yihengz1/negotiation_robot/Data/craigslist-data/dev.json"], "/projects/tir1/users/yihengz1/negotiation_robot/cocoa/craigslistbargain/price_tracker.pkl")
	#states = calculate_distribution()	

	# for s in states:
	# 	print "-------------------------------"
	# 	print "state: " + s
	# 	for key in states[s].transitions_history:
	# 		print s + " --%15s--> %15s  %4d" % (key.split("@")[0], key.split("@")[1], states[s].transitions_history[key])

	# #calculate fsm
	# transitions = open("transition_history").read().split("\n")
	# tmp = Counter()
	
	# for transition in transitions:
	# 	if transition.startswith("----") or transition.startswith("state"):
	# 		continue
	# 	tmp[transition] = int(transition.split()[-1])

	# for s,k in tmp.most_common(1000):
	# 	print s



			
