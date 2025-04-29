import sys, pygame
from resources.classes import button as button_obj
pygame.init()

#^^^ classes initialisation (idk what type this is)

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


#test bed ----
button = button_obj(image="Untitled.png")
button.position.x = 10

button2 = button_obj(name="button2")
button2.position.x = 20

print(button.position.x, button2.position.x)

# button.position_vector2(4, 20)
# print(button.position.x)
# print(button.position_vector2())
# button.position.x += 0.5
# button.position.y -= 20
# print(button.position_vector2())
#test bed ----


screen = pygame.display.set_mode(screenRes)
while running:
    screen.fill(colour.get("red"))
    for event in pygame.event.get():
        if event.type != None:
            #if event.type is queued, then it shall have A value, if not, just null
            #ig in python, null values are just "None" lmao xd why so fickle

            #print("input detected: eventtype: {event.type}")
            pass

        if event.type == pygame.QUIT:
            #print("Closing window \nQuitting Pygame")

            #pygame is the base module, in it, contains enumerator constants that cannot be changed but can be accessed and calledback by the pygame.event module's .get() function
            #the pygame.QUIT eventtype is binded to a specific value that if it matches with the .get(eventtype=pygame."eventname"), will return a true in "if event == pygame.QUIT"
            #the .get() function returns the eventtype from the queue (a queue is the pygame engine's way of listening for mouseclicks, keystrokes, movements, etc)
            #the .type returns the assigned constant of that eventtype stored in pygame.event's module
            running = False

    pygame.display.update()
pygame.quit()
    #literally refreshes the screen