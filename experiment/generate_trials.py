import random
import os
import math
from helper import random_point_in_circle

def generate_trials(subj_code,seed,version,boundary,items_list):
	separator=","
	
	#set seed
	#why? in case we want to generate the same trials again
	random.seed(int(seed))
	
	#open trial file and write header
	trial_file = open(os.path.join(os.getcwd(),'trials',subj_code+'_trials.csv'),'w')
	header = separator.join(["subj_code","seed","version", 'phase','item','init_x', 'init_y'])
	trial_file.write(header+'\n')
	
	#create trials
	trials = []
	item_positions = []
	for item in items_list:
		init_x, init_y = random_point_in_circle(boundary.radius, boundary.pos)
		existing_check_idx = 0
		while existing_check_idx < len(item_positions):
			print("checking location of item " + item['text'])
			existing_x, existing_y = item_positions[existing_check_idx]
			print(existing_x, existing_y)
			if math.sqrt((init_x - existing_x)**2 + (init_y - existing_y)**2) < 50: #actual number was trial and error
				print("too close, regenerating...")
				#regenerate item_x and y
				init_x, init_y = random_point_in_circle(boundary.radius, boundary.pos)
				#reset check idx
				existing_check_idx = 0 
			else: 
				#go to the next existing position
				existing_check_idx += 1
		# once we get here, item_x and y have been checked against all the existing positions
		item_positions.append((init_x, init_y))
		trials.append([subj_code,seed,version,"sort",item['text'],init_x,init_y])

	#print(trials)
	random.shuffle(trials)
	
	for cur_trial in trials:
		#print(cur_trial)
		trial_file.write(separator.join(map(str,cur_trial))+'\n')
	
	trial_file.close()
	return True