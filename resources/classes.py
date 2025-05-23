import ctypes
from enum import Enum
import pygame, sys
import os
import asyncio
import time

pygame.init()
currentscene = ["startscene"] #VERY IMPORTANT: first scene to be loaded
entities = [] #Loads all the buttons in the scene, so that the game can initialise each one's hitbox every update
questionIDs = [] #In the respective order, stores question ids to get answer attribute for later

timerID : int #Stores timer id to change access class methods or instance attributes later
scoreID : int #Stores score id to change access class methods or instance attributes later

#^^^stores the names of the objects in scene (text displays, buttons, timers, everything deemed important) alongside their ID (but only whenever you ACTUALLY draw them, otherwise they can't exist)
# whenever a new scene is to be loadedthis list will be wiped and replace with the next scene's objects


Q_Num = 0 #tells us which question we are on NOW
playerScore = 0 #stores the player score

class button:
    #start of button initialisation vars (our constants)
    #here, everytime we need a new button to show up or behave a particular way by referring to it,
    #   we don't need to manually code it in, we can refer to it here,
    #   and change it on the spot here too with classmethods
    def __init__(self, name = None, image = None, alt_image=None, buttonType = None):
        self.name = name #stores the name of the button
        self.imageName = image #caches the name of the original image
        self.alt_imageName = alt_image #caches the name of the alternate image
        self.id = id(self) #sets the id isolated id allocation of this object
        self.buttonType = buttonType #if not set to "toggle", we'll just ignore it and treat it as a normal button
        self.h_boundingbox = [0,0] #important for box and cursor detection
        self.v_boundingbox = [0,0]  #important for box and cursor detection


        if image != None:

            #This here checks if the programmer had given this button an image
            #   if not, it'll raise exception to tell the programmer where the error was at least

            self.image : list = ["fodder"] #we add this because the way we access image and alt_image is using listIndex[1 and -1], 1 gets the second item in the list, -1 gets the last
            workingDir = os.path.dirname(__file__) #this gets the file's working directory
            path = os.path.join(str(workingDir), str(image)) #this connects the working directory to the original image file
            alt_path = os.path.join(str(workingDir), str(alt_image)) #this connects the working directory to the alternate image file
            self.image.append(pygame.image.load(path)) #we append the image's path to the instance attribute self.image

            if alt_image != None:
                #basically the point of this entire function here is if there is no alt_image (which is only needed for "toggle" buttons)
                #, then we check if its a toggle, if it isn't we just ignore it, if it is, then we make the original image the alt image as well to avoid crashes
                self.image.append(pygame.image.load(alt_path))
            else:
                if self.buttonType == "toggle":
                    self.image.append(pygame.image.load(path))
                else:
                    pass
        else:
            raise Exception(f"WARNING: No original image was given to {self.name}")
                
        self.toggled_state = -1 #toggled_states:
                           # -1 = toggled off
                           #  1 = toggled on

    def setPosition(self, x = None, y = None):
        #I use this function to set the position of the object everytime
        self.cacheposition = self.Position(self.name) #unique reference to memory, a calling card to make sure the outerclass understands which object to call...
        self.cacheposition.x = x #we change the values inside this mf
        self.cacheposition.y = y
        # print("{a}'s position: {b}".format(a=self.name, b=self.getPosition()))

    def getPosition(self):
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
        #^^^ Basically, we call this function in the class shelf to ONLY draw shit
        #    we dont expect and will never expect it to return anything, unless its code to be ran in main.py for __main__ == __name__
        print("drawing")
        if isinstance(scale, (int, float)):
            self.scale = scale
        elif not isinstance(scale, (int, float)):
            self.scale = 1
        #^^^ Checks if the scale is already set (defined as if it's been ignored by me or actually been tampered with)
        #    If it is set, we set it to the desired value, but if not, then we just assume that we're trying to get the set value
        

        surface = pygame.display.get_surface().get_size() #gets the currently active viewport's viewport layer's size, im not explaining wtf a root, canvas, blah blah layer is
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
                print("you're an actual retard | FATAL ERROR TYPE: Object Error at {} [Attempted Process: draw(), self.getPosition() returned null]".format(self.name))
            else:
                #you have a getPosition, yay, we'll use that resource
                happyGoLucky = True



        if happyGoLucky: #done with the border checks, welcome to mexico :D
            if self.image[self.toggled_state] != None: #checks if the object's image (normal state) is valid, if not, should also crash tbh
                new_image = pygame.transform.scale(self.image[self.toggled_state], [imgRes[0] * self.scale, imgRes[1] * self.scale]) #scales the image to desired scale, if non, it just won't
                
                #mathematics CS majors couldn't be fucked to understand !!!
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
                #mathematics CS majors couldn't be fucked to understand !!!

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
                    #if you have a button in the scene that is funcType = 1, during runtime, you will be prompted with a screen
                    #that will ask you what elements you want to add, change, remove, etc
                    #the reason why we do this is because we want to test text display, text input/output and checks during runtime

                    #NOTE: hopefully by the time we're done, we would have used a seperate text files dedicated for every element if it shows up again
                    #      if we do this, then everytime the game is ran again, then that button's function will be dependent on whatever that file tells it to do
                    #      if not, the prompt will keep showing up, until you select a resource file, if you wish to change the resource file, then you need to change it with a command in runtime
                    notification = prompt(text="PRESS ANY KEY TO CONTINUE :)")
                    notification.setPosition(400,30)
                    notification.draw()
                    ctypes.cast(timerID, ctypes.py_object).value.draw(color=[255,0,0])
                    ctypes.cast(scoreID, ctypes.py_object).value.draw(color=[255,0,0])


                    obj = ctypes.cast(questionIDs[Q_Num], ctypes.py_object).value
                    globals()["Q_Num"] += 1
                    if obj.answer == self.name:
                        globals()["playerScore"] += 1

                    # change the image of the A-D buttons to become the alt image, for "wrong"
                    for item in entities:
                        if item["NAME"] in ["A", "B", "C", "D"]:
                            cacheimage = ctypes.cast(item["ID"], ctypes.py_object).value.imageName
                            if item["NAME"] != obj.answer: #if wrong...
                                #we will now cache the current image name
                                #then we will proceed to reinitialise the button with the new image name
                                ctypes.cast(item["ID"], ctypes.py_object).value.__init__(name=item["NAME"], image="lightswitchoff.png")
                                ctypes.cast(item["ID"], ctypes.py_object).value.draw(ctypes.cast(item["ID"], ctypes.py_object).value.getPosition(), ctypes.cast(item["ID"], ctypes.py_object).value.scale)
                                ctypes.cast(item["ID"], ctypes.py_object).value.__init__(name=item["NAME"], image=cacheimage)
                            else:
                                ctypes.cast(item["ID"], ctypes.py_object).value.__init__(name=item["NAME"], image=cacheimage)
                                ctypes.cast(item["ID"], ctypes.py_object).value.draw(ctypes.cast(item["ID"], ctypes.py_object).value.getPosition(), ctypes.cast(item["ID"], ctypes.py_object).value.scale)
                    

                    pygame.display.update()
                    asyncio.run(waiterFunc("anyKeyPressedEvent"))
                        

                    #If the button is not toggle, we are just gonna have it change something on screen instantly



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



    def draw(self, pos_x=350, pos_y=100, color=[255,255,255]):
        screen = pygame.display.get_surface()
        renderedFont = pygame.font.SysFont(self.font_type, self.fontSize).render(self.text, True, color)
        textPosition = [self.getPosition()["text_x"], self.getPosition()["text_y"]]
        if self.__class__.__name__ == "question":
            #the reason why we do this exclusively for "questions" is because IM TOO LAZY TO SET THE GODDAMN POSITION AND SIZING FOR EACH AND EVERY 10 OR MORE QUESTIONS
            #YOU TRY DOING IT ToT
            self.backgroundSize = [600,100]
            self.rectvalue = [pos_x - self.backgroundSize[0] / 2, pos_y - self.backgroundSize[1] / 2] + self.backgroundSize
            textPosition = [pos_x - self.font.size(self.text)[0] / 2, pos_y - self.font.size(self.text)[1] / 2]

        else:
            self.rectvalue = [self.getPosition()["box_x"],self.getPosition()["box_y"]] + self.backgroundSize #appends the list to have [position.x, position.y, dimension.x, dimension.y]
        
        pygame.draw.rect(screen, (58, 59, 57), self.rectvalue) #rect() syntax is as follows (target surface, color, (x_position, y_position, x_size, y_size) )
        screen.blit(renderedFont, textPosition) #drawing our text


