from psychopy import visual, event, core, gui, tools
import os
import glob
import random
import math

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

def get_runtime_variables(runtime_vars, order, exp_title='SuperLearning'):
    while True: 
        dlg = gui.DlgFromDict(runtime_vars, order=order, title=exp_title)
        if dlg.OK: 
            #if subject code has already been used (only need to check the 'free_sort' folder)
            #then loop back to input box
            file_name = "data/RAW_DATA/free_sort/" + runtime_vars['subj_code'] + "_data_free_sort.csv"
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

#open 3 data files. 1 store data from free sort task, 1 store reasoning game trials, and 1 store reasoning game responses.
def create_data_files(subj_code, separator=','): 
    # create a data folder if it doesn't already exist
    try:
        os.mkdir('data/RAW_DATA/free_sort')
    except FileExistsError:
        print('Data directory exists; proceeding to open file')
    
    try:
        os.mkdir('data/RAW_DATA/learning')
    except FileExistsError:
        print('Data directory exists; proceeding to open file')

    try:
        os.mkdir('data/RAW_DATA/learning_trials')
    except FileExistsError:
        print('Data directory exists; proceeding to open file')

    #open file to write data to and store a header
    data_file_free_sort = open(f"data/RAW_DATA/free_sort/{subj_code}_data_free_sort.csv",'w')
    header_free_sort = separator.join(["subj_code","seed","version", 'phase','item',
                             'init_x', 'init_y', 'final_x', 'final_y', 'cluster', 'rt'])
    data_file_free_sort.write(header_free_sort+'\n')

    data_file_learning = open(f"data/RAW_DATA/learning/{subj_code}_data_learning.csv",'w')
    header_learning = separator.join(["subj_code","seed","version", 'phase', 'label',
                             'trial', 'hint', 'hint_cluster', 'options', 'options_cluster', 
                             'options_selection', 'rt'])
    data_file_learning.write(header_learning+'\n')

    data_file_learning_trials = open(f"data/RAW_DATA/learning_trials/{subj_code}_trials.csv",'w')
    header_learning_trials = separator.join(["subj_code","seed","version", 'phase', 'label',
                             'trial', 'hint', 'hint_cluster', 'options', 'options_cluster'])
    data_file_learning_trials.write(header_learning_trials+'\n')

    return data_file_free_sort, data_file_learning, data_file_learning_trials

def write_to_file_learning_trials(fileHandle, hints, hints_cluster, options_list, options_cluster_list, runtime_vars, separator=',', sync=False, add_newline=True):
    novel_cat = random.choice(['tulvers', 'sibus', 'tomas'])
    for i in range(len(hints)): 
        separator.join(["subj_code","seed","version", 'phase', 'label',
                             'trial', 'hint', 'hint_cluster', 'options', 'options_cluster'])
        data = [runtime_vars['subj_code'], runtime_vars['seed'], runtime_vars['Select version'], 
                'learning', novel_cat, 
                #trial number
                str(i+1), 
                hints[i], 
                hints_cluster[i], 
                options_list[i], 
                options_cluster_list[i]]
        line = separator.join([str(i) for i in data])
        if add_newline: 
            line += '\n'
        try:
            fileHandle.write(line)
        except:
            print('file is not open for writing')
        if sync: #set sync=False to NOT close the file after writing each line.
            fileHandle.flush()
            os.fsync(fileHandle)
    return

def write_to_file_free_sort(fileHandle, items_list, rt, runtime_vars, separator=',', sync=False, add_newline=True): 
    for item in items_list: 
        data = [runtime_vars['subj_code'], runtime_vars['seed'], runtime_vars['Select version'], 
                'sort', item['text'], 
                item['init_x'], item['init_y'], 
                #final_x and final_y
                item['rect'].pos[0], item['rect'].pos[1],
                item['cluster'], rt]
        line = separator.join([str(i) for i in data])
        if add_newline: 
            line += '\n'
        try:
            fileHandle.write(line)
        except:
            print('file is not open for writing')
        if sync: #set sync=False to NOT close the file after writing each line.
            fileHandle.flush()
            os.fsync(fileHandle)
        
def write_to_file_learning(fileHandle, trial, options, rt, separator=',', sync=False, add_newline=True): 
    list_sep = '/'
    #get information of current trial
    trial_info = [trial[_] for _ in trial]
    #add response information
    options_selection = list_sep.join([str(int(x['selected'])) for x in options])
    trial_info.extend([options_selection, rt])
    line = separator.join(list([str(i) for i in trial_info]))
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
