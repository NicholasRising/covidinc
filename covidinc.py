import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import plotly.graph_objects as go
import pygame
import random

INFECT_RATE = 0.1
DEATH_RATE = 0.01
CURE_RATE = 0.02
UNCURE_RATE = 0.001
TRAVEL_RATE = 0.00001

class State:
    def __init__(self, name, pop, image): # TODO: Store land cover (not density) so that density can be dynamic with living population
        self.name = name
        self.pop = pop
        self.healthy = pop
        self.sick = 0
        self.immune = 0
        self.dead = 0
        self.image = image
        self.history = {'Healthy': [], 'Sick': [], 'Immune': [], 'Dead': []}

    def __str__(self):
        out = f'Healthy: {int((self.healthy / self.pop) * 100)}%, '
        out += f'Sick: {int((self.sick / self.pop) * 100)}%, '
        out += f'Immune: {int((self.immune / self.pop) * 100)}%, '
        out += f'Dead: {int((self.dead / self.pop) * 100)}%'
        return out

    def update(self): # TODO: Factor density into calculations
        if self.sick < 100:
            for i in range(self.sick):
                if random.random() < INFECT_RATE and self.healthy > 0:
                    self.infect(1)
        else:
            infected = int(self.sick * random.random() * INFECT_RATE)
            if infected > self.healthy:
                infected = self.healthy
            self.infect(infected)
        
        if self.sick < 100:
            for i in range(self.sick):
                if random.random() < DEATH_RATE and self.sick > 0:
                    self.kill(1)
                if random.random() < CURE_RATE and self.sick > 0:
                    self.cure(1)
        else:
            cured = int(self.sick * random.random() * CURE_RATE)
            if cured > self.sick:
                cured = self.sick
            self.cure(cured)
            dead = int(self.sick * random.random() * DEATH_RATE)
            if dead > self.sick:
                dead = self.sick
            self.kill(dead)

        if self.immune < 100:
            for i in range(self.immune):
                if random.random() < UNCURE_RATE and self.immune > 0:
                    self.uncure(1)
        else:
            uncured = int(self.immune * random.random() * UNCURE_RATE)
            if uncured > self.immune:
                uncured = self.immune
            self.uncure(uncured)
        
        self.history['Healthy'].append(self.healthy)
        self.history['Sick'].append(self.sick)
        self.history['Immune'].append(self.immune)
        self.history['Dead'].append(self.dead)

    def infect(self, count):
        self.sick += count
        self.healthy -= count

    def cure(self, count):
        self.immune += count
        self.sick -= count

    def kill(self, count):
        self.dead += count
        self.sick -= count

    def uncure(self, count):
        self.healthy += count
        self.immune -= count

    def get_color(self):
        redness = int((1 - self.dead / self.pop) * 255)
        brightness = int((1 - self.sick / self.pop) * redness)
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
        states.append(State(name, int(data[0]), image))
    border = pygame.transform.scale(pygame.image.load("map_images/background.png"), resolution)

    first_state = states[random.randrange(50)]
    first_state.infect(100)
    print(f'A mysterious illness begins in {first_state.name}')

    tick = 0
    while not done:
        for state in states:
            state.update()
            healthy_travel = int(state.healthy * TRAVEL_RATE)
            sick_travel = int(state.sick * TRAVEL_RATE * 0.5) # Sick people are half as likely to travel
            immune_travel = int(state.sick * TRAVEL_RATE)

            state.pop -= healthy_travel + sick_travel + immune_travel
            state.healthy -= healthy_travel
            state.sick -= sick_travel
            state.immune -= immune_travel

            for i in range(healthy_travel):
                dest_index = random.randrange(49)
                if states[dest_index] == state: # Kinda defeats the purpose of travel if you stay in your home state
                    dest_index = 49
                states[dest_index].pop += 1
                states[dest_index].healthy += 1

            for i in range(sick_travel):
                dest_index = random.randrange(49)
                if states[dest_index] == state:
                    dest_index = 49
                states[dest_index].pop += 1
                states[dest_index].sick += 1

            for i in range(immune_travel):
                dest_index = random.randrange(49)
                if states[dest_index] == state:
                    dest_index = 49
                states[dest_index].pop += 1
                states[dest_index].immune += 1

        if tick % 10 == 0:
            update_map(screen, states, border)
        tick += 1
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

    pygame.quit()

    done = False
    while not done:
        request = input('State to get data on (press enter to exit): ')
        if request == '':
            done = True
        else:
            for state in states:
                if state.name.lower() == request.lower():
                    data = state.history
                    days = [i for i in range(tick)]
                    fig = go.Figure()
                    for value in data:
                        fig.add_trace(go.Scatter(x = days, y = data[value], name = value))
                    fig.update_layout(title = state.name, xaxis_title = 'Day', yaxis_title = 'Population')
                    fig.show()

if __name__ == '__main__':
    main()