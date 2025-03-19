from psychopy import visual, event, core, gui # import the bits of PsychoPy we'll need for this walkthrough
import os
import random
import math
from helper import get_runtime_variables, import_trials, random_point_in_circle, create_data_files, write_to_file_free_sort, write_to_file_learning, write_to_file_learning_trials
from generate_guessing_game import generate_guessing_game, pluralize
from cluster import get_cluster, test_cluster, update_cluster

#open a window
WIN_SIZE = 800
#TODO: change this to full screen? 
win = visual.Window([WIN_SIZE,WIN_SIZE],color="grey", units='pix', checkTiming=False, 
                    fullscr=False) 

#get runtime variables
order =  ['subj_code','seed', 'version', 'n_guesses', 'n_options']
runtime_vars = get_runtime_variables({'subj_code':'sl_101', 'seed':23, 
                                      'Select version':['near', 'far'], 
                                      'n_guesses': 5, 
                                      'n_options': 5}, 
                                      order)
print(runtime_vars)

data_file_free_sort, data_file_learning, data_file_learning_trials = create_data_files(runtime_vars['subj_code'])

#create items list, to pass to generate_trials function
items = ['zebra', 'horse', 'giraffe', 'elephant', 'pig', 'sheep', 'cow', 'rabbit', 'seal', 'dog', 
         'cat', 'bear', 'tiger', 'fox', 'squirrel', 'monkey', 'human', 'raccoon', 'beaver', 'lion', 
         'mouse', 'whale', 'dolphin', 'shark', 'goldfish', 'eagle', 'parrot', 'penguin', 'peacock', 'fly', 
         'ant', 'bee', 'seahorse', 'chimpanzee', 'chicken', 'sealion', 'crab', 'snake', 'frog', 'turtle', 
         'butterfly', 'bat', 'worm', 'octopus', 'crocodile', 'gorilla', 'kangaroo', 'owl', 'gecko', 'mosquito',
         'jellyfish', 'scorpion', 'lobster', 'snail', 'spider', 'eel', 'salmon', 'cheetah', 'ostrich', 'starfish']

# select only a few from the items, to save free sorting time
# actual experiment should probably fix this number...
n_items = math.ceil((runtime_vars['n_guesses'] + runtime_vars['n_guesses'] * runtime_vars['n_options']) * 1.25)
items = random.sample(items, n_items)
items_list = list(map(lambda x: {'text': x}, items))

#show instructions
instruction_text = "Welcome to the experiment!\n\nPress the space bar to continue."
instruction = visual.TextStim(win, text = instruction_text,color="white", height=25, pos = (0,0))
instruction.draw()
win.flip()
#wait for the space key
event.waitKeys(keyList=['space'])
win.flip()
core.wait(.5)

#show instructions for visual sort task
instruction_visual_sort_text = "Please arrange these animals such that the ones more similar are closer together.\n\nPress the space bar when you are done."
instruction_visual_sort = visual.TextStim(win, text = instruction_visual_sort_text, color="white", height=25, pos = (0, WIN_SIZE/2 - 70), wrapWidth = WIN_SIZE * 0.8)
instruction_visual_sort.draw()

# create circle boundary, to pass to generate_trials function
RADIUS = WIN_SIZE * 0.4
boundary = visual.Circle(
    win=win,
    radius=RADIUS, # change this
    lineColor='black',
    fillColor='lightgreen',
    pos = (0, -70)
) 
boundary.draw()

item_positions = [] #keep track of item positions so that it's easier to check for location of rectangles to not be too overlapping.

for item in items_list: 
    #generate textboxes
    item_text = visual.TextStim(win,text=item['text'], height=20, color="black",pos=[0,0], 
                                draggable=True)
    item_rect = visual.Rect(win, width=item_text.boundingBox[0] + 10, #some additional padding
                                    height=item_text.boundingBox[1] + 10, 
                                    fillColor='white', lineColor='black')
    #Also from Claude.AI: check against existing locations to make sure text doesn't overlap
    #there's probably a better implementation of this
    item_x, item_y = random_point_in_circle(RADIUS, boundary.pos)
    existing_check_idx = 0
    while existing_check_idx < len(item_positions):
        existing_x, existing_y = item_positions[existing_check_idx]
        if math.sqrt((item_x - existing_x)**2 + (item_y - existing_y)**2) < 50: #actual number was trial and error
            #regenerate item_x and y
            item_x, item_y = random_point_in_circle(RADIUS, boundary.pos) 
            #reset check idx
            existing_check_idx = 0 
        else: 
            #go to the next existing position
            existing_check_idx += 1
    
    # once we get here, item_x and y have been checked against all the existing positions
    item_positions.append((item_x, item_y))
    item_text.setPos((item_x, item_y))
    item_rect.setPos((item_x, item_y))

    item['rect'] = item_rect
    item['text_stim'] = item_text

    item['init_x'] = item_x
    item['init_y'] = item_y

    item_rect.draw()
    item_text.draw()

win.flip()