class question(prompt): 
    #A subclass of "prompt" class, we can call methods and innerclasses and attributes from its superclass
    #Now the reason why we are subclassing it now is cuz its feasible, the superclass is 
    def __init__(self, text="", font="arial", font_size=15, answer=None, points=None, Qtype=0, autoExpandMode=1, boxSize_x=None, boxSize_y=None):
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
        self.check = True
        for i in self.__class__.__dict__["__static_attributes__"]: #due to the high volume of questions, we need to check if the question might break the program, so we just don't display or use any questions that are blank, or have no points or answers
            if self.__dict__[str(i)] is None or self.__dict__[str(i)] == None:
                self.check = False

class hint(prompt):
    def __init__(self, text="", font="arial", font_size=15):
        super().__init__(text, font, font_size)
    
    def getPosition(self):
        x = self.position.x #declaring x and y, based on the object's unique innerclass attributes (found in __init__)
        y = self.position.y

        t_x = x + self.backgroundSize[0] / 2 #here we just replace the function, not centering it tbh, but we do need to center the t_x and t_y
        t_y = y + self.backgroundSize[1] / 2
        b_x = self.backgroundSize[0]
        b_y = self.backgroundSize[1]
        return {
            "box_x" : b_x,
            "box_y" : b_y,
            "text_x" : t_x,
            "text_y" : t_y 
        }
    
