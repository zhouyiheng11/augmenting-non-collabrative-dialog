import json
from sklearn.cluster import KMeans
from collections import Counter
from nltk.cluster.kmeans import KMeansClusterer
import sys
sys.path.insert(0, "../bot")
from match_coef_and_ns import *
import numpy as np
np.random.seed(0)
weights = construct_weight_vector()
recommendation_feature_mapping = ["seller_neg_sentiment", 	"seller_pos_sentiment", 	"buyer_neg_sentiment", 	"buyer_pos_sentiment", 	"first_person_plural_count_seller", 	"first_person_singular_count_seller", 	"first_person_plural_count_buyer", 	"first_person_singular_count_buyer", 	"third_person_singular_seller", 	"third_person_plural_seller", 	"third_person_singular_buyer", 	"third_person_plural_buyer", 	"number_of_diff_dic_pos", 	"number_of_diff_dic_neg", 	"buyer_propose", 	"seller_propose", 	"hedge_count_seller", 	"hedge_count_buyer", 	"assertive_count_seller", 	"assertive_count_buyer", 	"factive_count_seller", 	"factive_count_buyer", 	"who_propose", 	"seller_trade_in", 	"personal_concern_seller", 	"sg_concern", 	"liwc_certainty", 	"liwc_informal", 	"politeness_seller_please", 	"politeness_seller_gratitude", 	"politeness_seller_please_s", 	"ap_des", 	"ap_pata", 	"ap_infer", 	"family", 	"friend", 	"politeness_buyer_please", 	"politeness_buyer_gratitude", 	"politeness_buyer_please_s", 	"politeness_seller_greet", 	"politeness_buyer_greet"] 
recommendation_feature_mapping_re = {"seller_neg_sentiment":0,"seller_pos_sentiment":1,"buyer_neg_sentiment":2,"buyer_pos_sentiment":3,"first_person_plural_count_seller":4,"first_person_singular_count_seller":5,"first_person_plural_count_buyer":6,"first_person_singular_count_buyer":7,"third_person_singular_seller":8,"third_person_plural_seller":9,"third_person_singular_buyer":10,"third_person_plural_buyer":11,"number_of_diff_dic_pos":12,"number_of_diff_dic_neg":13,"buyer_propose":14,"seller_propose":15,"hedge_count_seller":16,"hedge_count_buyer":17,"assertive_count_seller":18,"assertive_count_buyer":19,"factive_count_seller":20,"factive_count_buyer":21,"who_propose":22,"seller_trade_in":23,"personal_concern_seller":24,"sg_concern":25,"liwc_certainty":26,"liwc_informal":27,"politeness_seller_please":28,"politeness_seller_gratitude":29,"politeness_seller_please_s":30,"ap_des":31,"ap_pata":32,"ap_infer":33,"family":34,"friend":35,"politeness_buyer_please":36,"politeness_buyer_gratitude":37,"politeness_buyer_please_s":38,"politeness_seller_greet":39,"politeness_buyer_greet":40}

def parse_fine_acts_with_buyer(path="fine_intents"):
	raw_data = json.load(open(path))
	uuids = json.load(open("../bot/uuids"))
	
	#lower all the ids
	for i in range(len(uuids)):
		uuids[i] = uuids[i].lower()

	seq_train = ""
	seq_dev = ""

	for uuid in raw_data:
		if uuid not in uuids:
			for l in raw_data[uuid]:
				seq_train += " ".join(l) + " "
			seq_train += "\n"
		if uuid in uuids[:300]:
			for l in raw_data[uuid]:
				seq_dev += " ".join(l) + " "
			seq_dev += "\n"

	with open("seq_fine_acts_train", "w") as output:
		output.write(seq_train)
	with open("seq_fine_acts_dev", "w") as output:
		output.write(seq_dev)	

