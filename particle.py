import random
import numpy as np
import pygame

def new_matrix():
    '''
    Generates a matrix of random attraction and repulsion for each pair of colors between -1 and 1.
    '''

    attract_matrix = np.ndarray(shape=(6, 6), dtype=float)
    for i in range(6):
        for j in range(6):
            attract_matrix[i][j] = random.random()*2 - 1  
    return attract_matrix

class Particle:
    red_count = 0
    green_count = 0
    blue_count = 0
    purple_count = 0
    yellow_count = 0
    cyan_count = 0
    COLORS=[(255,0,0),(0,255,0),(0,0,255),(255,0,255),(0,255,255),(255,255,0)]
    attract_matrix = new_matrix()
    
    def __init__(self):
        self.x = random.random()
        self.y = random.random()
        self.x_vel = 0
        self.y_vel = 0
        self.size = random.choice([1,2,3,4,5,6])
        self.color = random.choice([0,1,2,3,4,5])
        if self.color == 0:
            Particle.red_count += 1
        elif self.color == 1:
            Particle.green_count += 1
        elif self.color == 2:
            Particle.blue_count += 1
        elif self.color == 3:
            Particle.purple_count += 1
        elif self.color == 4:
            Particle.yellow_count += 1
        elif self.color == 5:
            Particle.cyan_count += 1

    def intra_particle_dist(self, other_particle, rmax, screen_size_y):
        '''
        Determines the distance between two particles.
        '''
        x_dist = screen_size_y*abs(self.x-other_particle.x)
        y_dist = screen_size_y*abs(self.y-other_particle.y)
        r = (x_dist**2 + y_dist**2)**(1/2)
        scaled_dist = r/rmax
        print(self, other_particle, x_dist, y_dist, r, scaled_dist)
        return x_dist, y_dist, r, scaled_dist

    def force(self, other_particle, beta, rmax, screen_size_y):
        '''
        Determines the force applied by one particle on another based on their distance apart.
        '''
        x_dist, y_dist, r, scaled_dist = self.intra_particle_dist(other_particle, rmax, screen_size_y)
        if scaled_dist < beta:
            f = 1 - (scaled_dist/beta)
        elif scaled_dist < 1:
            f =  Particle.attract_matrix[self.color][other_particle.color] * (1 - abs(2 * scaled_dist - 1 - beta)/ (1 - beta))
        else:
            f=0
        return (x_dist/r) * f, (y_dist/r) * f

    def draw(self, simulation_screen, simulation_size_x, screen_size_y):
        pygame.draw.circle(simulation_screen, Particle.COLORS[self.color], (self.x*simulation_size_x, self.y*screen_size_y), self.size)  