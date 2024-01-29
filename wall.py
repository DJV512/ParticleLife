from pygame import draw, Rect

class Wall:
    def __init__(self, x, y, size):
        '''
        Initializes a new piece of wall.
        '''
        self.x = x
        self.y = y
        self.size = size
    
    def draw_wall(self, simulation_screen):
        '''
        Draws a wall piece.
        '''
        draw.circle(simulation_screen, (150,75,0), (self.x, self.y), self.size)
