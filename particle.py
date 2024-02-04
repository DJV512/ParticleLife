from random import choice, random, randint, uniform
from pygame import draw

class Particle:
    COLORS=[(255,0,0), (0,255,0), (0,0,255), (255,0,255), (255,255,0), (0,255,255)]
    
    def __init__(self, x=None, y=None, x_vel=None, y_vel=None, age=None, color=None, size=None, reproduced=None, attractions=None, rmax = None, food_radar = None, history=None, mutate=False):
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
        
        # Initialize the variable to keep track of food intake.
        self.nutrition = 0

        # Initialize the variable to keep track of how many times the current particle has reproduced.
        if reproduced == None:
            self.reproduced = 0
        else:
            self.reproduced = reproduced

        # Initialize the new particle's attractions and repulsions to all other colors
        if attractions == None:
            self.attractions = [(random() * 2 - 1) for _ in range(6)]
        else:
            self.attractions = attractions

        # Initialize the new particle's attraction or repulsion from food pieces
        if food_radar == None:
            self.food_radar = uniform(-0.2, 0.2)
        else:
            self.food_radar = food_radar

        # Initialize the new particle's distance that it can "see" other particles and food
        if rmax == None:
            self.rmax = uniform(75, 125)
        else:
            self.rmax = rmax
        
        # Initialize a list called history to keep track of the historical parameters of a particle lineage
        if history == None:
            self.history=[]
        else:
            self.history=history
        
        # If this is a particle being created due to a reproduction event, randomly mutate one of it's self parameters
        if mutate:
            param_to_change = randint(0,10)
            if 0 <= param_to_change <= 5:
                self.attractions[param_to_change] += uniform(-0.05, 0.05)
            elif 6 <= param_to_change <= 8:
                self.food_radar += uniform(-0.1, 0.1)
            elif param_to_change == 9:
                self.rmax += uniform(-25, 25)
            elif param_to_change == 10:
                self.size += choice([-1,1])


    def intra_particle_dist(self, other):
        '''
        Determines the euclidian distance between the centers and surfaces of two particles.
        '''
        rx = self.x-other.x
        ry = self.y-other.y
        r_centers = (rx**2 + ry**2)**(1/2)
        r_surfaces = r_centers - self.size - other.size
        return rx, ry, r_centers, r_surfaces

    def particle_to_food_dist(self, food):
        '''
        Determines the euclidian distance between the center of a particle and a food piece.
        '''
        rx = self.x-food.x
        ry = self.y-food.y
        r_centers = (rx**2 + ry**2)**(1/2)
        return rx, ry, r_centers

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
