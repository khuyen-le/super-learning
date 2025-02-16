from psychopy import visual, event, core, sound, gui # import the bits of PsychoPy we'll need for this walkthrough
import os
import random
import math
from generate_trials import generate_trials
from helper import get_runtime_variables, import_trials, random_point_in_circle

#open a window
WIN_SIZE = 800
#TODO: change this to full screen
win = visual.Window([WIN_SIZE,WIN_SIZE],color="grey", units='pix', checkTiming=False) 

#get runtime variables
order =  ['subj_code','seed']
runtime_vars = get_runtime_variables({'subj_code':'sl_101', 'seed':23}, order)
print(runtime_vars)

# generate trials
# generate_trials(runtime_vars['subj_code'],runtime_vars['seed'],runtime_vars['test_mode'])

#read in trials
#trial_path = os.path.join(os.getcwd(),'trials',runtime_vars['subj_code']+'_trials.csv')
#trial_list = import_trials(trial_path)
#print(trial_list)

#open file to write data to and store a header
#data_file = open(os.path.join(os.getcwd(),'data',runtime_vars['subj_code']+'_data.csv'),'w')
#header = separator.join(["subj_code","seed", 'image_name','item','angle','match','correct_response','response','rt'])
#data_file.write(header+'\n')

#show instructions
instruction_text = "Welcome to the experiment!\n\nPress the space bar to continue."
instruction = visual.TextStim(win, text = instruction_text,color="white", height=30, pos = (0,0))
instruction.draw()
win.flip()
#wait for the space key
event.waitKeys(keyList=['space'])
win.flip()
core.wait(.5)

items = ['dog', 'cat', 'ant', 'frog', 'shark', 'human', 'lion', 'rabbit', 'snake', 'eagle']
#trial loop
#responseTimer = core.Clock()

#while True:
# create circle boundary
RADIUS = WIN_SIZE * 0.4
boundary = visual.Circle(
    win=win,
    radius=RADIUS, # change this
    lineColor='black',
    fillColor='lightgreen'
) 
boundary.draw()
#win.flip()

item_positions = []
#for each item, create a textbox
#then keep track of the textboxes and their position, as a dict?

for item in items: 
    #generate textboxes
    item_text = visual.TextStim(win,text="", height=22, color="black",pos=[0,0], 
                                draggable=True)
    item_text.setText(item)
    item_rect = visual.Rect(win, width=item_text.boundingBox[0] + 10, #some additional padding
                                    height=item_text.boundingBox[1] + 10, 
                                    fillColor='white', lineColor='black')

    #Also from Claude.AI: check against existing locations to make sure text doesn't overlap
    #there's probably a better implementation of this
    item_x, item_y = random_point_in_circle(RADIUS)
    existing_check_idx = 0
    while existing_check_idx < len(item_positions):
        print("checking location of item " + item)
        existing_x, existing_y = item_positions[existing_check_idx]
        print(existing_x, existing_y)
        if math.sqrt((item_x - existing_x)**2 + (item_y - existing_y)**2) < 40: #actual number was trial and error
            print("too close, regenerating...")
            #regenerate item_x and y
            item_x, item_y = random_point_in_circle(RADIUS) 
            #reset check idx
            existing_check_idx = 0 
        else: 
            #go to the next existing position
            existing_check_idx += 1
    
    # once we get here, item_x and y have been checked against all the existing positions
    item_positions.append((item_x, item_y))
    item_text.setPos((item_x, item_y))
    item_rect.setPos((item_x, item_y))

    item_rect.draw()
    item_text.draw()

# yay! we figured out how to draw the free sort stuff!
# now let's figure out how to move things around the circle

# first I want to keep track of everything

stimuli = dict(zip(items, item_positions))
print(stimuli)

# getting help from drag_images
# create a mouse
mouse = event.Mouse(win=win)

win.flip()
core.wait(15)

#data_file.close()
win.close() #close the window
core.quit() #quit out of the program

