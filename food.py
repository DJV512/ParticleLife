from random import random, choice
from pygame import draw

class Food:
    def __init__(self, x=None, y=None, size=None):
        '''
        Initializes a new onject of the food class.
        '''
        # Random initial position for brand new food, matching position to dead particle otherwise
        if x == None:
            self.x = random() * 1000
        else:
            self.x = x
        if y == None:
            self.y = random() * 1000
        else:
            self.y = y
        
        # Initialize the size. Random at the start of the sim, or equal to dead particle otherwise
        if size == None:
            self.size = choice([1,2,3])
        else:
            self.size = size

    def draw(self, simulation_screen):
        '''
        Given a food object, draws it on the simulation_screen surface.
        '''
        draw.circle(simulation_screen, (255,255,255), (self.x, self.y), self.size)