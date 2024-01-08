import random
import numpy as np
import pygame

class Particle:
    red_count = 0
    green_count = 0
    blue_count = 0
    purple_count = 0
    yellow_count = 0
    cyan_count = 0
    COLORS=[(255,0,0), (0,255,0), (0,0,255), (255,0,255), (255,255,0), (0,255,255)]
    
    def __init__(self, simulation_size_x, screen_size_y):
        self.x = random.random() * simulation_size_x
        self.y = random.random() * screen_size_y
        self.x_vel = 0
        self.y_vel = 0
        # self.size = 2
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

    @staticmethod
    def new_matrix():
        '''
        Generates a matrix of random attraction and repulsion for each pair of colors between -1 and 1.
        '''
        attract_matrix = np.ndarray(shape=(6, 6), dtype=float)
        for i in range(6):
            for j in range(6):
                attract_matrix[i][j] = random.random() * 2 - 1 
        return attract_matrix 

    def intra_particle_dist(self, other_particle, rmax):
        '''
        Determines the distance between two particles.
        '''
        r = ry = 1000
        rx = self.x - other_particle.x
        if rx < rmax:
            ry = self.y - other_particle.y
            if ry < rmax:
                r = (rx**2 + ry**2)**(1/2)
        return rx, ry, r

    @staticmethod
    def force(attraction, scaled_dist, beta):
        '''
        Determines the force applied by one particle on another based on their distance apart and attraction value.
        '''
        if scaled_dist < beta:
            return 1 - (scaled_dist/beta)
        elif scaled_dist < 1:
            return attraction * (1 - abs(2 * scaled_dist - 1 - beta)/ (1 - beta))

    def draw(self, simulation_screen):
        pygame.draw.circle(simulation_screen, Particle.COLORS[self.color], (self.x, self.y), self.size)