#now we're gonna try to move the texts around.
# create a mouse
mouse = event.Mouse(win=win)
responseTimer = core.Clock()
# a little bit funky if you move the mouse too fast
while not event.getKeys(keyList=['space']):
    for item in items_list:
        if mouse.isPressedIn(item['rect']): 
            cur_item_rect = item['rect']
            cur_item_text = item['text_stim']
            # to keep the mouse on one particular item until it is released
            while mouse.isPressedIn(cur_item_rect): 
                #keep the text within the green boundary
                if boundary.contains(mouse): 
                    cur_item_rect.pos = mouse.getPos()
                    cur_item_text.pos = mouse.getPos()
                    instruction_visual_sort.draw()
                    boundary.draw()
                    for item in items_list: 
                        item['rect'].draw()
                        item['text_stim'].draw()
                    win.flip()

#get reaction time the moment 'space' is hit.
rt = responseTimer.getTime()
mouse.clickReset()

items_pos = list(map(lambda x: x['rect'].pos, items_list))
cluster = get_cluster(items_pos, max_n_cluster=10)
#update items_list with cluster label
items_list = update_cluster(items_list, cluster)

# write to the free sort data file
write_to_file_free_sort(data_file_free_sort, items_list, rt, runtime_vars)
data_file_free_sort.close()

#ONLY FOR DEMO: show colored-in clusters
instruction_test_cluster = visual.TextStim(win, text = "This part is here to test the clustering method, will be commented out for actual experiment. Press space bar to continue.", color="white", height=25, pos = (0, WIN_SIZE/2 - 70), wrapWidth = WIN_SIZE * 0.8)
instruction_test_cluster.draw()
test_cluster(cluster, items_list)
win.flip()
event.waitKeys(keyList=['space'])
win.flip()

#now play the guessing game
N_GUESSES = runtime_vars['n_guesses'] 
N_OPTIONS = runtime_vars['n_options']

# probably can combine these next two lines...
hints, hints_cluster, options_list, options_cluster_list = generate_guessing_game(items_list, cluster, runtime_vars['Select version'], N_GUESSES, N_OPTIONS)
write_to_file_learning_trials(data_file_learning_trials, hints, hints_cluster, options_list, options_cluster_list, runtime_vars)
data_file_learning_trials.close()

#read in trials
trial_path = f"data/RAW_DATA/learning_trials/{runtime_vars['subj_code']}_trials.csv"
trial_list = import_trials(trial_path)
print(trial_list)

novel_cat = trial_list[0]['label']

instruction_game_text = f"In this section, you'll hear about animals that are {novel_cat}. Some animals are {novel_cat}, but not all animals are {novel_cat}.\n\nYour task is to guess which animals are {novel_cat} based on the examples provided.\n\nPress the space bar to continue."
instruction_game = visual.TextStim(win, text = instruction_game_text, color="white", height=25, pos = (0, WIN_SIZE/2 - 200), wrapWidth = WIN_SIZE * 0.8)
instruction_game.draw()
win.flip()
event.waitKeys(keyList='space')
win.flip()
core.wait(.5)

#play the guessing game
for i in range(len(trial_list)):
    trial = trial_list[i]
    exemplar_text = f"{pluralize(trial['hint']).capitalize()} are {trial['label']}.\n\nOf the animals below, which one(s) do you think are also {trial['label']}?\n\nClick on a text box to select that animal (highlighted in yellow), click again to unselect. Press the space bar to continue."
    exemplar = visual.TextStim(win, text = exemplar_text, color="white", height=25, pos = (0, WIN_SIZE/2 - 200), wrapWidth = WIN_SIZE * 0.8)
    exemplar.draw()

    options = [{'text': x, 'selected': 0} for x in trial['options'].split('/')]
    print(options)

    # go through the options 
    for idx, opt_dict in enumerate(options): 
        #generate textboxes
        opt_text = visual.TextStim(win,text=opt_dict['text'], height=20, color="black",pos=[0,0])
        opt_rect = visual.Rect(win, width=120, #standardize so that they can be evenly distributed across the screen 
                               height=40, fillColor='white', lineColor='black')
        loc_x = -WIN_SIZE/2 + 100 + (WIN_SIZE-200) * idx / (N_OPTIONS-1) # distribute the options on the screen
        opt_text.setPos((loc_x, 0))
        opt_rect.setPos((loc_x, 0))
        opt_rect.draw()
        opt_text.draw()
        opt_dict['text_stim'] = opt_text
        opt_dict['rect_stim'] = opt_rect
    win.flip()

    while not event.getKeys(keyList=['space']): 
        for option in options:
            cur_rect = option['rect_stim'] 
            if mouse.isPressedIn(cur_rect): 
                #switch selection of option 
                option['selected'] = not option['selected']
                if option['selected']: 
                    cur_rect.setFillColor('yellow')
                else: 
                    cur_rect.setFillColor('white')
                for option in options:  
                    option['rect_stim'].draw()
                    option['text_stim'].draw()
                exemplar.draw()
                #reset the timer after it draws
                responseTimer.reset()
                win.flip()
                #wait a little so that the colors don't flip constantly...
                core.wait(.5)

    rt = responseTimer.getTime()
    mouse.clickReset()
    # write to the learning data file
    write_to_file_learning(data_file_learning, trial, options, rt)

data_file_learning.close()

#show thank you text and end
thanks_text = "Thank you for completing the study!\nPress the space bar to exit."
thanks = visual.TextStim(win, text = thanks_text,color="white", height=25, pos = (0,0))
thanks.draw()
win.flip()
#wait for the space key
event.waitKeys(keyList=['space'])
win.close() #close the window
core.quit() #quit out of the program

