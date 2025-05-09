import ctypes
import sys, pygame
import resources.classes as reference
from resources.classes import button as button_obj
from resources.classes import prompt as prompt_obj
from resources.classes import question as question_obj
from resources.classes import timer as timer_obj
from resources.classes import score as score_obj
from resources.classes import clampf as clampf
import time
pygame.init()


TIME = 0
def hi(string):
    
    numbers = ["0","1","2","3","4","5","6","7","8","9","."]
    temp = [input(string), "float"]
    for i in temp[0]:
        if i not in numbers:
            temp[1] = "str"
    
    if temp[1] != "float":
        hi(string="You suck, i said a starting TIME, that means numbers, you may include decimals")
    else:
        if float(temp[0]) >= 10:
            global TIME
            TIME = float(temp[0])
        else:
            hi(string="Starting time must be MORE THAN 10 seconds lol")


MOUSESTATE : dict = {
    "HOVERING" : False,
    "HOVERING_OVER" : ""
}

MOUSE : dict = {

    "LEFTBUTTON" : False,
    "RIGHTBUTTON" : False,
    "MIDDLEMOUSE_BUTTON" : False,
    "SCROLLDOWN" : False,
    "SCROLLUP" : False
}

width : int = 800
height : int = 600
screenRes : tuple = [width, height]
running : bool = True
colour : dict = {
    #some instances of colours, this was made with the background of the window in mind, btw
    #we will have a button that will enable and disable debugging, where we will have options to
    #change background colors, move around UI elements (by clicking and dragging) like the timer (for now)
    "red" : [255, 69, 0],
    "white" : [255, 255, 255]
}

# -- initialise all your elements --
debug = button_obj(name="debug", image="debug_button.png", buttonType="toggle", alt_image="Untitled.png")
lightswitch = button_obj(name="lightswitch", image="debug_button.png", buttonType="toggle", alt_image="Untitled.png")
reset = button_obj(name="reset", image="debug_button.png")
#each scene will have a light switch, it'll just turn off the lights
#each scene will have a debug button
#^^^buttons that will stay in every scene^^^

# -- initialise the screen -- 
screen = pygame.display.set_mode(screenRes)

start = button_obj(name="start", image="debug_button.png")
A = button_obj(name="A", image="debug_button.png")
B = button_obj(name="B", image="debug_button.png")
C = button_obj(name="C", image="debug_button.png")
D = button_obj(name="D", image="debug_button.png")

# -- create your scenes' layouts --
def scene1():
    global STARTTIMER
    STARTTIMER = time.perf_counter()
    reset.setPosition(x=730, y=550)
    debug.setPosition(x=730, y=50)
    start.setPosition(x=400,y=300)
    lightswitch.setPosition(x=730, y=130)

    reset.pressed(funcType=0, loadscene="scene1")
    lightswitch.pressed(funcType=1)
    debug.pressed(funcType=1)
    start.pressed(funcType=0, loadscene="scene2")

    reset.draw(reset.getPosition(), scale=0.1)
    debug.draw(debug.getPosition(), scale= 0.1)
    start.draw(start.getPosition(), scale=0.3)
    lightswitch.draw(lightswitch.getPosition(), scale=0.1)

    reference.playerScore = 0

def scene2():
    #here's an example of a "scene"
    #process always goes like this, you declare the objects themselves outside as global vars
    #then you declare their position
    #then you draw them
    A.setPosition(x=100, y=250)
    B.setPosition(x=100, y=320)
    C.setPosition(x=100, y=390)
    D.setPosition(x=100, y=460)

    A.pressed(funcType=1)
    B.pressed(funcType=1)
    C.pressed(funcType=1)
    D.pressed(funcType=1)

    reset.draw(reset.getPosition(), scale=0.1)
    debug.draw(debug.getPosition(), scale= 0.1)
    A.draw(A.getPosition(), scale=0.1)
    B.draw(B.getPosition(), scale=0.1)
    C.draw(C.getPosition(), scale=0.1)
    D.draw(D.getPosition(), scale=0.1)
    lightswitch.draw(lightswitch.getPosition(), scale=0.1)

    score.draw()
    timer.draw()

    #upon backcalling "draw", you've created ALL the entities in the scene in a list, which the "engine" will recognise as "clickable" or "interactable"
    #then when you press a button for example, the next scene will load by changing what scene will load in the next loop (next frame)

def endscene(): #we can use this scene as the results screen 
    global STARTTIMER
    STARTTIMER = time.perf_counter()
    reset.setPosition(x=400, y=300)
    reset.draw(reset.getPosition(), scale=0.5)
    score = score_obj(f"Your Final Score: {reference.playerScore}", font_size=30)
    score.setPosition(x=400,y=50)
    score.draw()


#-- defining the check mouse function, keybindings located here --
def check_mouse():
    #checks through all instances
    #matches mouse position to see if its in the bounding box (only ever can be a box btw)'s bounds
    mouse_pos = pygame.mouse.get_pos()
    # print(reference.entities)
    
    for enti in reference.entities:
        ent = globals()[enti["NAME"]] #turns the string into a variable from the global variables
        # print("h_box params: ", ent.h_boundingbox, "v_box params: ", ent.v_boundingbox)
        #CHECK THE MOUSE HOVER FUNCTION
        if mouse_pos[0] > ent.h_boundingbox[0] and mouse_pos[0] < ent.h_boundingbox[1] and mouse_pos [1] > ent.v_boundingbox[0] and mouse_pos[1] < ent.v_boundingbox[1]:
            #here we are hovering in this frame, next frame, only check FIRST if we're hovering or not then update the cursor,
            MOUSESTATE["HOVERING"] = True
            MOUSESTATE["HOVERING_OVER"] = ent
            if MOUSE["LEFTBUTTON"]:
                MOUSESTATE["HOVERING_OVER"].pressed() #please please please check it in the same function its assigned or your chance is gone
        else:
            MOUSESTATE["HOVERING"] = False
            MOUSESTATE["HOVERING_OVER"] = ""


    if MOUSESTATE["HOVERING"]:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        #in the current frame, imagine you are clicking, then we want to check if you were hovering over something, the hovering list would've changed long after as above
        #as far as this frame is concerned, you ARE indeed clicking on something that you ARE hovering on, without having to wait for any functions to update that hovering bit

        

