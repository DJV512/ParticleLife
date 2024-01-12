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
    
    def __init__(self, x=None, y=None, x_vel=None, y_vel=None, age=None, color=None, size=None, mutate=None, load=False):
        '''
        Initializes a new object of the particle class.
        '''
        # Random initial position for brand new particles, matching position to parent if offspring
        if x == None:
            self.x = random.random() * 1000
        else:
            self.x = x
        if y == None:
            self.y = random.random() * 1000
        else:
            self.y = y

        # Initial velocity = 0 for brand new particles, matching velocity if loaded from save
        if x_vel == None:
            self.x_vel = 0
        else:
            self.x_vel = x_vel
        if y_vel == None:
            self.y_vel = 0
        else:
            self.y_vel = y_vel

        # Parameter to keep track of how many "neighboring" particles a particle has
        self.neighbors = 0

        # Initialize the particle's age as 0 loops, unless specififed from loaded file
        if age == None:
            self.age = 0
        else:
            self.age = age


        # Initialize the size. Random at the start of the sim, or equal to its parent if it's a new particle, or from a loaded file
        if size == None:
            self.size = random.choice([1,2,3,4,5,6,7,8,9,10])
        else:
            self.size = size

        # Initialize the color. Random at the start of the sim, or equal to its parent if it's a new particle, or from a loaded file
        if color == None:
            self.color = random.choice([0,1,2,3,4,5])
        else:
            self.color = color

        #Keep track of the number of each color particle if these are new particles, not from a load
        if not load:
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
        Determines the euclidian distance between two particles.
        '''
        r = ry = 1000
        rx = self.x - other_particle.x
        if rx < rmax:
            ry = self.y - other_particle.y
            if ry < rmax:
                r = (rx**2 + ry**2)**(1/2)
                r -= self.size - other_particle.size
        return rx, ry, r

    @staticmethod
    def force(attraction, scaled_dist, beta):
        '''
        Determines the force applied by one particle on another based on their distance apart and attraction value.
        '''
        if scaled_dist < beta:
            return 2 - (scaled_dist/beta)
        elif scaled_dist < 1:
            return attraction * (1 - abs(2 * scaled_dist - 1 - beta)/ (1 - beta))

    def draw(self, simulation_screen):
        '''
        Given a particle object, draws it on the simulation_screen surface.
        '''
        pygame.draw.circle(simulation_screen, Particle.COLORS[self.color], (self.x, self.y), self.size)
