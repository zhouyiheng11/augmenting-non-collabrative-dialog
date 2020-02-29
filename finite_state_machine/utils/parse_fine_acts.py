import json


def parse_fine_acts(path="fine_intents"):
	raw_data = json.load(open(path))
	acts = dict()
	intents = ['1:counter-price', '1:unknown', '1:vague-price', '1:insist', '1:inquiry', '1:inform', '1:disagree', '1:agree', '1:intro', '1:init-price']

	for i in intents:
		acts[i] = ""

	for key in raw_data:
		for intent in raw_data[key]:
			for element in raw_data[key][intent]:
				if intent not in acts:
					continue
				acts[intent] += " ".join(element) + "\n"
	
	for key in acts:
		print key
		print len(acts[key].split("\n"))
		print "-----"
		with open(key + "_wfst_train", "w") as output:
			output.write(acts[key])

	return acts

parse_fine_acts()

