import ctypes
import pygame, sys
import os
import asyncio
import string

pygame.init()
currentscene = ["startscene"] #VERY IMPORTANT: first scene to be loaded
entities = [] #Loads all the buttons in the scene, so that the game can initialise each one's hitbox every update

#^^^stores the names of the objects in scene (text displays, buttons, timers, everything deemed important) alongside their ID (but only whenever you ACTUALLY draw them, otherwise they can't exist)
# whenever a new scene is to be loaded this list will be wiped and replace with the next scene's objects


questionIDs = [] #In the respective order, stores question ids to get answer attribute for later
timerID : int #Stores timer object runtime id to change access class methods or instance attributes later
scoreID : int #Stores score object runtime id to change access class methods or instance attributes later



Q_Num = 0 #tells us which question we are on NOW
playerScore = 0 #accumulative player score, based on how many correct and wrong
dynamicText = "" #stores concurrent text as a cache to update the text in textedit subclass object
windowClosed = False

# vvv Class constructors for button class, containing several button types as well (change scene button, mcq button, toggle button, lightswitch button)

class button:
    #start of button initialisation vars (our constants)
    #here, everytime we need a new button to show up or behave a particular way by referring to it,
    #   we don't need to manually code it in, we can refer to it here,
    #   and change it on the spot here too with classmethods
    def __init__(self, name = None, image = None, alt_image=None, buttonType = None):
        self.name = name #stores the identity of the button (A, B, C, D)
        self.imageName = image #caches the name of the original image (ex: Image.png)
        self.alt_imageName = alt_image #caches the name of the alternate image (same as imageName but for secondary toggle state / "tell the user if their answer is wrong or right")
        self.id = id(self) #assigns object id of this "button" class-instance (to be accessed later to change attributes/properties or methods using ctypes.cast())
        self.buttonType = buttonType #tells the game whether or not this button is a toggle-button or a normal-button
        self.h_boundingbox = [0,0] #important for cursor detection over a button (horizontal component)
        self.v_boundingbox = [0,0] #important for cursor detection over a button (vertical component)
        self.labels = None
        self.targetLabel = None


        #------returns a referalindex based on what name the button is, assuming its an MCQ and the name is a single character string---------
        if self.name and len(self.name) == 1: #returns a truthy
            self.referalIndex = string.ascii_lowercase.index(self.name.lower())
        else:
            self.referalIndex = None
        #-------------------------------------------------------------------------------------------------------------------------------------


        if image != None: 
        #NOTE ^^^ This checks if the button class was instantiated with an image (which it needs to be, at least imageName, alt_imageName is not required for normal buttons)

            self.image : list = ["fodder"] #self.image stores all images, alt and normal of a button
            #we add "fodder" because the way we access image and alt_image is using listIndex[1 and -1], 1 gets the second item in the list, -1 gets the last
            
            
            workingDir = os.path.dirname(__file__) #this gets the image's working directory
            path = os.path.join(str(workingDir), str(image)) #this connects the working directory to the original image filename (so that the system knows what to access, string formatting fails here)
            alt_path = os.path.join(str(workingDir), str(alt_image)) #same as "path" but for alt_imageName
            self.image.append(pygame.image.load(path)) #we append the image's path to the instance attribute self.image

            if alt_image != None: #NOTE: note that alt image is not required for all buttons, only toggle types
                #basically the point of this entire function here is if there is no alt_image (which is only needed for "toggle" buttons)
                #, then we check if the button type is a "toggle", if it isn't we just ignore it, if it is, then we make the original image the alt image as well to avoid crashes
                self.image.append(pygame.image.load(alt_path))
            else:
                if self.buttonType == "toggle":
                    self.image.append(pygame.image.load(path))
                else:
                    pass
        else:
            raise Exception(f"WARNING: No original image was given to {self.name}")
            crash() #crashes for debugging
                
        self.toggled_state = -1 #toggled_states:
                           # -1 = toggled off
                           #  1 = toggled on


    def initialiseLabels(self, xOffset=0, yOffset=0):
        if self.labels is not None and self.referalIndex < len(self.labels): #rarely called unless the question expects fewer buttons than there are in the scene and 
            if self.targetLabel is None:
                self.targetLabel = self.labels[self.referalIndex] #returns a string of the label
                offsetX = self.getPosition()[0] + xOffset
                offsetY = self.getPosition()[1] + yOffset
                self.labelPrompt = prompt(autoExpandMode=0, boxSize_x=0, boxSize_y=0, font_size=30)
                self.labelPrompt.setPosition(offsetX, offsetY)
                print(f"{self.name}: {offsetX}, {offsetY}")
            else:
                self.labelPrompt.text = self.targetLabel
                self.labelPrompt.draw(textcolor=[0,0,0])

    def setPosition(self, x = None, y = None):
        #Everytime before you draw an button onto the screen, you need to set its position
        self.cacheposition = self.Position(self.name) #unique reference to memory, a calling card to make sure the outerclass understands which object to call...
        
        #we change the x and y values in the Position innerclass
        self.cacheposition.x = x
        self.cacheposition.y = y

    def getPosition(self):
        #For buttons in particular, called 

        v2 = [self.cacheposition.x, self.cacheposition.y]
        for v in v2: #checks if this object even has any values changed in self.Position
            if v == None: 
                v2 = None
                print("WARNING: Object {} has no position values at all".format(self.name))
            else:
                pass
        return v2

    class Position:
        #this is the innerclass version of "position", which only stores x and y in the button baseclass
        def __init__(self, name):
            self.name = name
            self.x = None
            self.y = None
            
    def draw(self, pos = None, scale = None):
        #^^^ Basically, we call this function in the class shelf to ONLY draw stuff
        #    we dont expect and will never expect it to return anything, unless its code to be ran in main.py for __main__ == __name__
        if isinstance(scale, (int, float)):
            self.scale = scale
        elif not isinstance(scale, (int, float)):
            self.scale = 1
        #^^^ Checks if the scale is already set (defined as if it's been ignored by me or actually been tampered with)
        #    If it is set, we set it to the desired value, but if not, then we just assume that we're trying to get the set value
        

        surface = pygame.display.get_surface().get_size() #gets the currently active viewport's viewport layer's size
        width, height = surface[0], surface[1] #assigns the width and height respectively to the returned tuple of get_size()
        imgRes = self.image[self.toggled_state].get_size() #gets the (width, height) dimensions of the object's image
        happyGoLucky = False #gives the green flag for fool proof method

        if isinstance(pos, (tuple, list)): #checks if you've set anything for pos argument, if not, we assume you are braindead and assume autopilot
            #pos is happy
            happyGoLucky = True
        else:
            #pos isn't happy
            print("WARNING: no 'pos' argument detected, Failsafe activated, assuming getPosition()")
            if self.getPosition() == None:
                #no pos, no getPosition, wtf are you trying to do?
                print("FATAL ERROR TYPE: Object Error at {} [Attempted Process: draw(), self.getPosition() returned null]".format(self.name))
            else:
                #you have a getPosition, yay, we'll use that resource
                happyGoLucky = True



        if happyGoLucky: #done with the border checks, welcome to mexico :D
            if self.image[self.toggled_state] != None: #checks if the object's image (normal state) is valid, if not, should also crash tbh
                new_image = pygame.transform.scale(self.image[self.toggled_state], [imgRes[0] * self.scale, imgRes[1] * self.scale]) #scales the image to desired scale, if non, it just won't
                
                #mathematics
                new_pos = [0,0]
                new_pos[0] = pos[0] - (imgRes[0] * self.scale) / 2 #this part just translates the image to the centre before it places it on the screen 
                new_pos[1] = pos[1] - (imgRes[1] * self.scale) / 2
                #we will initialise the bounding box now, based on how much we've translated the box, (from 0,0 to new_pos)
                self.h_boundingbox[0] = new_pos[0]
                #left side
                self.h_boundingbox[1] = pos[0] + (imgRes[0] * self.scale) / 2 
                #right side

                self.v_boundingbox[0] = new_pos[1]
                #upper
                self.v_boundingbox[1] = pos[1] + (imgRes[1] * self.scale) / 2
                #lower

                if self.name == "lightswitch": #this just checks if this button is a funny lightswitch, idk why, its my script 
                    if self.toggled_state == 1:
                        pygame.display.get_surface().fill([0,0,0])


            #this whole block is dedicated to checking if a specific item is in the entities list
                inside = False
                for item in entities:
                    if item["ID"] == self.id:
                        inside = True

                if not inside:
                    entity = {
                        "NAME" : self.name,
                        "ID" : self.id,
                        "TYPE" : self.__class__.__name__,
                        "MEMORY ADDRESS" : self.__repr__() #parsed
                    }
                    entities.append(entity)
                else:
                    pass
                #^^^ Checks if the entities' id is already taken by another in this list, if not, just add the object to this list
                #    If yes, we use "pass" to not get in the way of any loops, especially since we're not returning anything
                #    everyone's happy just shut up about the "correct way" to do it


                

                return pygame.display.get_surface().blit(new_image.convert_alpha(), new_pos) #get_surface instead of set_mode(), set_mode() creates a new instance of a window again and again
                #^^^ this just returns the actual blit func to be ran in the main.py 
                

            else:
                print("ERROR: no image detected in {}, proceeding to die".format(self.name))
                crash() # type: ignore #crashes if you don't have an image, actually any image

            #!!NOTE:in case that the viewport isn't recognised in this script, we will call the actual function in the running script (not the transcompiled one here)
            #draw() intended to be called before every display.update() and after every fill()
            #intended to always have a position within viewport (relative to viewport)
        else:
            crash() # type: ignore #unironic solution, OJWDNFOASFHOAISHDF HAHAHAHA (this happens when you fail the border checks, you get shot in the head lmao)




    def pressed(self, funcType=None, loadscene=None): #intention of elements: we input ex: ("reset.funcType = 0")
        #in here, we need to pass initially what we want the button to do (for the sake of time, for buttons, we're only adding scene)
        noArgs = True
        args = [funcType, loadscene]
        for arg in args:
            if arg is not None:
                noArgs= False
        if noArgs:
            for i in entities:
                if i["ID"] == self.id:
                    print("%s was pressed" % [i["NAME"]])



        if isinstance(loadscene, str): #this is called twice so that the nested function doesn't get in the way of the self.loadscene object creation
            self.loadscene = loadscene
        elif not isinstance(loadscene, str):
            pass
        

        if isinstance(funcType, int):
            self.funcType = funcType
            # print("funcType of {a}: {b} | loadscene: {c}".format(a=self.name, b=funcType, c=self.loadscene))
        elif not isinstance(funcType, int):
            # print("funcType of {a}: {b}".format(a=self.name, b=funcType))
            if self.funcType == 0:
                #this mode changes the whole scene
                entities.clear()
                currentscene.clear()
                if isinstance(loadscene, str):
                    self.loadscene = loadscene
                elif not isinstance(loadscene, str):
                    currentscene.append(self.loadscene)

            
            elif self.funcType == 1:
                if self.buttonType == "toggle": #very specific, only redrawing the picture of the toggle button
                    self.toggled_state *= -1
                    self.draw(self.getPosition(), self.scale * 0.8)
                else:
                    addedScore = 0
                    #if you have a button in the scene that is funcType = 1, during runtime, you will be prompted with a screen
                    #that will ask you what elements you want to add, change, remove, etc
                    #the reason why we do this is because we want to test text display, text input/output and checks during runtime

                    #NOTE: hopefully by the time we're done, we would have used a seperate text files dedicated for every element if it shows up again
                    #      if we do this, then everytime the game is ran again, then that button's function will be dependent on whatever that file tells it to do
                    #      if not, the prompt will keep showing up, until you select a resource file, if you wish to change the resource file, then you need to change it with a command in runtime
                    notification = prompt(text="PRESS ANY KEY TO CONTINUE :) your time is still running")
                    notification.setPosition(400,30)
                    notification.draw()
                    ctypes.cast(timerID, ctypes.py_object).value.draw(textcolor=[255,0,0])
                    ctypes.cast(scoreID, ctypes.py_object).value.draw(textcolor=[255,0,0])


                    obj = ctypes.cast(questionIDs[Q_Num], ctypes.py_object).value
                    globals()["Q_Num"] += 1
                    if obj.answer == self.name:
                        globals()["playerScore"] += obj.points
                        addedScore = obj.points

                    # change the image of the A-D buttons to become the alt image, for "wrong"
                    for item in entities: 
                        
                        #NOTE: program will appear to slow down here becauses it pauses a bit to take things out of memory, which is occuring at least 3 times with each button, hence a total of 12 (CTYPES)

                        if item["NAME"] in ["A", "B", "C", "D"]:
                            cacheimage = ctypes.cast(item["ID"], ctypes.py_object).value.imageName
                            if item["NAME"] != obj.answer: #if wrong...
                                #we will now cache the current image name
                                #then we will proceed to reinitialise the button with the new image name
                                ctypes.cast(item["ID"], ctypes.py_object).value.__init__(name=item["NAME"], image="Wrong.png")
                                ctypes.cast(item["ID"], ctypes.py_object).value.draw(ctypes.cast(item["ID"], ctypes.py_object).value.getPosition(), 0.055)
                                ctypes.cast(item["ID"], ctypes.py_object).value.__init__(name=item["NAME"], image=cacheimage)
                            else:
                                ctypes.cast(item["ID"], ctypes.py_object).value.__init__(name=item["NAME"], image="Correct.png")
                                ctypes.cast(item["ID"], ctypes.py_object).value.draw(ctypes.cast(item["ID"], ctypes.py_object).value.getPosition(), 0.055)
                                ctypes.cast(item["ID"], ctypes.py_object).value.__init__(name=item["NAME"], image=cacheimage)
                    


                    ctypes.cast(scoreID, ctypes.py_object).value.text = f"Your Score: Added {addedScore}"
                    if addedScore > 0:
                        ctypes.cast(scoreID, ctypes.py_object).value.draw(textcolor=[51,255,51])
                    else:
                        ctypes.cast(scoreID, ctypes.py_object).value.draw(textcolor=[255,0,0])
                    ctypes.cast(timerID, ctypes.py_object).value.draw(textcolor=[255,0,0])
                    pygame.display.update()
                    asyncio.run(waiterFunc("anyKeyPressedEvent"))
                        

                    #If the button is not toggle, we are just gonna have it change something on screen instantly