class timer(prompt): #i could use __init_subclass__ or something but nah
    pass

class score(prompt):
    pass


def clampf(val, min=None, max=None): #the purpose of this function is to check if "val" satisfies the min and max
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
        # print("PLEASE PRESS ANY KEY TO CONTINUE")
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN:
                a = False
            elif e.type == pygame.QUIT:
                a = False
                pygame.quit()
    event.set()
    await event.wait()

async def waiterFunc(EventType=None): #this function will be called everytime you need a coroutine, it'll run and wait for the Event(event) function to finish its process, in which then it will allow the program to continue running as normal
    if not isinstance(EventType, str): #checks if its still None
        pass
        if isinstance(EventType, (float, int)): #Not allowed to add ints or floats
            crash()
    else:
        event = asyncio.Event()
        waitingFor = globals()[EventType](event)

        await waitingFor

class t1():
    def __init__(self, points):
        self.points = points
    def setname(self):
        if __name__ == "__main__":
            return f"this is: {self.__class__.__name__}"
        
    def printname(self):
        print(self.setname())

class t2(t1):
    def __init__(self, points):
        super().__init__(points)

    def setname(self):
        if __name__ == "__main__":
            var1 = "override"
            return var1
        #self.points is calling the superclass' attribute, however, because the self.points is an attribute that is created in a __init__ function, it is 
        #   linked to the object id that owns it, so technically, when you instantiate a t2 class object, in that instant, there simply can't be any interference
        #   and you get away with the unique object id and the object attributes belonging to the subclass rather than the superclass' instance

        #And if you're taking in a return value of a function from a superclass (called within the subclass), override it within the subclass, and within the superclass, get the return value of
        #   the superclass' function, you get the overriden function's return value
test = t2(points=200)
original = t1(points=100)  
test.printname()