def parse_bag_of_strats(path="bag_of_strategies"):
	raw_data = json.load(open(path))
	uuids = json.load(open("../bot/uuids"))
	counter = Counter()

	#lower all the ids
	for i in range(len(uuids)):
		uuids[i] = uuids[i].lower()

	seq_train = ""
	seq_dev = ""

	for uuid in raw_data:
		if uuid not in uuids:
			for l in raw_data[uuid]:
				seq_train += "<" + "".join([str(i) for i in l]) + "> "
				counter["".join([str(i) for i in l])] += 1
			seq_train += "\n"
		if uuid in uuids[:300]:
			for l in raw_data[uuid]:
				seq_dev += "<" + "".join([str(i) for i in l]) + "> "
				counter["".join([str(i) for i in l])] += 1
			seq_dev += "\n"

	with open("seq_bag_strats_train", "w") as output:
		output.write(seq_train)
	with open("seq_bag_strats_dev", "w") as output:
		output.write(seq_dev)	

	print (len(counter))
	print (counter.most_common(100))



def parse_bag_of_strats_cluster(num_clusters, filename=None, path="bag_of_strategies"):
	raw_data = json.load(open(path))
	uuids = json.load(open("../bot/uuids"))
	counter = {}
	cluster_info = {}

	#create training data
	kmeans_input = list()

	#lower all the ids
	for i in range(len(uuids)):
		uuids[i] = uuids[i].lower()

	for uuid in raw_data:
		if uuid not in uuids:
			for l in raw_data[uuid]:
				if str(l) not in counter:
					kmeans_input.append(np.multiply(l, weights))
					counter[str(l)] = 1

	#define clusters
	from joblib import dump, load
	if not filename:
		kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(kmeans_input)
		dump(kmeans, 'minkowski_kmeans'+"_"+str(num_clusters)+'.pkg') 
	else:
		kmeans = load(filename) 

	seq_train = ""
	seq_dev = ""

	# for i in range(len(kmeans_input)):
	# 	tmp = ""
	# 	if kmeans.labels_[i] == 10:
	# 		for s_i, s in enumerate(kmeans_input[i]):
	# 			if s > 0:
	# 				tmp += "<"+recommendation_feature_mapping[s_i]+">" + "; "
	# 		print (tmp)
	# 		print ("------------")

	# for i in range(len(kmeans_input)):
	# 	if "<" + str(kmeans.labels_[i]) + ">" not in cluster_info:
	# 		cluster_info["<" + str(kmeans.labels_[i]) + ">"] = []
	# 	tmp_ci = []
	# 	for s_i, s in enumerate(kmeans_input[i]):
	# 		if s > 0:
	# 			tmp_ci.append("<"+recommendation_feature_mapping[s_i]+">")
	# 	cluster_info["<" + str(kmeans.labels_[i]) + ">"].append(tmp_ci)

	# with open("cluster_info", "w") as output:
	# 	json.dump(cluster_info, output)
	# exit()
	# strategies_set = "seller_propose"
	# strategies_set_2 = "politeness_seller_greet"
	# set_1 = [0]*len(recommendation_feature_mapping)
	# set_2 = [0]*len(recommendation_feature_mapping)
	# for s in strategies_set.split(","):
	# 	set_1[recommendation_feature_mapping_re[s]] = 1
	# for s in strategies_set_2.split(","):
	# 	set_2[recommendation_feature_mapping_re[s]] = 1
	
	# print (kmeans.predict([set_1])[0])
	# print (kmeans.predict([set_2])[0])
	# print (np.linalg.norm(np.multiply(set_1, weights) - np.multiply(set_2, weights)))
	# exit()

	for uuid in raw_data:
		if uuid not in uuids:
			for l in raw_data[uuid]:
				seq_train += "<" + str(kmeans.predict([l])[0]) + "> "
			seq_train += "\n"
		if uuid in uuids[:300]:
			for l in raw_data[uuid]:
				seq_dev += "<" + str(kmeans.predict([l])[0]) + "> "
			seq_dev += "\n"

	with open("wfst_train/minkowski_seq_bag_strats_train_"+str(num_clusters), "w") as output:
		output.write(seq_train)
	with open("wfst_train/minkowski_seq_bag_strats_dev_"+str(num_clusters), "w") as output:
		output.write(seq_dev)

	#reload data
	ret_raw = dict()
	for uuid in raw_data:
		ret_raw[uuid] = list()
		for l in raw_data[uuid]:
			ret_raw[uuid].append("<" + str(kmeans.predict([l])[0]) + ">")

	with open("minkowski_bag_of_strategies_"+str(num_clusters), "w") as output:
		json.dump(ret_raw, output)



#parse_bag_of_strats()

print (parse_bag_of_strats_cluster(300, "minkowski_kmeans_300.pkg"))