# vvv Class constructors for "default text prompt", "question prompt", "timer/score prompts", "dynamic text edit prompt"

class prompt(): 
    #DEVELOPER NOTE: have finished making the text box itself, intend to add breaks in the text if its too long, prob like 70% of the entire width
    #                for the console itself, i'll add a fixed box that fills like 80% of the screen
    #                would really like to add scrolling as well btw
    #                
    #                instead of centering the text later on, i'll add a checker to see if youre making a question or a command prompt, and if its a 
    #                command prompt, the text will be anchored to the side starting from a fixed point, a percentage of the full width
    #                
    #                
    #                

    def __init__(self, text="", font="arial", font_size=15, autoExpandMode=1, boxSize_x=None, boxSize_y=None): #autoExpandMode=0 (manually change the size of box background), autoExpandMode = 1 (can leave the others blank)
        screen = pygame.display.get_surface()
        if self.__class__.__name__ == "timer":
            globals()["timerID"] = id(self)
        elif self.__class__.__name__ == "score":
            globals()["scoreID"] = id(self)
        
        width, height = screen.get_size()[0], screen.get_size()[1] 
        self.fontSize = font_size
        self.font_type = font
        self.font = pygame.font.SysFont(self.font_type, self.fontSize) #ONLY UPDATES ONCE WHEN YOU INSTANTIATE IT WITH THE __INIT__ FUNCTION
                                                                       #    FOR UPDATING, REUSE THE CHANGED INSTANCE ATTRIBUTES, AS CHANGING ONE DOESNT MEAN CHANGING THE OTHERS
        self.text = text    #setting the string of text
        class Position:
            x = width / 2
            y = height / 2
        
        self.position = Position()
        self.backgroundSize = [self.font.size(self.text)[0] + 10, self.font.size(self.text)[1] + 10] #we initialise the background box to have dimensions with extra border thickness
        self.autoExpandMode = autoExpandMode
        if self.autoExpandMode == 1:
            self.backgroundSize = [self.font.size(self.text)[0] + 10, self.font.size(self.text)[1] + 10]
        else:
            args = [boxSize_x, boxSize_y]
            for arg in args:
                if arg is None:
                    raise Exception(f"No arguments were found for boxSize_x && boxSize_y, for autoExpandMode was set to 1 || Warning from {self.__init__.__name__} in {self.__class__.__name__}")
            self.backgroundSize = [boxSize_x, boxSize_y]


    def getPosition(self):
        x = self.position.x #declaring x and y, based on the object's unique innerclass attributes (found in __init__)
        y = self.position.y

        t_x = x - self.font.size(self.text)[0] / 2 #this is the width of the whole text, we are centering the text along the horizontal
        t_y = y - self.font.size(self.text)[1] / 2 #this is the height of the whole text, in which we are cetnering the text along the vertical
        b_x = x - self.backgroundSize[0] / 2    #this is the width of the background, which we've artifically expanded, we are centering it along the horizontal
        b_y = y - self.backgroundSize[1] / 2    #this is the height of the background rect, centering it again
        return {
            "box_x" : b_x,
            "box_y" : b_y,
            "text_x" : t_x,
            "text_y" : t_y 
        }
    
    def setPosition(self, x = None, y = None):
        Args = False #this checks if there were any arguments passed through, if yes, we update the Args boolean allow the self.position.x and y to update
        args = [x, y]
        for val in args:
            if isinstance(val, (int, float)):
                Args = True
            else:
                pass

        if Args:
            self.position.x = x
            self.position.y = y

        else:
            print("ERROR: no args detected in class %s with class method %s" % [self.__class__.__name__, self.getPosition.__name__])
            crash() # type: ignore



    def draw(self, textcolor=[255,255,255], backgroundColor=[58, 59, 57]):
        screen = pygame.display.get_surface()
        renderedFont = pygame.font.SysFont(self.font_type, self.fontSize).render(self.text, True, textcolor)
        textPosition = [self.getPosition()["text_x"], self.getPosition()["text_y"]]
        if self.__class__.__name__ == "question":
            #the reason why we do this exclusively for "questions" is because IM TOO LAZY TO SET THE GODDAMN POSITION AND SIZING FOR EACH AND EVERY 10 OR MORE QUESTIONS
            #YOU TRY DOING IT ToT
            pos_x = 350
            pos_y = 100
            self.backgroundSize = [600,100]
            self.rectvalue = [pos_x - self.backgroundSize[0] / 2, pos_y - self.backgroundSize[1] / 2] + self.backgroundSize
            textPosition = [pos_x - self.font.size(self.text)[0] / 2, pos_y - self.font.size(self.text)[1] / 2]

        else:
            self.rectvalue = [self.getPosition()["box_x"],self.getPosition()["box_y"]] + self.backgroundSize #appends the list to have [position.x, position.y, dimension.x, dimension.y]
        
        pygame.draw.rect(screen, backgroundColor, self.rectvalue) #rect() syntax is as follows (target surface, color, (x_position, y_position, x_size, y_size) )
        screen.blit(renderedFont, textPosition) #drawing our text

