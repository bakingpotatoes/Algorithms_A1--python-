import pygame #module
import resources.classes as reference #local (for changing variables without allocating another slot in memory for another object of the same type in this file)
from resources.classes import button as button_obj #local
from resources.classes import prompt as prompt_obj #local
from resources.classes import question as question_obj #local
from resources.classes import timer as timer_obj #local
from resources.classes import score as score_obj #local
from resources.classes import clampf as clampf #local
from resources.classes import textEdit as textEdit_obj #local
import sys
import time
pygame.init()

running : bool = True
# -- initialise the screen -- 
width : int = 800
height : int = 600
screenRes : tuple = [width, height]
screen = pygame.display.set_mode(screenRes)
screen.fill([0,0,0])
openingText = prompt_obj("Look down at your terminal, its asking for your DESIRED TIME, you can't exit the program now until after this screen", font_size=18)
openingText2 = prompt_obj("Please just bear with me here", font_size=19)
openingText.setPosition(400,300)
openingText2.setPosition(400,400)
openingText.draw(backgroundColor=(0,0,0))
openingText2.draw(backgroundColor=(0,0,0))
pygame.display.update()

TIME = 0 #TIME set to another value when you input your "desired time"
def inputTime(string):
    
    numbers = ["0","1","2","3","4","5","6","7","8","9","."]
    temp = [input(string), "float"]
    if len(temp[0]) == 0:
        inputTime(string="Please input starting time: ")
    else:
        for i in temp[0]:
            if i not in numbers:
                temp[1] = "str"
        
        if temp[1] != "float":
            inputTime(string="You must be testing me! I said TIME, and that means numbers, you may include decimals too: " )
        else:
            if float(temp[0]) >= 50:
                global TIME
                TIME = float(temp[0])
            else:
                inputTime(string="Starting time must be MORE THAN 100 seconds lol: " )


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

colour : dict = {
    #some instances of colours, this was made with the background of the window in mind, btw
    #we will have a button that will enable and disable debugging, where we will have options to
    #change background colors, move around UI elements (by clicking and dragging) like the timer (for now)
    "red" : [255, 69, 0],
    "white" : [255, 255, 255]
}

# -- initialise all your elements --
debug = button_obj(name="debug", image="debug_button.png", buttonType="toggle", alt_image="Untitled.png")
lightswitch = button_obj(name="lightswitch", image="lightswitchoff.png", buttonType="toggle", alt_image="lightswitchon.png")
reset = button_obj(name="reset", image="5632370.png")
#each scene will have a light switch, it'll just turn off the lights
#each scene will have a debug button
#^^^buttons that will stay in every scene^^^

start = button_obj(name="start", image="5518039.png")
textInput = textEdit_obj(autoExpandMode=0, boxSize_x=600, boxSize_y=300, font_size=40)
textInputGuidance1 = prompt_obj(text="For string questions, write the exact string, spaces and hyphens don't matter", autoExpandMode=0, boxSize_x=600, boxSize_y=50, font_size=20)
textInputGuidance2 = prompt_obj(text="For number questions, don't include spaces, negatives before decimals, -.005 is -0.005, don't be silly", autoExpandMode=0, boxSize_x=600, boxSize_y=50, font_size=16)

#-----INITIALISING THE MCQ BUTTONS-----------
MCQbuttons = [button_obj(name="A", image="Green A.png"), button_obj(name="B", image="Green B.png"), button_obj(name="C", image="Green C.png"), button_obj(name="D", image="Green D.png")]
ogYpos = 250
ogXpos = 100
for i in MCQbuttons:
    i.setPosition(x=ogXpos, y=ogYpos)
    i.pressed(funcType=1)
    ogYpos += 70
    globals()[f"{i.name}"] = i #creates a global scope variable of the MCQbutton with the variable being the name of the button in its class instance
#--------------------------------------------

reset.setPosition(x=730, y=550)
debug.setPosition(x=730, y=50)
start.setPosition(x=400,y=300)
lightswitch.setPosition(x=730, y=130)

reset.pressed(funcType=0, loadscene="startscene")
lightswitch.pressed(funcType=1)
debug.pressed(funcType=1)
start.pressed(funcType=0, loadscene="questionscene")


currentQuestionType = 0
# -- create your scenes' layouts --
def startscene():
    global STARTTIMER
    STARTTIMER = time.perf_counter()
    reset.setPosition(x=730, y=550)
    debug.setPosition(x=730, y=50)
    debug.draw(debug.getPosition(), scale= 0.1)
    start.draw(start.getPosition(), scale=0.3)
    lightswitch.draw(lightswitch.getPosition(), scale=0.1)

    reference.playerScore = 0 #resets the score

