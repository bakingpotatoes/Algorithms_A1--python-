import ctypes
from enum import Enum
import pygame, sys
import os
pygame.init()
currentscene = ["scene1"] #VERY IMPORTANT: first scene to be loaded
entities : list = [] 
displayPrompt = False


#^^^stores the names of the objects in scene (text displays, buttons, timers, everything deemed important) alongside their ID (but only whenever you ACTUALLY draw them, otherwise they can't exist)
# whenever a new scene is to be loadedthis list will be wiped and replace with the next scene's objects



time = 0 
score = 0
# stored time and score here so no one can hack it via memory heap scanning >:)
#stores the timer's value and the score to track

class button:
    #start of button initialisation vars (our constants)
    #here, everytime we need a new button to show up or behave a particular way by referring to it,
    #   we don't need to manually code it in, we can refer to it here,
    #   and change it on the spot here too with classmethods
    def __init__(self, name = None, image = None, alt_image=None, buttonType = None):
        self.name = name
        self.id = id(self) #sets the id isolated id allocation of this object
        obj = ctypes.cast(self.id, ctypes.py_object).value #getting the object's values using ctype module (it will use the object's id to retrieve its memory address and to access it)
        self.buttonType = buttonType #if not set to "toggle", we'll just ignore it and treat it as a normal button
        self.h_boundingbox = [0,0] #important for box and cursor detection
        self.v_boundingbox = [0,0]  #important for box and cursor detection
        print("<ID of {name}: {memory} & classname: {repr}".format(name=obj.name, memory=self.id, repr=self.__class__.__name__))
        if image != None:
            self.image : list = ["fodder"]
            workingDir = os.path.dirname(__file__)
            path = os.path.join(str(workingDir), str(image))
            alt_path = os.path.join(str(workingDir), str(alt_image))
            self.image.append(pygame.image.load(path)) #this part is kinda the same as ("blah %s" % [var])
            if alt_image != None:
                self.image.append(pygame.image.load(alt_path))
            else:
                if self.buttonType == "toggle":
                    self.image.append(pygame.image.load(path))
                else:
                    pass
                
        self.toggled_state = -1 #toggled_states:
                           # -1 = toggled off
                           #  1 = toggled on

    def setPosition(self, x = None, y = None):
        #this is the function version of "position", which is a callable ()
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
            if self.image[self.toggled_state] != None: #checks if the object's image (normal state) is valid, if not, should also crash tbh, youre retarded
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
                crash() #crashes if you don't have an image, actually any image

            #!!NOTE:in case that the viewport isn't recognised in this script, we will call the actual function in the running script (not the transcompiled one here)
            #draw() intended to be called before every display.update() and after every fill()
            #intended to always have a position within viewport (relative to viewport)
        else:
            crash() #unironic solution, OJWDNFOASFHOAISHDF HAHAHAHA (this happens when you fail the border checks, you get shot in the head lmao)




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
                if self.buttonType == "toggle":
                    self.toggled_state *= -1
                    self.draw(self.getPosition(), self.scale)
                else:
                    #if you have a button in the scene that is funcType = 1, during runtime, you will be prompted with a screen
                    #that will ask you what elements you want to add, change, remove, etc
                    #the reason why we do this is because we want to test text display, text input/output and checks during runtime

                    #NOTE: hopefully by the time we're done, we would have used a seperate text files dedicated for every element if it shows up again
                    #      if we do this, then everytime the game is ran again, then that button's function will be dependent on whatever that file tells it to do
                    #      if not, the prompt will keep showing up, until you select a resource file, if you wish to change the resource file, then you need to change it with a command in runtime
                    global displayPrompt
                    displayPrompt = True


                    #If the button is not toggle, we are just gonna have it change something on screen



                #this mode changes elements already in the scene and allows changing of variables (small stuff like removing certain elements, changing colors)
                return
            
            elif self.funcType == 2:
                #this is a custom function; IE: a question/answer checker, and if its the wrong answer, it'll look through all the entities currently in the scene 
                #and will check if the name of the button is the same as the question's answer, which then it will change the images of the other buttons as wrong,
                #displays the correct answer as a text display 
                pass



                #change elements in the current screen, aka in the entities list
                #once you've selected which button/element you want to change, you can change its properties for the same scene to be loaded but this time with the 
                # new element properties inside



class prompt(button): 
    #DEVELOPER NOTE: have finished making the text box itself, intend to add breaks in the text if its too long, prob like 70% of the entire width
    #                for the console itself, i'll add a fixed box that fills like 80% of the screen
    #                would really like to add scrolling as well btw
    #                
    #                instead of centering the text later on, i'll add a checker to see if youre making a question or a command prompt, and if its a 
    #                command prompt, the text will be anchored to the side starting from a fixed point, a percentage of the full width
    #                
    #                
    #                

    def __init__(self):
        screen = pygame.display.get_surface()
        width, height = screen.get_size()[0], screen.get_size()[1] 
        self.name = "prompt"
        self.fontSize = 15
        self.font = pygame.font.SysFont("couriernew", self.fontSize)
        self.text = "TESTTESTTEST TESTTESTTEST"
        self.render = self.font.render(self.text, True, (255,255,255))
        class Position:
            x = width/2
            y = height/2
        
        self.position = Position()
        self.backgroundSize = [self.font.size(self.text)[0] + 10, height]
        self.rectvalue = [self.getPosition()["box_x"],self.getPosition()["box_y"]] + self.backgroundSize

    def getPosition(self):
        x = self.position.x
        y = self.position.y

        t_x = x - self.font.size(self.text)[0] / 2
        t_y = y - self.font.size(self.text)[1] / 2
        b_x = x - (self.backgroundSize[0] / 2)
        b_y = y - (self.backgroundSize[1] / 2)
        return {
            "box_x" : b_x,
            "box_y" : b_y,
            "text_x" : t_x,
            "text_y" : t_y 
        }

    def draw(self):
        screen = pygame.display.get_surface()
        pygame.draw.rect(screen, (58, 59, 57), self.rectvalue)
        screen.blit(self.render, [self.getPosition()["text_x"], self.getPosition()["text_y"]])