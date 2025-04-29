from enum import Enum
import pygame, sys
pygame.init()

#Enum rn doesnt have a purpose, requires non null vars

class button:
    #start of button initialisation vars (our constants)
    #   you call this with "..button.typename"
    typename : str = "button"
    #here, everytime we need a new button to show up or behave a particular way by referring to it,
    #   we don't need to manually code it in, we can refer to it here,
    #   and change it on the spot here too with classmethods
    def __init__(self, name = None, top = None, bottom = None, sides = None, image = None):
        self.name = name
        self.top =  top #specifies the "top" position based on the size of the button and the spawning location
        self.bottom = bottom #specifies the "bottom" position based on the size of the button and the spawning location
        self.sides = sides #specifies the horizontal position of the button based on the size of button and its immediate location
        if image != None:
            path : str = "resources/{image}"
            self.image = pygame.image.load(path.format(image = image)) #this part is kinda the same as ("blah %s" % [var])\
            
    # def __init_subclass__(cls):
    #     return super().__init_subclass__()
    #     # put position as a subclass here, learn more soon


    class position(Enum): #everytime you wanna access the individual position of class button, you have to use position.x or y
        #this enum is in a class, so it can be accessed as one meaning to access x and y, we need to type position.x or position.y
        #can be changed with self.position.x or y
        def __init_subclass__(cls):
            return super().__init_subclass__()

    def position_vector2(self, x = None, y = None): #everytime you wanna set both at the same time, you need to use position_vector2(x, y)
        #arguments = None means that you don't have to input arguments when you call the function itself
        #call this function to get or set the position of the button
        if x == None and y == None:
            vector2 = [self.position.x, self.position.y]
            return vector2
        else:
            self.position.x = x
            self.position.y = y

    def draw(self, pos = None): #this "self" is binded to this button class
        if pos is self.position_vector2:
            if self.image != None:
                return screen.blit(self.image.convert_alpha())
            #!!NOTE:in case that the viewport isn't recognised in this script, we will call the actual function in the running script (not the transcompiled one here)
        #draw() intended to be called before every display.update() and after every fill()
        #intended to always have a position within viewport (relative to viewport)
        
        #if the arguments in draw() are different from the enum (position), update position.x and y
        else:
            print("ERROR: only accepting class method (position_vector())")