def questionscene():
    #here's an example of a "scene"
    #process always goes like this, you declare the objects themselves outside as global vars
    #then you declare their position
    #then you draw them
    reset.setPosition(x=730, y=550)
    if QUESTIONS[reference.Q_Num].type == 0:
        #this part is for objective questions
        globals()["currentQuestionType"] = 0

        debug.draw(debug.getPosition(), scale= 0.1)
        for i in MCQbuttons: #reinitialising the buttons with the new question as its reference
            i.draw(i.getPosition(), scale=0.025)
            i.labels = QUESTIONS[reference.Q_Num].label
            i.initialiseLabels(xOffset=300)

        QUESTIONS[reference.Q_Num].draw()

    else:
        #this part is for subjective questions
        globals()["currentQuestionType"] = 1
        
        debug.draw(debug.getPosition(), scale= 0.1)
        QUESTIONS[reference.Q_Num].draw()
        textInput.text = reference.dynamicText
        textInput.setPosition(x=350, y=350)
        textInputGuidance1.setPosition(x=350, y=200)
        textInputGuidance2.setPosition(x=350, y=250)
        textInput.draw(backgroundColor=[211,211,211], textcolor=[0,0,0])
        textInputGuidance1.draw(backgroundColor=[255, 255, 0], textcolor=[0,0,0])
        textInputGuidance2.draw(backgroundColor=[255, 255, 0], textcolor=[0,0,0])

    score.draw()
    timer.draw()
    lightswitch.draw(lightswitch.getPosition(), scale=0.1)

    #upon backcalling "draw", you've created ALL the entities in the scene in a list, which the "engine" will recognise as "clickable" or "interactable"
    #then when you press a button for example, the next scene will load by changing what scene will load in the next loop (next frame)

def endscene(): #we can use this scene as the results screen 
    global STARTTIMER
    STARTTIMER = time.perf_counter()
    reference.Q_Num = 0
    percentage = (reference.playerScore / sum) * 100
    remark : str
    if percentage > 90:
        remark = ":D"
    elif percentage > 70:
        remark = ":)"
    elif percentage > 50:
        remark = ":|"
    elif percentage > 30:
        remark = ":("
    elif percentage > 0 and percentage <= 30:
        remark = ":'("
    else:
        remark = "(x_x)"


    reset.setPosition(x=400, y=300)
    reset.draw(reset.getPosition(), scale=0.5)
    score = score_obj(f"Your Final Score: {round(percentage, 2)}% {remark}", font_size=30)
    score.setPosition(x=400,y=50)
    score.draw()
    lightswitch.draw(lightswitch.getPosition(), scale=0.1)


#-- defining the check mouse function, keybindings located here --
def check_mouse():
    #checks through all instances
    #matches mouse position to see if its in the bounding box (only ever can be a box btw)'s bounds
    mouse_pos = pygame.mouse.get_pos()
    
    for enti in reference.entities:
        ent = globals()[enti["NAME"]] #turns the string into a variable from the global variables
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

        #in the current frame, imagine you are clicking, then we want to check if you were hovering over something, the hovering list would've changed long after as above
        #as far as this frame is concerned, you ARE indeed clicking on something that you ARE hovering on, without having to wait for any functions to update that hovering bit

#-- setting the opening scene -- 

QUESTIONS = [ 
    #------------------------
    #SET THE QUESTIONS HERE
    #------------------------

    question_obj("1) What are the first 3 digits of PI?", Qtype=1, font_size=20, answer="3.14", points=5),
    question_obj("2) Which one is a name of a snake?", answer="A", font_size=20, points=1, labels=["Python", "CSS", "Javascript", "HTML"]),
    question_obj("3) Evaluate the python expression: int(22/5)+23/4.", answer="C", points=1, font_size=20, labels=["10", "10.75", "9.75", "9"]),
    question_obj("4) What is the first name of the current monarch of England?", Qtype=1, font_size=20, answer="Charles", points=5),
    question_obj("5) Anyways back to real questions, what does SHA stand for?", Qtype=1, font_size=20, answer="Secure Hash Algorithm", points=5),
    question_obj("6) Which fruit is classified as a berry?", answer="A", points=1, font_size=20, labels=["Banana", "Strawberry", "Apple", "Peach"]),
    question_obj("7) What is the fourth option in this question?", answer="A", points=1, font_size=20, labels=["D", "Maybe D", "Must be D", "Not D"]),
    question_obj("8) My name has glass and tree in it, what frog am I?", Qtype=1, font_size=20, answer="Glass Tree Frog", points=5),
    question_obj("9) Quick Maths, 10+9+8+7+6+5+4+3+2+1 equals to?", Qtype=1, font_size=20, answer="55", points=5),
    question_obj("10) Let's try 55 in words, shall we?", Qtype=1, font_size=20, answer="Fifty-Five", points=5),
    question_obj("11) I have keys but no locks. I have space but no room. You can enter data, but you can't go inside, what am I? ", answer="B", points=1, font_size=15, labels=["Website", "Keyboard", "Monitor", "Spacebar"]),
    question_obj("12) I'm a 5-letter word starting with A and ending with O. No other word my length holds more vowels than me—who am I?", answer="A", points=1, font_size=12, labels=["Audio", "A 6-letter word", "Umbrella", "Vowel"])
]

sum = 0
for question in QUESTIONS:
    sum += question.points

