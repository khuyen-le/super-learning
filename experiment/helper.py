from psychopy import visual, event, core, gui, tools
import os
import glob
import random
import math

def generate_guessing_options(items_list, unique_cluster_labels, cluster_dict, possible_options_idx, N_GUESSES, N_OPTIONS): 
    options_list = []
    random.shuffle(unique_cluster_labels)
    for _ in range(N_GUESSES): 
        option_choices_idx = []
        # try to sample evenly across all clusters
        for cur_cluster in unique_cluster_labels: 
            cur_cluster_possible_options = [i for i in cluster_dict[cur_cluster] if i in possible_options_idx]
            #if there are still remaining items in a particular cluster, then sample one from it
            if cur_cluster_possible_options:  
                option_choices_idx.extend(random.sample(cur_cluster_possible_options, 1))
                #make sure to not sample more than the number of options
                if len(option_choices_idx) == N_OPTIONS: 
                    break
        possible_options_idx = [i for i in possible_options_idx if i not in option_choices_idx]
        n_remaining_options = N_OPTIONS - len(option_choices_idx)
        print(n_remaining_options)
        #fill out the rest of the options number
        if(n_remaining_options > 0): 
            print('needed to sample more...')
            option_choices_idx.extend(random.sample(possible_options_idx, n_remaining_options))

        print("options for question " + str(_))
        print(option_choices_idx)
        #options is an array of dicts
        options = list(map(lambda x: {'text': items_list[x]['text'], 'selected': False}, option_choices_idx))
        options_list.append(options)
        #shorten possible option indices
        possible_options_idx = [i for i in possible_options_idx if i not in option_choices_idx]
    return options_list 

def generate_guessing_game(items_list, cluster, version, N_GUESSES, N_OPTIONS):
    unique_cluster_labels = list(range(0, max(cluster.labels_) + 1))
    print(unique_cluster_labels)

    print(type(unique_cluster_labels))
    # create a dictionary with key = each cluster_label, value = corresponding item idx
    cluster_dict = {}
    for cluster_label in unique_cluster_labels: 
        cluster_dict[cluster_label] = [idx for idx, c in enumerate(cluster.labels_) if c == cluster_label]

    starting_cluster_label = random.choice(unique_cluster_labels)
    starting_cluster_item_idx = cluster_dict[starting_cluster_label]
    while len(starting_cluster_item_idx) < 5: # need starting cluster to have at least 5 things in there.
        #choose a random cluster from all the clusters
        starting_cluster_label = random.choice(unique_cluster_labels)
        starting_cluster_item_idx = cluster_dict[starting_cluster_label]
    print(starting_cluster_label)
    print("items of starting cluster:")
    print(starting_cluster_item_idx)

    hints = []
    options_list = []

    if (version == "near"): 
        #choose the hints from the starting_cluster
        hints_idx = random.sample(starting_cluster_item_idx, N_GUESSES)
        print("the hints:")
        print(hints_idx)
        #hints is just an array of the text (animal names)
        hints = [w['text'] for i, w in enumerate(items_list) if i in hints_idx]
        #now limit the options to the animals that are not part of the hints
        possible_options_idx = [i for i in range(0, len(items_list)) if i not in hints_idx]
        print("possible options after hints:")
        print(possible_options_idx)
        options_list = generate_guessing_options(items_list, unique_cluster_labels, cluster_dict, possible_options_idx, N_GUESSES, N_OPTIONS)

    elif (version == "far"):
        print(cluster_dict)
        #first hint is from the starting cluster
        hints_idx = random.sample(starting_cluster_item_idx, 1)
        print('got the first hint from the starting cluster')
        print(hints_idx)
        #sample from all the cluster, making sure that each cluster gets at least one hint
        #first make sure that the non-starting clusters get at least one hint each
        for cur_cluster_label in unique_cluster_labels: 
            if cur_cluster_label == starting_cluster_label: 
                print("this is the starting cluster " + str(cur_cluster_label) + ", skipping...")
            else: 
                print('sampling from cluster ' + str(cur_cluster_label))
                cur_cluster_idx = cluster_dict[cur_cluster_label]
                hints_idx.extend(random.sample(cur_cluster_idx, 1))
                print(hints_idx)
        #present the sparsely-sampled hints in order, then fill out the remaining number of hints with randomly selected hints
        possible_hints_idx = [i for i in range(0, len(items_list)) if i not in hints_idx]
        hints_idx.extend(random.sample(possible_hints_idx, N_GUESSES - len(hints_idx)))
        print("the hints:")
        print(hints_idx)
        #hints is just an array of the text (animal names)
        hints = [w['text'] for i, w in enumerate(items_list) if i in hints_idx]
        print(hints)
        #now limit the options to the animals that are not part of the hints
        possible_options_idx = [i for i in range(0, len(items_list)) if i not in hints_idx]
        print("possible options after hints:")
        print(possible_options_idx)
        options_list = generate_guessing_options(items_list, unique_cluster_labels, cluster_dict, possible_options_idx, N_GUESSES, N_OPTIONS)
    return hints, options_list

