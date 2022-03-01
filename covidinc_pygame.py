import random
import pygame
import os



#recolors the pygame images for given state
def recolor(state_num,new_color):
    var = pygame.PixelArray(states[state_num])
    var.replace(state_colors[state_num], new_color)
    state_colors[state_num] = new_color
    del var

#creates the current color of the state based on it's sick and dead populations
def color_generator(state):
    redness = 255-int((int(state_values[state][2])/state_values[state][0])*255)
    darkness = 1-(state_values[state][3]/state_values[state][0])
    redness = int(redness*darkness)
    return (int(255*darkness),redness,redness)

pygame.init()
 
size = (960, 540)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Covid Inc.")

done = False
clock = pygame.time.Clock()


#states[] are the pygame image files for each state
states_folder = "map_images/map_base"
states = [pygame.transform.scale(pygame.image.load(os.path.join(states_folder,filename)), size) for filename in os.listdir(states_folder)]
border = pygame.transform.scale(pygame.image.load("map_images/background.png"), size)


#current color of each state image
state_colors = [(255,255,255) for i in range(50)]




# [total population, density, sick population, dead population, infection pool]
state_values = [[0,0,0,0,0] for i in range(50)]


#setting up state_values for each state based on the data
info = [[int(i.split(',')[0]),float(i.split(',')[1])] for i in open("state_data.csv").readlines()]
for state in range(50):
    state_values[state][0] = info[state][0]
    state_values[state][1] = info[state][1]
    state_values[state][4] = info[state][0]


infection_rate = 2
death_rate = 0.03

#infect random state
#state_values[random.randint(0,49)][2] = 1
state_values[4][2] = 1

while not done:
    screen.fill((150,200,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True



    for state in range(50):
        state_values[state][2] += 0.3*(1-state_values[state][2]/state_values[state][4])*state_values[state][2]
        #Final formula to implement: 0.3*(1/(4*% masked+1))*ln(ln(pop density))*(1-infections/infection pool)*infections
        #If pop density < 16 people/mi^2, then instead of ln(ln(d)), just use 1.

        if state_values[state][2]>state_values[state][0]:
            state_values[state][2] = state_values[state][0]

        died = state_values[state][2]*death_rate
        state_values[state][3] += died
        state_values[state][2] -= died
        state_values[state][4] -= (died + state_values[state][2])

        #5th Value Vaxxed? Subtracts from infection pool, which reduces infection rate and total possible infected.
        #Could be implemented without a 5th value.

        #Maybe for each state infected, there's a 10-20% chance another state gets an infection. Can include already infected states.

        if state_values[state][3]>state_values[state][0]:
            state_values[state][3] = state_values[state][0]
        recolor(state,color_generator(state))


    screen.blit(border,(0,0))
    for state in states:    
        screen.blit(state,(0,0))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()