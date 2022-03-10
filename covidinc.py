import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import random

INFECT_RATE = 0.1
DEATH_RATE = 0.01

class State:
    def __init__(self, name, pop, density, image):
        self.name = name
        self.pop = pop
        self.healthy_pop = pop
        self.sick_pop = 0
        self.immune_pop = 0
        self.dead_pop = 0
        self.density = density
        self.image = image

    def update(self):
        if self.sick_pop < 100:
            for i in range(self.sick_pop):
                if random.random() < INFECT_RATE and self.healthy_pop > 0:
                    self.infect(1)
        else:
            infected = int(self.sick_pop * random.random() * INFECT_RATE)
            if infected > self.healthy_pop:
                infected = self.healthy_pop
            self.infect(infected)
        
        if self.sick_pop < 100:
            for i in range(self.sick_pop):
                if random.random() < DEATH_RATE and self.sick_pop > 0:
                    self.kill(1)
        else:
            dead = int(self.sick_pop * random.random() * DEATH_RATE)
            if dead > self.sick_pop:
                dead_pop = self.sick_pop
            self.kill(dead)

    def infect(self, count):
        self.sick_pop += count
        self.healthy_pop -= count

    def kill(self, count):
        self.dead_pop += count
        self.sick_pop -= count

    def get_healthy_pop(self):
        return self.pop - self.sick_pop - self.dead_pop

    def get_color(self):
        redness = int((1 - self.dead_pop / self.pop) * 255)
        brightness = int((1 - self.sick_pop / self.pop) * redness)
        return (redness, brightness, brightness)

def update_map(screen, states, border):
    screen.fill((150, 200, 255))
    for state in states:
        state.image.fill(state.get_color(), special_flags = pygame.BLEND_MIN)
        screen.blit(state.image, (0, 0))
    screen.blit(border, (0, 0))
    pygame.display.flip()

def main():
    pygame.init()
    resolution = (960, 540)
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption("COVID Inc.")
    done = False
    clock = pygame.time.Clock()

    states = []
    state_folder = "map_images/map_base"
    for line, filename in zip(open("state_data.csv").readlines(), sorted(os.listdir(state_folder))):
        name = filename[0].upper() + filename[1:-4]
        space_index = name.find('_')
        if space_index != -1:
            name = name[:space_index] + ' ' + name[space_index + 1].upper() + name[(space_index + 2):]
        data = line.split(',')
        image = pygame.transform.scale(pygame.image.load(os.path.join(state_folder, filename)), resolution)
        states.append(State(name, int(data[0]), float(data[1]), image))
    border = pygame.transform.scale(pygame.image.load("map_images/background.png"), resolution)

    first_state = states[random.randrange(50)]
    first_state.infect(1)
    print(f'A mysterious illness begins in {first_state.name}')

    tick = 0
    while not done:
        for state in states:
            state.update()

        if tick % 10 == 0:
            update_map(screen, states, border)
        tick += 1
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
    pygame.quit()

if __name__ == '__main__':
    main()