# vvv Subclass of prompt to inherit from "prompt" class
class question(prompt): 
    #A subclass of "prompt" class, we can call methods and innerclasses and attributes from its superclass
    #Now the reason why we are subclassing it now is cuz its feasible, the superclass is 
    def __init__(self, text="", font="arial", font_size=15, answer=None, points=0, Qtype=0, autoExpandMode=1, boxSize_x=None, boxSize_y=None, numberOfButtons=4, labels=[]):
        #turns out that subclass __init__() constructors are actually their own thing, unrelated to the super().__init__()
        super().__init__(text, font, font_size, autoExpandMode, boxSize_x, boxSize_y)
        #even the __class__.__name__ is the "cls", which will be known as the subclass
        questionIDs.append(id(self)) #this is unique and important to using ctypes to identify the question answers, points, etc, DO NOT TOUCH
        if len(text) == 0:
            self.tempText = None
        else:
            self.tempText = text
        self.type = Qtype #0 means its an MCQ question, 1 means its a written one
        self.answer = answer
        self.points = points
        self.label = []
        #---Label initialisation---
        if isinstance(labels, list):
            for index in range(clampf(numberOfButtons, 0, len(string.ascii_lowercase))):
                if index < len(labels):
                    self.label.append(labels[index])
                else:
                    self.label.append(f"null label {index}")

        else:
            self.label = []
        #--------------------------
        errorDict = {
            "answer" : "Null answer(s)",
            "points" : "Null points",
            "tempText" : "Null placeholder or official text for this question",
            "type" : "type of question is neither MCQ or Subjective (Null)",
            "label" : "no label items detected or null"
        }
        for attr in iter(self.__class__.__dict__["__static_attributes__"]):
            ###due to the high volume of questions, we need to check if the question might break the program, 
            # so we just don't display or use any questions that are blank, or have no points or answers###
            '''Deeper explanation: 
                    "self" in this case is a subclass of "prompt" class, 
                    self.__class__ accesses the in-built __class__ special attributes, treating this subclass as its own class for a while
                    self.__class__.__dict__ accesses those __class__ special attributes
                    self.__class__.__dict__["__static_attributes__"] accesses only the class-instance attributes that are set in this class alone

                    self.__dict__ returns the same class-instance attributes, even the super() attributes

                    class variables are accessed by classname.variableName, they are shared among all instances that belong to that class
                    class-instance attributes are only accessed using .variablename outside the class, or variablename inside the class

            '''
            if attr in ("check"): #skips "check"
                continue
            if self.__dict__[attr] is not None: #checks if class-instance attributes are empty
                match attr:
                    case "answer":
                        if len(self.__dict__[attr]) == 0:
                            print("Error: Question says 'Nothing for question's answer'")
                            crash() # type: ignore
                        else:
                            continue
                    case "points":
                        if self.__dict__[attr] < 0:
                            print("Error: allocated Points cannot be negative")
                            crash() # type: ignore
                        elif self.__dict__[attr] == 0:
                            print("Warning: points is zero")
                        else:
                            continue
                    case "tempText":
                        if len(self.__dict__[attr]) == 0 or self.__dict__[attr] is None:
                            print("Error: Question says 'Nothing for question's text'")
                            crash() # type: ignore
                        else:
                            continue

                    case "type":
                        if self.__dict__[attr] not in (0, 1):
                            print("Error: No valid question type, but its not null")
                            crash() # type: ignore
                        else:
                            continue  
                    
                    case "label":
                        pass       
            else:
                print("Error: Question says %s " % [errorDict[attr]])
                crash() # type: ignore

        if self.type == 0:
            pass
        else:
            pass
                

