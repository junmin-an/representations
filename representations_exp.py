## Experiment for Representations course

import expyriment
import random

WHITE = (255,255,255)
BLACK = (0,0,0)

exp = expyriment.design.Experiment(name="Representations",
                                   text_size = 43, 
                                   background_colour = WHITE) 

#expyriment.control.set_develop_mode(on=True)  ## Set develop mode. Comment for real experiment
expyriment.io.defaults.outputfile_time_stamp = False ## Remove timestamp from output file

expyriment.control.initialize(exp)
exp.data_variable_names = ["block", "image1", "image2", "diss_rating", "image", "x_pos", "y_pos"]

n = 16 ## Number of stimuli

block_arrangement = expyriment.design.Block(name="Arrangement Method")
trial_arr = expyriment.design.Trial()
stim_list = []

# Square arena
arena_size = min(exp.screen.size)
arena_left   = -arena_size // 2
arena_right  =  arena_size // 2
arena_top    =  arena_size // 2
arena_bottom = -arena_size // 2

# Vertical spacing for placing 8 stimuli per side
total_height = arena_size
step = total_height / 8
start_y = arena_size*0.9 // 2

# Horizontal positions OUTSIDE the arena
left_x  = arena_left  - (exp.screen.size[0] * 0.10)
right_x = arena_right + (exp.screen.size[0] * 0.10)

arena_border = expyriment.stimuli.Rectangle(
    size=(arena_size, arena_size),
    colour=(0,0,0),
    line_width=4
)

stim_dict = {}
stim_pos = []
i = 0
for x in [left_x, right_x]:
    for i in range(8):
        y = start_y - i * step 
        stim_pos.append((x, y))
random.shuffle(stim_pos)

for i in range(n):
    new_pic = expyriment.stimuli.Picture(f"/Users/junminan/Desktop/Master/M2/representations/stimuli/hat{i+1}.png", position=stim_pos[i])
    stim_dict[i+1] = new_pic

for s in stim_dict.values():
    s.preload()


block_pairwise = expyriment.design.Block(name="Pairwise Method")
for i in range(n):
    for j in range(i+1, n):
        trial = expyriment.design.Trial()
        trial.set_factor("i", i+1)
        trial.set_factor("j", j+1)

        stim = expyriment.stimuli.Canvas(size=exp.screen.size, colour=WHITE)

        position_ij = [(-400,0),(400,0)]
        random.shuffle(position_ij)

        pic1 = expyriment.stimuli.Picture(f"/Users/junminan/Desktop/Master/M2/representations/stimuli/hat{i+1}.png", position=position_ij[0])
        pic2 = expyriment.stimuli.Picture(f"/Users/junminan/Desktop/Master/M2/representations/stimuli/hat{j+1}.png", position=position_ij[1])

        pic1.scale(3)
        pic2.scale(3)
        pic1.plot(stim)
        pic2.plot(stim)

        txt = expyriment.stimuli.TextLine(
            "How visually similar are these two hats?",
            text_colour=(0,0,0),
            text_size = 40,
            position=(0, 250)
        )
        txt.plot(stim)

        txt2 = expyriment.stimuli.TextLine(
            "1----2----3----4----5----6----7----8----9",
            text_colour=(0,0,0),
            text_size = 45,
            position=(0, -250)
        )
        txt2.plot(stim)

        txt3 = expyriment.stimuli.TextLine(
            f"1-very dissimilar                  5-moderately similar                  9-very similar",
            text_colour=(0,0,0),
            text_size = 40,
            position=(0, -350)
        )
        txt3.plot(stim)

        stim.preload()
        trial.add_stimulus(stim)
        block_pairwise.add_trial(trial)

block_pairwise.shuffle_trials()

cue = expyriment.stimuli.FixCross(size=(50, 50), line_width=4) #fixation cross 
blankscreen = expyriment.stimuli.BlankScreen()

instructions_pairwise = expyriment.stimuli.TextScreen("Instructions",
    f"""You will see pairs of hats. Your task is to rate their VISUAL similarity out of 9.

    Rate similarity 1 (different) to 9 (similar) by pressing the corresponding key on the keyboard.

    Press SPACE to start.""", text_colour = (BLACK), heading_colour = BLACK)

instruction_arrangement = expyriment.stimuli.TextScreen("Instructions",
    f"""You will see 16 hats on the screen. Drag items with the mouse so distances between images on the screen reflect their similarity.

    When judging similarity, please try to focus on the VISUAL information that you can see.
    If the images look visually similar, place them close together, if they look visually dissimilar, place them farther away from each other.
    
    Press SPACE to start. 
    Press SPACE again when finished.""", text_colour = (BLACK), heading_colour = BLACK)

are_you_sure_message = expyriment.stimuli.TextScreen("Are you sure ?",
    f"""y/n""", text_colour = (BLACK), heading_colour = BLACK)

expyriment.control.start(skip_ready_screen=True)
methods = ["a", "p"]
random.shuffle(methods)

for method in methods:
    if method == "p":
        instructions_pairwise.present()
        exp.keyboard.wait_char(' ')
        for trial in block_pairwise.trials:
            blankscreen.present()
            exp.clock.wait(500)
            cue.present()
            exp.clock.wait(500)
            trial.stimuli[0].present()
            key, rt = exp.keyboard.wait_char(["1","2","3","4","5","6","7","8","9"])
            rating = int(key)
            i = trial.get_factor("i")
            j = trial.get_factor("j")
            exp.data.add(["pairwise", int(i), int(j), int(10-rating), None, None, None])
    else:
        instruction_arrangement.present()
        exp.keyboard.wait_char(' ')
        mouse = expyriment.io.Mouse()
        mouse.show_cursor(True)
        dragging = (False, None, None)
        offset = (0,0)
        finished = False
        canvas = expyriment.stimuli.Canvas(size=exp.screen.size, colour=WHITE)
        
        while not finished :
            # draw 
            canvas.clear_surface()
            
            for s in stim_dict.values():
                s.plot(canvas)
            arena_border.plot(canvas)
            canvas.present()

            mpos = mouse.position
            left = mouse.check_button_pressed(0)

            # Start dragging when mouse pressed on a stimulus
            if left and not dragging[0]:
                for key in stim_dict:
                    s = stim_dict[key]
                    if s.overlapping_with_position(mpos):   # CORRECT HITTEST
                        dragging = (True, s, key)
                        offset = (s.position[0] - mpos[0], s.position[1] - mpos[1])
                        break

            # Update dragging movement
            if left and dragging[0]:
                dragging[1].position = (mpos[0] + offset[0], mpos[1] + offset[1])
                stim_dict[dragging[2]] = dragging[1]

            # Drop the object when mouse released
            if (not left) and dragging[0]:
                dragging[1].position = (mpos[0] + offset[0], mpos[1] + offset[1])
                stim_dict[dragging[2]] = dragging[1]
                dragging = (False, None, None)
                offset = (0,0)

            if exp.keyboard.check(expyriment.misc.constants.K_SPACE):
                are_you_sure_message.present()
                key, rt = exp.keyboard.wait_char(["y","n"])
                if key == "y" or key == "Y":
                    finished = True
                elif key == "n" or key == "N":
                    finished = False
            
        for key in stim_dict:
            s = stim_dict[key]
            exp.data.add(["arrangement", None, None, None, int(key), float(s.position[0]), float(s.position[1])])

expyriment.control.end()