#-- setting the opening scene -- 

QUESTIONS = [
    question_obj("1)    Which one is a name of a snake?", answer="A", points=1),
    question_obj("2)	What is the fourth option in this question?", answer="A", points=1),
    question_obj("3)	Evaluate the python expression: int(22/5)+23/4.", answer="C", points=1),
    question_obj("4)	How many hours do FIC students study a day?", answer="D", points=1),
    question_obj("5)	I have keys but no locks. I have space but no room. You can enter data, but you can't go inside, what am I? ", answer="B", points=1),
    question_obj("6)	Which fruit is classified as a berry?", answer="A", points=1),
    question_obj("7)	I'm a 5-letter word starting with A and ending with O. No other word my length holds more vowels than me—who am I?", answer="A", points=1),
    question_obj("8)	What was the answer to the first question in this quiz?", answer="C", points=1),
    question_obj("9)	Which mathematical expression below equals 2?", answer="D", points=1),
    question_obj("10)	Where is Taylor University located?", answer="B", points=1)
]


hi("Please input starting time: ")
STARTTIMER = time.perf_counter() #when you reset the timer, make sure to reinstantiate this again, CURRENTTIME is reinstantiated every loop
tripped : bool = False
#-- game start loop --
while running:
    CURRENTTIME = time.perf_counter() - STARTTIMER #increases in X.XX (2 decimal places)
    TIMELEFT = round(clampf(val=(TIME - CURRENTTIME), min=0.0), 0) #clamping it to 0 as minimum, maximum not set
    if (TIMELEFT == 0.00 or TIMELEFT < 0) and not tripped: #within the loop, it checks if the timeleft you have is up
        #LEVER TRIPPING CONDITION (REQUIRES PRIMARY CONDITION TO BE TRIPPED AND CHECKS IF ALREADY TRIPPED)
        tripped = True
        currentscene.clear()
        currentscene.append("endscene")
        reference.entities.clear()
    elif TIMELEFT > 0 and tripped: #untrips the one time call if ("endscene" not in currentscene) condition is met (In this case, this is called assuming that you've restarted the timer)
        #LEVER SELF UNTRIPPING (PRIMARY CONDITION OPPOSITE MUST BE MET AND MUST BE ALREADY TRIPPED)
        #   if we don't add the reverse of the primary condition, we will only trip and untrip for every loop... not ideal when you dont want a rapid fire of TRUE and FALSE
        tripped = False
        #this function just makes it so that we can call this lever function multiple times in the same loop without anything additional

    currentscene = reference.currentscene
    screen.fill(colour.get("red"))
    timer = timer_obj(f"Your Remaining Time: {TIMELEFT} seconds", autoExpandMode=0, boxSize_x=250,boxSize_y=30)
    score = score_obj(f"Your Current Score: {reference.playerScore} / SUM QUESTION SCORES")
    timer.setPosition(x=190, y=580)
    score.setPosition(x=200, y=550)
    # --- game scene creation --- 
    #this will change upon pressing a button on the screen
    if currentscene[0] != None:
        globals()[currentscene[0]]() #loads the scene stored in a function callable
        # if reference.displayPrompt: #if enabled, this will cause a center prompt screen to pop up in the middle (originally for CMD)
        #     prompt = prompt_obj(text="sdasdoa", font="arial")
        #     prompt.setPosition(x=400,y=300)
        #     prompt.draw()
            
    else:
        crash() # type: ignore (JUST A CRASH TO CRASH SYSTEM FOR DEBUGGING)


    # ---=^^^ game scene creation ^^^=---


    
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            match event.dict["button"]:
                case 1:
                    #left mouse button down
                    MOUSE["LEFTBUTTON"] = True
                    print("Input detected: Left Mouse Button")
                    pass
                case 2:
                    #scroll wheel button down
                    MOUSE["MIDDLEMOUSE_BUTTON"] = True
                    pass
                case 3:
                    #right mouse button down
                    MOUSE["RIGHTBUTTON"] = True
                    pass
                case 4:
                    #scroll wheel up
                    MOUSE["SCROLLUP"] = True
                    pass
                case 5:
                    #scroll wheel down
                    MOUSE["SCROLLDOWN"] = True
                    pass
            pass

        if event.type == pygame.QUIT:
            #print("Closing window \nQuitting Pygame")

            #pygame is the base module, in it, contains enumerator constants that cannot be changed but can be accessed and calledback by the pygame.event module's .get() function
            #the pygame.QUIT eventtype is binded to a specific value that if it matches with the .get(eventtype=pygame."eventname"), will return a true in "if event == pygame.QUIT"
            #the .get() function returns the eventtype from the queue (a queue is the pygame engine's way of listening for mouseclicks, keystrokes, movements, etc)
            #the .type returns the assigned constant of that eventtype stored in pygame.event's module
            running = False

    check_mouse()

    MOUSE["LEFTBUTTON"] = False
    MOUSE["MIDDLEMOUSE_BUTTON"] = False
    MOUSE["RIGHTBUTTON"] = False
    MOUSE["SCROLLDOWN"] = False
    MOUSE["SCROLLUP"] = False
    pygame.display.update()
pygame.quit()
    #literally refreshes the screen