class timer(prompt): #i could use __init_subclass__ or something but nah
    pass

class score(prompt):
    pass


class textEdit(prompt):
    def __init__(self, text="", font="arial", font_size=15, autoExpandMode=1, boxSize_x=None, boxSize_y=None):
        super().__init__(text, font, font_size, autoExpandMode, boxSize_x, boxSize_y)
        self.text = text

    def checkAnswer(self):
        globals()["dynamicText"] = ""

        notification = prompt(text="PRESS ANY KEY TO CONTINUE :) your time is still running")
        notification.setPosition(400,30)
        notification.draw()

        obj = ctypes.cast(questionIDs[Q_Num], ctypes.py_object).value

        globals()["Q_Num"] += 1
        def GODOFCHECKINGEYEOFRA():

            '''
            Basically this function checks if you've entered a string or a float

            100 is a float
            100.1 is a float
            -100.1 is a float
            -.543 is a float
                ABOUT FLOATS: if the float has a bad syntax, like -.-1 or 2.3.4, it will remain a string
            
                
            if your answer is a float and the answer is bad syntax, and the correct answer is a float, it will tell you where the problem lies
            ... and the answer too :)

            the only limitation here is that if  you enter a technical float like 500.5.1, you won't get the "bad number syntax" penalty
            
            '''

            ctypes.cast(scoreID, ctypes.py_object).value.text = f"Your Current Score: Added {obj.points}"
            ctypes.cast(scoreID, ctypes.py_object).value.draw(textcolor=[255,0,0])
            ctypes.cast(timerID, ctypes.py_object).value.draw(textcolor=[255,0,0])
            userAnswer = self.text #caching to leave the original data unaffected
            questionAnswer = obj.answer #caching to leave the original data unaffected
            letters = string.ascii_lowercase + string.ascii_uppercase + " "
            sts = ""
            add = ""
            addAns = ""
            achievedScore = 0
            query = [questionAnswer, userAnswer]
            splicedSentence = [[],[]] #[userAnswer spliced],[questionAnswer spliced]

            for i in query:
                indexVal = query.index(i) #caching this because if you try to access the index of 'i' after changing 'i', it doesn't exist anymore :p
                assign = ""

                for letter in i:
                    if letter.lower() in letters:
                        assign = "str"
                        break
                if assign == "str" or len(i) == 0: #if there's nothing in the input, the For loop just doesn't execute
                    query[indexVal] = str(i)
                else:
                    #at this point, its a float
                    #trying my best to not nest so deep as it becomes unreadable
                    if indexVal == 1:
                        if "-" in i and "." in i: #checks if your float formatting for "-" and "." is incorrect
                            if (i.index("-") > i.index(".")):
                                #kill
                                add = "(bad float) negatives cannot be behind decimals"
                                sts = "Wrong"
                                achievedScore = -2
                                addAns = f"Correct answer is {obj.answer}"
                                return (sts, add, addAns, achievedScore)

                            elif i.index("-") > 0:
                                #kill
                                add = "(bad float) negative sign not infront of number"
                                sts = "Wrong"
                                achievedScore = -2
                                addAns = f"Correct answer is {obj.answer}"
                                return (sts, add, addAns, achievedScore)

                            elif i.count(".") > 1:
                                #kill
                                add = "(bad float) too many decimals"
                                sts = "Wrong"
                                achievedScore = -2
                                addAns = f"Correct answer is {obj.answer}"
                                return (sts, add, addAns, achievedScore)


                            elif i.count("-") > 1:
                                #kill
                                add = "(bad float) too many negatives"
                                sts = "Wrong"
                                achievedScore = -2
                                addAns = f"Correct answer is {obj.answer}"
                                return (sts, add, addAns, achievedScore)


                            else:
                                query[indexVal] = float(i)
                        elif "-" in i:
                            if i.index("-") > 0:
                                #kill
                                add = "(bad float) negative in the wrong place"
                                sts = "Wrong"
                                achievedScore = -2
                                addAns = f"Correct answer is {obj.answer}"
                                return (sts, add, addAns, achievedScore)


                            elif i.count("-") > 0:
                                #kill
                                add = "(bad float) too many negatives"
                                sts = "Wrong"
                                achievedScore = -2
                                addAns = f"Correct answer is {obj.answer}"
                                return (sts, add, addAns, achievedScore)


                            else:
                                query[indexVal] = float(i)

                        elif "." in i:
                            if i.count(".") > 1:
                                #kill
                                add = "(bad float) too many decimals"
                                sts = "Wrong"
                                achievedScore = -2
                                addAns = f"Correct answer is {obj.answer}"
                                return (sts, add, addAns, achievedScore)

                            else:
                                query[indexVal] = float(i)

                        else:
                            #treat as normal float
                            query[indexVal] = float(i)
                    
                    
                    # here for the question here, above for the useranswer
                    
                    elif indexVal == 0:
                        if "-" in i and "." in i:
                            if (i.index("-") > i.index(".")) or i.index("-") > 0 or i.count(".") > 1 or i.count("-") > 1:
                                pass
                            else:
                                query[indexVal] = float(i)
                        elif "-" in i:
                            if i.index("-") > 0 or i.count("-") > 0:
                                pass
                            else:
                                query[indexVal] = float(i)
                        elif "." in i:
                            if i.count(".") > 1:
                                pass
                            else:
                                query[indexVal] = float(i)
                        else:
                            #treat as normal float
                            query[indexVal] = float(i)


            #check if both answers are the same type
            if type(query[0]) == type(query[1]) and type(query[0]) is str: #check if they're strings
                word = "" #need to store this here because it is accumulative (wish there was another way instead of clogging outside the code)
                currIndex = 0
                for i, v in enumerate(query):
                    currIndex = i
                    for char in query[currIndex]:
                        if char not in [" ", "-"]:
                            word += char.lower() #adds the word if there is a space
                        elif len(word) > 0 and char in [" ", "-"]: #adds the word if there is a space, doesn't add empty strings
                            splicedSentence[currIndex].append(word)
                            word = ""

                    if len(word) > 0: #adds the word if its the last word of the user's answer or the question class instance's answer, doesn't add empty strings
                        splicedSentence[currIndex].append(word)
                        word = ""
                #NOTE: Next, check for if the length of the words is matching, then check their individual letters, if not, then we squish them into one work and check letter by letter
                #squish the words'
                sentenceCombined = []
                def concat(ss):
                    tempSentence = ""
                    for a in ss:
                        tempSentence += a
                    return tempSentence.lower()
                        
                for i in splicedSentence:
                    sentenceCombined.append(concat(i))

                #these print statements are were only for debugging purposes
                # print(f"splicedSentence: {splicedSentence}")
                # print(f"Compare OBJ1: {sentenceCombined[0]}, Compare OBJ2: {sentenceCombined[1]}")

                if sentenceCombined[0] == sentenceCombined[1]: #checks if both sentences are the exact same, if not, return it as a wrong
                    globals()["playerScore"] += obj.points
                    sts = "Correct"
                    add = f"answer is {obj.answer}" 
                    achievedScore = obj.points

                else:
                    #kill
                    sts = "Wrong"
                    add = f"Correct answer is {obj.answer}" 

            elif type(query[0]) == type(query[1]) and type(query[0]) is float: #check if they're floats
                a = query[0]
                b = query[1]
                if abs(a - b) < 0.1 :
                    globals()["playerScore"] += obj.points
                    sts = "Correct"
                    add = f"answer is {obj.answer}"
                    achievedScore = obj.points

                else:
                    #kill
                    sts = "Wrong"
                    add = f"Correct answer is {obj.answer}"
                
            elif type(query[0]) != type(query[1]):
                #kill
                sts = "Wrong"
                add = f"Your answer is {type(query[1])}, but the actual answer is {type(query[0])}" 

            return (sts, add, addAns, achievedScore)
        


        
        (s, a, addAns, addedScore)= GODOFCHECKINGEYEOFRA()
        ctypes.cast(scoreID, ctypes.py_object).value.text = f"Your Score: Added {addedScore}"
        if addedScore > 0:
            ctypes.cast(scoreID, ctypes.py_object).value.draw(textcolor=[51,255,51])
        else:
            ctypes.cast(scoreID, ctypes.py_object).value.draw(textcolor=[255,0,0])
        ctypes.cast(timerID, ctypes.py_object).value.draw(textcolor=[255,0,0])
        result = f"Your answer is {s}, {a}"
        correctAns = prompt(text=result, font_size=20)
        correctAns2 = prompt(text=addAns, font_size=20, autoExpandMode=0, boxSize_x=300, boxSize_y=30)
        correctAns.setPosition(350, 470)
        correctAns2.setPosition(350, 500)
        correctAns.draw()
        if addAns != "":
            correctAns2.draw()
        else:
            pass

        self.text = "" #clears the text inside the textbox
        pygame.display.update()
        asyncio.run(waiterFunc("anyKeyPressedEvent"))

    def checkLength(self):
        if len(dynamicText) <= 28:
            return True
        elif len(dynamicText) < 0:
            return True
        else: 
            return False


