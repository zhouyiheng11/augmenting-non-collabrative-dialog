import graphviz as gv
from wfst_visualization import rank_and_clean_up

def construct_and_save_graph(path="/projects/tir1/users/yihengz1/negotiation_robot/finite_state_machine/wfst_train/intents_1.wfst"):
	new_graph = gv.Digraph(path.split("/")[-1])
	top = 3
	#add edges
	raw_data = rank_and_clean_up(path).split("\n")
	current_ide = ""
	counter = 0
	for row in raw_data:
		if not row:
			continue
		#if we have a new state
		if row[0] == "(":
			current_ide = row.split()[0][2:]
			continue
		elif row[0] == ")":
			counter = 0
			continue
		else:
			if float(row.split()[-1][:-1]) > 0.0 and counter < top:
				new_graph.edge(current_ide, row.split()[1],label=row.split()[0][1:].replace('"', ""))
				counter += 1

	new_graph.render()

construct_and_save_graph("wfst_train/persuasion/intents_wfst_persuasion")