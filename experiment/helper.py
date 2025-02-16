from psychopy import visual, event, core, gui 
import os
import glob
import random
import math

def random_point_in_circle(radius): 
    #I got this idea from Claude.AI, before this I was just generating random x and y and checking whether it's inside the boundary of the circle or not
    #The idea is that a random point inside a circle can be described by its angle and r
    #First generate a random angle from 0 to 2pi (radians)
    angle = random.uniform(0, 2 * math.pi)
    #Then generate a random r, slightly smaller than circle radius to ensure text fits
    r = random.uniform(0, radius * 0.8)
    #Then calculate x and y using trigonometry!
    item_x = r * math.cos(angle)
    item_y = r * math.sin(angle)
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
