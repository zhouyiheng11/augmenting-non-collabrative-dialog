import pandas as pd
import json
from sklearn.cluster import KMeans
from joblib import dump, load
import csv

all_persuasion_strategies = {'0:greeting': 0, '1:greeting': 1, '0:other': 2, '0:task-related-inquiry': 3, '1:positive-to-inquiry': 4, '1:task-related-inquiry': 5, '0:acknowledgement': 6, '0:neutral-to-inquiry': 7, '1:acknowledgement': 8, '1:positive-reaction-to-donation': 9, '1:agree-donation': 10, '0:credibility-appeal': 11, '0:proposition-of-donation': 12, '0:ask-donate-more': 13, '0:confirm-donation': 14, '0:logical-appeal': 15, '0:thank': 16, '1:provide-donation-amount': 17, '1:negative-to-inquiry': 18, '1:thank': 19, '0:personal-related-inquiry': 20, '1:neutral-reaction-to-donation': 21, '0:source-related-inquiry': 22, '0:donation-information': 23, '1:ask-donation-procedure': 24, '0:foot-in-the-door': 25, '0:you-are-welcome': 26, '1:disagree-donation': 27, '1:ask-org-info': 28, '1:other': 29, '0:positive-to-inquiry': 30, '1:negative-reaction-to-donation': 31, '1:off-task': 32, '0:emotion-appeal': 33, '0:self-modeling': 34, '1:personal-related-inquiry': 35, '0:ask-donation-amount': 36, '0:closing': 37, '1:closing': 38, '0:praise-user': 39, '1:ask-persuader-donation-intention': 40, '0:off-task': 41, '1:neutral-to-inquiry': 42, '0:negative-to-inquiry': 43, '0:ask-not-donate-reason': 44, '0:comment-partner': 45, '0:personal-story': 46, '1:you-are-welcome': 47, '1:confirm-donation': 48, '1:disagree-donation-more': 49}


def read_full_data(path="/projects/tir1/users/yihengz1/negotiation_robot/Data/persuasion/full_dialog.csv"):
	with open(path, newline='') as csvfile:
		dialog_reader = csv.reader(csvfile, delimiter=',')
		dials = {}

		for row in dialog_reader:
			if row[-1] not in dials:
				dials[row[-1]] = {}
			if row[-3] not in dials[row[-1]]:
				dials[row[-1]][row[-3]] = []
			dials[row[-1]][row[-3]].append(row[1])

	return dials

def read_only_dialog_acts(path="/projects/tir1/users/yihengz1/negotiation_robot/Data/persuasion/300_dialog.xlsx"):
	df = pd.read_excel(path)
	dials = {}
	for row in df.iterrows():
		row = row[1]
		
		#create instance
		if row.B2 not in dials:
			dials[row.B2] = {}

		if row.Turn not in dials[row.B2]:
			dials[row.B2][row.Turn] = {}
			dials[row.B2][row.Turn]["ee"] = []
			dials[row.B2][row.Turn]["er"] = []

		if row.B4 == 0:
			dials[row.B2][row.Turn]["er"].append(str(row.B4) + ":" + row.er_label_1)
		else:
			dials[row.B2][row.Turn]["ee"].append(str(row.B4) + ":" +row.ee_label_1)

	#sort dialog acts
	for dial in dials:
		dial = dials[dial]
		for i in range(len(dial)):
			dial[i]["er"] = list(set(dial[i]["er"]))
			dial[i]["ee"] = list(set(dial[i]["ee"]))
			dial[i]["er"].sort()
			dial[i]["ee"].sort()

	return dials