def random_point_in_circle(radius, center): 
    #I got this idea from Claude.AI, before this I was just generating random x and y and checking whether it's inside the boundary of the circle or not
    #First generate a random angle
    angle = random.uniform(0, 360)
    #Then generate a random r, slightly smaller than circle radius to ensure text fits
    r = random.uniform(0, radius * 0.95)
    item_x, item_y = tools.coordinatetools.pol2cart(angle, r, units='deg') 
    item_x += center[0]
    item_y += center[1]
    return item_x, item_y

def get_runtime_variables(runtime_vars, order, exp_title='Stroop'):
    while True: 
        dlg = gui.DlgFromDict(runtime_vars, order=order, title=exp_title)
        if dlg.OK: 
            #if subject code has already been used, then loop back to input box
            file_name = "trials/" + runtime_vars['subj_code'] + "_trials.csv"
            if os.path.isfile(file_name): 
                errorDlg = gui.Dlg(title="Error")
                errorDlg.addText(f"Error: {runtime_vars['subj_code']} already in use.", color = 'Red')
                errorDlg.show()
            else: 
                return runtime_vars
        else: 
            print('User Cancelled')
            break

#read in trials
def import_trials(trial_filename, col_names=None, separator=','):
    trial_file = open(trial_filename, 'r')
    if col_names is None:
        # Assume the first row contains the column names
        col_names = trial_file.readline().rstrip().split(separator)
    trials_list = []
    #loop through each line in trial_file
    for cur_trial in trial_file:
        cur_trial = cur_trial.rstrip().split(separator)
        assert len(cur_trial) == len(col_names) # make sure the number of column names = number of columns
        #create a dict of pairwise values in col_names and cur_trial
        trial_dict = dict(zip(col_names, cur_trial))
        trials_list.append(trial_dict)
    return trials_list

#open data file
def create_data_file(subj_code, separator=','): 
    # create a data folder if it doesn't already exist
    try:
        os.mkdir('data')
    except FileExistsError:
        print('Data directory exists; proceeding to open file')

    #open file to write data to and store a header
    data_file = open(f"data/{subj_code}_data.csv",'w')
    header = separator.join(["subj_code", "seed", "word", 'color', 'trial_type', 'orientation',
                             "trial_num", "response", "is_correct", "rt"])
    data_file.write(header+'\n')
    return data_file

def write_to_file(fileHandle, trial, response, separator=',', sync=False, add_newline=True): 
    #get information of current trial
    trial_info = [trial[_] for _ in trial]
    #add response information
    trial_info.extend(response)
    #stringify
    trial_response = map(str, trial_info)
    line = separator.join([str(i) for i in trial_response])
    print(line)
    if add_newline: 
        line += '\n'
    try:
        fileHandle.write(line)
    except:
        print('file is not open for writing')
    if sync: #set sync=False to NOT close the file after writing each line.
        fileHandle.flush()
        os.fsync(fileHandle)
