import random
import os
import math

def pluralize(animal_name): 
    if animal_name == 'mouse': 
        return 'mice'
    elif animal_name == 'fly': 
        return 'flies'
    elif animal_name == 'butterfly': 
        return 'butterflies'
    elif animal_name in ['octopus', 'ostrich']: 
        return animal_name + 'es'
    elif animal_name in ['sheep', 'goldfish', 'jellyfish', 'starfish']:
        return animal_name 
    else: 
        return animal_name + 's'
    
def generate_guessing_options(items_list, unique_cluster_labels, cluster_dict, cluster, possible_options_idx, N_GUESSES, N_OPTIONS): 
    options_list = []
    options_cluster_list = []
    for _ in range(N_GUESSES): 
        random.shuffle(unique_cluster_labels)
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
        #fill out the rest of the options number
        if(n_remaining_options > 0): 
            random_options_add = random.sample(possible_options_idx, n_remaining_options)
            option_choices_idx.extend(random_options_add)

        random.shuffle(option_choices_idx)
        #options is a string, will be read in by import_trials
        options = '/'.join([items_list[i]['text'] for i in option_choices_idx])
        options_list.append(options)
        options_cluster = '/'.join([str(cluster.labels_[i]) for i in option_choices_idx])
        options_cluster_list.append(options_cluster)

        #shorten possible option indices for next round of guessing
        possible_options_idx = [i for i in possible_options_idx if i not in option_choices_idx]

    return options_list, options_cluster_list

def generate_guessing_game(items_list, cluster, version, N_GUESSES, N_OPTIONS):
    unique_cluster_labels = list(range(0, max(cluster.labels_) + 1))
    random.shuffle(unique_cluster_labels)
    # create a dictionary with key = each cluster_label, value = corresponding item idx
    cluster_dict = {}
    for cluster_label in unique_cluster_labels: 
        cluster_dict[cluster_label] = [idx for idx, c in enumerate(cluster.labels_) if c == cluster_label]

    starting_cluster_label = random.choice(unique_cluster_labels)
    starting_cluster_item_idx = cluster_dict[starting_cluster_label]
    while len(starting_cluster_item_idx) < N_GUESSES + 1: # need starting cluster to have at least 6 things in there, to have at least 1 question have the starting cluster...
        #choose a random cluster from all the clusters
        starting_cluster_label = random.choice(unique_cluster_labels)
        starting_cluster_item_idx = cluster_dict[starting_cluster_label]

    hints = []
    hints_cluster = []
    options_list = []
    options_cluster_list = []

    if (version == "near"): 
        #choose the hints from the starting_cluster
        hints_idx = random.sample(starting_cluster_item_idx, N_GUESSES)
        #hints is just an array of the text (animal names)
        hints = [items_list[i]['text'] for i in hints_idx]
        #now limit the options to the animals that are not part of the hints
        possible_options_idx = [i for i in range(0, len(items_list)) if i not in hints_idx]
        options_list, options_cluster_list = generate_guessing_options(items_list, unique_cluster_labels, cluster_dict, cluster, possible_options_idx, N_GUESSES, N_OPTIONS)

    elif (version == "far"):
        #first hint is from the starting cluster
        hints_idx = random.sample(starting_cluster_item_idx, 1)
        #sample from all the cluster, making sure that each cluster gets at least one hint
        #first make sure that the non-starting clusters get at least one hint each
        for cur_cluster_label in unique_cluster_labels: 
            if cur_cluster_label != starting_cluster_label: 
                cur_cluster_idx = cluster_dict[cur_cluster_label]
                hints_idx.extend(random.sample(cur_cluster_idx, 1))
        #present the sparsely-sampled hints in order, then fill out the remaining number of hints with randomly selected hints
        possible_hints_idx = [i for i in range(0, len(items_list)) if i not in hints_idx]
        hints_idx.extend(random.sample(possible_hints_idx, N_GUESSES - len(hints_idx)))
        #hints is just an array of the text (animal names)
        hints = [items_list[i]['text'] for i in hints_idx]
        #now limit the options to the animals that are not part of the hints
        possible_options_idx = [i for i in range(0, len(items_list)) if i not in hints_idx]
        options_list, options_cluster_list = generate_guessing_options(items_list, unique_cluster_labels, cluster_dict, cluster, possible_options_idx, N_GUESSES, N_OPTIONS)
    
    hints_cluster = [str(cluster.labels_[x]) for x in hints_idx]

    return hints, hints_cluster, options_list, options_cluster_list