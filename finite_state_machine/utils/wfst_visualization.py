

def rank_and_clean_up(path="wfst_train/wfst_fine_output/init.wfst"):
	raw_data = open(path).read().split("\n")
	out = ""
	states = list()
	states_value = list()

	for row in raw_data:
		if row[0] == "(":
			out += row + "\n"
		elif row[0] == ")":
			states = [x for _,x in sorted(zip(states_value,states), reverse=True)]
			out += "\n".join(states) + "\n"
			out += row + "\n"
			states = list()
			states_value = list()
		else:
			if row.split()[0][1:] != row.split()[1]:
				print ("mismatched!")
				print (row)
				exit()
			states.append("  (" + " ".join(row.split()[1:]))
			states_value.append(float(row.split()[-1][:-1]))
	#print out
	return out


print (rank_and_clean_up())