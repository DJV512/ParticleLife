from pygame import draw, Rect

class Wall:
    def __init__(self, x, y):
        '''
        Initializes a new piece of wall.
        '''
        self.x = x
        self.y = y
    
    def draw_wall(self, simulation_screen):
        '''
        Draws a wall piece.
        '''
        draw.rect(simulation_screen, (255,255,255), Rect(self.x, self.y, 5, 5))
