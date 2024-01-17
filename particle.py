from random import choice, random
from numpy import ndarray
from pygame import draw

class Particle:
    COLORS=[(255,0,0), (0,255,0), (0,0,255), (255,0,255), (255,255,0), (0,255,255)]
    
    def __init__(self, x=None, y=None, x_vel=None, y_vel=None, age=None, color=None, size=None, mutate=None):
        '''
        Initializes a new object of the particle class.
        '''
        # Random initial position for brand new particles, matching position to parent if offspring
        if x == None:
            self.x = random() * 1000
        else:
            self.x = x
        if y == None:
            self.y = random() * 1000
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
            self.size = choice([1,2,3,4,5,6])
        else:
            self.size = size

        # Initialize the color. Random at the start of the sim, or equal to its parent if it's a new particle, or from a loaded file
        if color == None:
            self.color = choice([0,1,2,3,4,5])
        else:
            self.color = color

    @staticmethod
    def new_matrix():
        '''
        Generates a matrix of random attraction and repulsion for each pair of colors between -1 and 1.
        '''
        attract_matrix = ndarray(shape=(6, 6), dtype=float)
        for i in range(6):
            for j in range(6):
                attract_matrix[i][j] = random() * 2 - 1 
        return attract_matrix 

    def intra_particle_dist(self, other):
        '''
        Determines the euclidian distance between the centers and surfaces of two particles.
        '''
        rx = self.x-other.x
        ry = self.y-other.y
        r_centers = (rx**2 + ry**2)**(1/2)
        r_surfaces = r_centers - self.size - other.size
        return rx, ry, r_centers, r_surfaces

    @staticmethod
    def force(attraction, scaled_dist, beta):
        '''
        Determines the force applied by one particle on another based on their distance apart, beta and their attraction value.
        '''
        if scaled_dist < beta:
            return 2 - (scaled_dist/beta)
        elif scaled_dist < 1:
            return attraction * (1 - abs(2 * scaled_dist - 1 - beta)/ (1 - beta))

    def draw(self, simulation_screen):
        '''
        Given a particle object, draws it on the simulation_screen surface.
        '''
        draw.circle(simulation_screen, Particle.COLORS[self.color], (self.x, self.y), self.size)
