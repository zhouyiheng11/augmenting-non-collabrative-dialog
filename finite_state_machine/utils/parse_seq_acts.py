import json

def parse(path):
	raw_data = json.load(open(path))
	result = ""
	for key in raw_data:
		result += " ".join(raw_data[key][1:]) + "\n"
	with open("intents.dev", "w") as output:
		output.write(result)


parse("/projects/tir1/users/yihengz1/negotiation_robot/finite_state_machine/seq_of_intents_dev")