def read_text_and_dialog_acts(path="/projects/tir1/users/yihengz1/negotiation_robot/Data/persuasion/300_dialog.xlsx"):
	df = pd.read_excel(path)
	dials = {}
	for row in df.iterrows():
		row = row[1]
		
		#create instance
		if row.B2 not in dials:
			dials[row.B2] = {}

		if row.Turn not in dials[row.B2]:
			dials[row.B2][row.Turn] = {}
			dials[row.B2][row.Turn]["dialog_act"] = {}
			dials[row.B2][row.Turn]["text"] = {}
			dials[row.B2][row.Turn]["dialog_act"]["ee"] = []
			dials[row.B2][row.Turn]["dialog_act"]["er"] = []
			dials[row.B2][row.Turn]["text"]["er"] = []
			dials[row.B2][row.Turn]["text"]["ee"] = []
			dials[row.B2][row.Turn]["pos"] = {}
			dials[row.B2][row.Turn]["neu"] = {}
			dials[row.B2][row.Turn]["neg"] = {}

		if row.B4 == 0:
			dials[row.B2][row.Turn]["dialog_act"]["er"].append(str(row.B4) + ":" + row.er_label_1)
			dials[row.B2][row.Turn]["text"]["er"].append(row.Unit)
			dials[row.B2][row.Turn]["pos"]["er"] = row.pos
			dials[row.B2][row.Turn]["neu"]["er"] = row.neu
			dials[row.B2][row.Turn]["neg"]["er"] = row.neg
		else:
			dials[row.B2][row.Turn]["dialog_act"]["ee"].append(str(row.B4) + ":" + row.ee_label_1)
			dials[row.B2][row.Turn]["text"]["ee"].append(row.Unit)
			dials[row.B2][row.Turn]["pos"]["ee"] = row.pos
			dials[row.B2][row.Turn]["neu"]["ee"] = row.neu
			dials[row.B2][row.Turn]["neg"]["ee"] = row.neg

	return dials

def extract_seq_for_fst(dials, uuids):
	ret = ""

	for dial in uuids:
		dial = dials[dial]
		for turn in dial:
			turn = dial[turn]
			er_acts = turn["er"]
			ee_acts = turn["ee"]
			er_acts = list(set(er_acts))
			ee_acts = list(set(ee_acts))
			er_acts.sort()
			ee_acts.sort()

			ret += "_".join(er_acts) + " " + "_".join(ee_acts) + " "
		ret += "\n"
	return ret

def extract_seq_for_fst_cluster(dials, uuids, kmeans=None):
	ret = ""
	X = []

	if kmeans is None:
		for dial in uuids:
			dial = dials[dial]
			for turn in dial:
				turn = dial[turn]
				er_acts = turn["er"]
				ee_acts = turn["ee"]

				na_target = [0] * len(all_persuasion_strategies)
				for per_strat in er_acts:
					na_target[all_persuasion_strategies[per_strat]] = 1
				X.append(na_target)

				na_target = [0] * len(all_persuasion_strategies)
				for per_strat in ee_acts:
					na_target[all_persuasion_strategies[per_strat]] = 1
				X.append(na_target)

		kmeans = KMeans(n_clusters=100, random_state=0).fit(X)
		dump(kmeans, 'persuasion.joblib')
	
	else:
		for dial in uuids:
			dial = dials[dial]
			for turn in dial:
				turn = dial[turn]
				er_acts = turn["er"]
				ee_acts = turn["ee"]

				na_target = [0] * len(all_persuasion_strategies)
				for per_strat in er_acts:
					na_target[all_persuasion_strategies[per_strat]] = 1
				ret += "<" + str(kmeans.predict([na_target])[0]) + "> "

				na_target = [0] * len(all_persuasion_strategies)
				for per_strat in ee_acts:
					na_target[all_persuasion_strategies[per_strat]] = 1
				ret += "<" + str(kmeans.predict([na_target])[0]) + "> "
			ret += "\n"

	return ret

# full_dialogs = read_full_data()
# with open("full_dialog.json", "w") as output:
# 	json.dump(full_dialogs, output)

# uuids = json.load(open("/projects/tir1/users/yihengz1/negotiation_robot/bot/persuasion_uuids"))
# uuids_train = uuids[:180]
# dials = read_only_dialog_acts()
# kmeans = load('persuasion.joblib')
# print (extract_seq_for_fst_cluster(dials, uuids, kmeans))
# # print (extract_seq_for_fst(dials, uuids_train))
# # print (dials)