inputTime(string="Please input starting time: ")
STARTTIMER = time.perf_counter() #when you reset the timer, make sure to reinstantiate this again, CURRENTTIME is reinstantiated every loop
tripped : bool = False
#-- game start loop --
while running:
    currentscene = reference.currentscene
    shift = pygame.key.get_pressed()[pygame.K_LSHIFT] #detects when you hold shift key
    CURRENTTIME = time.perf_counter() - STARTTIMER #increases in X.XX (2 decimal places), starts close to 0
    TIMELEFT = round(clampf(val=(TIME - CURRENTTIME), min=0.0), 1) #clamping it to 0 as minimum, maximum not set
    

    if (TIMELEFT == 0.00 or TIMELEFT < 0) and not tripped: #within the loop, it checks if the timeleft you have is up
        #LEVER TRIPPING CONDITION (REQUIRES PRIMARY CONDITION TO BE TRIPPED AND CHECKS IF ALREADY TRIPPED)
        #When your TIMELEFT is up, it removes all entities you can interact with and forces you to the endscene
        tripped = True
        currentscene.clear()
        currentscene.append("endscene")
        reference.entities.clear()
    elif TIMELEFT > 0 and tripped:
        #LEVER SELF UNTRIPPING (PRIMARY CONDITION OPPOSITE MUST BE MET AND MUST BE ALREADY TRIPPED)
        #untrips itself once the user chooses to "Reset", which will reset the timer and start back at the start
        #^^^ this lever tripping function allows the game to force the endscene when TIMELEFT is up only ONCE, 
        # allows the user to click other buttons in the scene and load other scenes when TIMELEFT is up but equals to or is below zero
        tripped = False


    if (reference.Q_Num + 1) > len(QUESTIONS): #Checks if youre at the end of the questions or not, clears the scene, loads endscene and clear all previous entities on screen
        currentscene.clear()
        currentscene.append("endscene")
        reference.entities.clear()

    screen.fill([181,199,235])
    timer = timer_obj(f"Your Remaining Time: {TIMELEFT} seconds", autoExpandMode=0, boxSize_x=250,boxSize_y=30)
    score = score_obj(f"Your Current Score: {reference.playerScore} / {sum}")
    timer.setPosition(x=190, y=580)
    score.setPosition(x=200, y=550)
    # --- game scene creation --- 
    #this will change upon pressing a button on the screen
    if currentscene[0] != None:
        globals()[currentscene[0]]() #loads the scene stored in a function callable
            
    else:
        crash() # type: ignore (JUST A CRASH TO CRASH SYSTEM FOR DEBUGGING)


    # ---=^^^ game scene creation ^^^=---


    
    for event in pygame.event.get(): #checks if any mouse or keyboard events are executed
        if event.type == pygame.MOUSEBUTTONDOWN: #checks if the event is a mouse click/scroll/moved cursor
            match event.dict["button"]: #checks through built-in pygame list of mouse event types (1 is LMB, 2 is MMB, 3 is RMB, 4 is scrollWheelUp, 5 is scrollWheelDown)
                # match-case is like if event.dict["button"] == 1, goto case 1 function
                case 1:
                    #left mouse button down
                    MOUSE["LEFTBUTTON"] = True
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
        
        elif event.type == pygame.KEYDOWN:
            if currentQuestionType == 1:
                inputKeyNames = [
                    "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
                    "0","1","2","3","4","5","6","7","8","9",".","-", "space"
                    ]

                if pygame.key.name(event.key) in inputKeyNames:
                    newtext = pygame.key.name(event.key)
                    if textInput.checkLength():
                        if pygame.key.name(event.key) == "space":
                            reference.dynamicText += " "
                        else:
                            if shift:
                                reference.dynamicText += newtext.upper()
                            else:
                                reference.dynamicText += newtext.lower()
                    
                elif pygame.key.name(event.key) == "backspace":
                    reference.dynamicText = reference.dynamicText[:-1] #selects all characters in a string except for the last one

                elif pygame.key.name(event.key) == "return": #return is just the enter key
                    textInput.checkAnswer()

            else:
                pass    


        if event.type == pygame.QUIT:
            #pygame is the base module, in it, contains enumerator constants that cannot be changed but can be accessed and calledback by the pygame.event module's .get() function
            #the pygame.QUIT eventtype is binded to a specific value that if it matches with the .get(eventtype=pygame."eventname"), will return a true in "if event == pygame.QUIT"
            #the .get() function returns the eventtype from the queue (a queue is the pygame engine's way of listening for mouseclicks, keystrokes, movements, etc)
            #the .type returns the assigned constant of that eventtype stored in pygame.event's module
            running = False
    #add a check for if the game window was already closed
    check_mouse()
    MOUSE["LEFTBUTTON"] = False
    MOUSE["MIDDLEMOUSE_BUTTON"] = False
    MOUSE["RIGHTBUTTON"] = False
    MOUSE["SCROLLDOWN"] = False
    MOUSE["SCROLLUP"] = False
    pygame.display.update()
pygame.quit()
sys.exit()
    #literally refreshes the screen