# vvv Auxillary functions (math functions, async functions, async setter functions)

def clampf(val, min=None, max=None): #the purpose of this function is to check if "val" satisfies the min and maxc
    if not isinstance(min, (int, float)): #if you didn't set a min value, in the same frame you called this function, it changes the min value to the current passed in value
        min = val                         # to precis, it'll just do the same as (else: return val), leaving the val alone
    if not isinstance(max, (int, float)): #same thing here with the max value
        max = val

    if val <= min:
        return min
    elif val >= max:
        return max
    else:
        return val



async def anyKeyPressedEvent(event): #if any key is pressed, "event" will .set()
    a = True
    while a:
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                a = False
            elif e.type == pygame.QUIT:
                a = False
                globals()["windowClosed"] = True
                pygame.quit() #exits the pygame
                sys.exit() #exits the python program
    event.set()
    await event.wait()

async def waiterFunc(EventType=None): #this function will be called everytime you need a coroutine, it'll run and wait for the Event(event) function to finish its process, in which then it will allow the program to continue running as normal
    if not isinstance(EventType, str): #checks if its still None
        pass
        if isinstance(EventType, (float, int)): #Not allowed to add ints or floats
            crash() # type: ignore
    else:
        event = asyncio.Event()
        waitingFor = globals()[EventType](event)

        await waitingFor