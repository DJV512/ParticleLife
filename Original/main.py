import numpy as np
import pygame
import pygame_gui
import random
import time

BLUE = (0,0,255)
RED = (255,0,0)
GREEN = (0,255,0)
PURPLE = (255,0,255)
YELLOW = (255,255,0)
CYAN = (0,255,255)
BLACK = (0,0,0)
WHITE = (255,255,255)

# Screen size parameters
screen_size_x = 1340
panel_size_x = 340
simulation_size_x = screen_size_x - panel_size_x
screen_size_y = 1000

particule_num_y = 10
button_y = 100
slider_y = 300
attraction_matrix_y = 600

particle_size = 2
wall_repel_distance = 30

# Controls frame rate
rate = 40
dt = 1/rate

#Flag to determine whether particles should die randomly
kill = False

# Set default values for changeable parameters
default_rmax = screen_size_y / 10
default_friction_half_life = 0.04
default_beta = 0.3
default_force_factor = 5

color_dict = {
        RED: 0,
        GREEN: 1,
        BLUE: 2,
        PURPLE: 3,
        YELLOW: 4,
        CYAN: 5
    }
    
def force(attraction, scaled_distance, beta):
    '''
    Determines the force applied by one particle on another based on their distance apart.
    '''
    if scaled_distance < beta:
        return 1 - (scaled_distance/beta)
    else:
        return attraction * (1 - abs(2 * scaled_distance - 1 - beta)/ (1 - beta))

def new_matrix(n):
    '''
    Generates a matrix of random attraction and repulsion for each pair of colors between -1 and 1.
    '''
    attract_matrix = np.ndarray(shape=(n,n), dtype=float)
    for i in range(n):
        for j in range(n):
            attract_matrix[i][j] = random.random()*2 - 1  
    return attract_matrix  

def make_random_particles(num_particles):
    '''
    Takes in a variable num_particles and generates that number of random particles.
    Returns lists for the positions, velocities and color, and returns the total count 
    of each color of particle.
    '''
    x_positions = []
    y_positions = []
    x_velocity = []
    y_velocity = []
    particle_color = []
    red_count = 0
    green_count = 0
    blue_count = 0
    purple_count = 0
    yellow_count = 0
    cyan_count = 0

    for _ in range(num_particles):
        x_positions.append(float(random.uniform(0,simulation_size_x)))
        y_positions.append(float(random.uniform(0,screen_size_y)))
        x_velocity.append(0)
        y_velocity.append(0)
        color = random.choice([RED, GREEN, BLUE, PURPLE, YELLOW, CYAN])
        particle_color.append(color)
        if color == RED:
            red_count += 1
        elif color == GREEN:
            green_count += 1
        elif color == BLUE:
            blue_count += 1
        elif color == PURPLE:
            purple_count += 1
        elif color == YELLOW:
            yellow_count += 1
        elif color == CYAN:
            cyan_count += 1
    
    return x_positions, y_positions, x_velocity, y_velocity, particle_color, red_count, green_count, blue_count, purple_count, yellow_count, cyan_count

def main():
    num_particles = 200
    num_colors = 6
    rmax = default_rmax
    friction_half_life = default_friction_half_life
    beta = default_beta

    #Measure actual frame_rate
    actual_rate = rate

    # Control the friction force
    force_factor = default_force_factor
    friction_factor = 0.5 ** (dt/friction_half_life)

    # Timer to ensure that something happens in the simulation every 1 second
    event_timer = 1

    # Make num_particles number of randomly positioned and colored colors, and randomize an attraction matrx for all colors
    x_positions, y_positions, x_velocity, y_velocity, particle_color, red_count, green_count, blue_count, purple_count, yellow_count, cyan_count = make_random_particles(num_particles)
    attract_matrix = new_matrix(num_colors)


    pygame.init()
    clock = pygame.time.Clock()
    
    pygame.display.set_caption("Particle Life")
    screen = pygame.display.set_mode([screen_size_x, screen_size_y])
    simulation_screen = pygame.Surface((simulation_size_x, screen_size_y))
    panel = pygame.Surface((panel_size_x,screen_size_y))
    manager = pygame_gui.UIManager((panel_size_x, screen_size_y), 'theme.json')

    credit_line = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 970), (300, 20)),
                                            text="Particle Life, by David Vance, 2024",
                                            manager=manager)
    fps_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 950), (60, 20)),
                                            text="FPS: ", manager=manager)
    fps_rate = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, 950), (60, 20)),
                                            text=f"{actual_rate:.2f}", manager=manager)

    reset_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((15, button_y), (120, 30)),
                                            text='Reset', manager=manager)
    new_matrix_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((15, button_y+40), (120, 30)),
                                            text='New Forces', manager=manager)
    slider_beta = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y + 20), (300, 20)),
                                                  start_value=beta, value_range=(0, 1),
                                                  manager=manager)
    text_beta = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((25, slider_y), (80, 20)),
                                            text=f"Beta: {slider_beta.get_current_value():.2f}",
                                            manager=manager)
    slider_friction = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y + 70), (300, 20)),
                                                  start_value=friction_half_life, value_range=(0.0001, 3),
                                                  manager=manager)
    text_friction = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, slider_y + 50), (120, 20)),
                                            text=f"Friction: {slider_friction.get_current_value():.2f}",
                                            manager=manager)
    slider_force = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y + 120), (300, 20)),
                                                  start_value=force_factor, value_range=(0, 50),
                                                  manager=manager)
    text_force = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, slider_y + 100), (100, 20)),
                                            text=f"Force: {slider_force.get_current_value():.2f}",
                                            manager=manager)
    slider_rmax = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y+170), (300, 20)),
                                                  start_value=rmax, value_range=(0, screen_size_y) ,
                                                  manager=manager)
    text_rmax = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, slider_y+150), (100, 20)),
                                            text=f"rMax: {slider_rmax.get_current_value():.2f}",
                                            manager=manager)
    red_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][0]:.2f}")
    red_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, attraction_matrix_y), (50, 20)),
                                            text="R-R", manager=manager)
    red_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][1]:.2f}")
    red_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, attraction_matrix_y), (50, 20)),
                                            text="R-G", manager=manager)
    red_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][2]:.2f}")
    red_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, attraction_matrix_y), (50, 20)),
                                            text="R-B", manager=manager)
    red_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][3]:.2f}")
    red_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, attraction_matrix_y), (50, 20)),
                                            text="R-P", manager=manager)
    red_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][4]:.2f}")
    red_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, attraction_matrix_y), (50, 20)),
                                            text="R-Y", manager=manager)
    red_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][5]:.2f}")
    red_cyan_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, attraction_matrix_y), (50, 20)),
                                            text="R-C", manager=manager)
    
    green_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][0]:.2f}")
    green_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, attraction_matrix_y+50), (50, 20)),
                                            text="G-R", manager=manager)
    green_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][1]:.2f}")
    green_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, attraction_matrix_y+50), (50, 20)),
                                            text="G-G", manager=manager)
    green_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][2]:.2f}")
    green_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, attraction_matrix_y+50), (50, 20)),
                                            text="G-B", manager=manager)
    green_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][3]:.2f}")
    green_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, attraction_matrix_y+50), (50, 20)),
                                            text="G-P", manager=manager)
    green_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][4]:.2f}")
    green_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, attraction_matrix_y+50), (50, 20)),
                                            text="G-Y", manager=manager)
    green_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][5]:.2f}")
    green_cyan_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, attraction_matrix_y+50), (50, 20)),
                                            text="G-C", manager=manager)

    blue_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][0]:.2f}")
    blue_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, attraction_matrix_y+100), (50, 20)),
                                            text="B-R", manager=manager)
    blue_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][1]:.2f}")
    blue_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, attraction_matrix_y+100), (50, 20)),
                                            text="B-G", manager=manager)
    blue_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][2]:.2f}")
    blue_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, attraction_matrix_y+100), (50, 20)),
                                            text="B-B", manager=manager)
    blue_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][3]:.2f}")
    blue_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, attraction_matrix_y+100), (50, 20)),
                                            text="B-P", manager=manager)
    blue_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][4]:.2f}")
    blue_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, attraction_matrix_y+100), (50, 20)),
                                            text="B-Y", manager=manager)
    blue_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][5]:.2f}")
    blue_cyan_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, attraction_matrix_y+100), (50, 20)),
                                            text="B-C", manager=manager)
    
    purple_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20, attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][0]:.2f}")
    purple_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, attraction_matrix_y+150), (50, 20)),
                                            text="P-R", manager=manager)
    purple_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][1]:.2f}")
    purple_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, attraction_matrix_y+150), (50, 20)),
                                            text="P-G", manager=manager)
    purple_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][2]:.2f}")
    purple_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, attraction_matrix_y+150), (50, 20)),
                                            text="P-B", manager=manager)
    purple_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][3]:.2f}")
    purple_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, attraction_matrix_y+150), (50, 20)),
                                            text="P-P", manager=manager)
    purple_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][4]:.2f}")
    purple_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, attraction_matrix_y+150), (50, 20)),
                                            text="P-Y", manager=manager)
    purple_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][5]:.2f}")
    purple_cyan_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, attraction_matrix_y+150), (50, 20)),
                                            text="P-C", manager=manager)
    
    yellow_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][0]:.2f}")
    yellow_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, attraction_matrix_y+200), (50, 20)),
                                            text="Y-R", manager=manager)
    yellow_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][1]:.2f}")
    yellow_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, attraction_matrix_y+200), (50, 20)),
                                            text="Y-G", manager=manager)
    yellow_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][2]:.2f}")
    yellow_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, attraction_matrix_y+200), (50, 20)),
                                            text="Y-B", manager=manager)
    yellow_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][3]:.2f}")
    yellow_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, attraction_matrix_y+200), (50, 20)),
                                            text="Y-P", manager=manager)
    yellow_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][4]:.2f}")
    yellow_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, attraction_matrix_y+200), (50, 20)),
                                            text="Y-Y", manager=manager)
    yellow_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][5]:.2f}")
    yellow_cyan_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, attraction_matrix_y+200), (50, 20)),
                                            text="Y-C", manager=manager)
    
    cyan_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][0]:.2f}")
    cyan_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, attraction_matrix_y+250), (50, 20)),
                                            text="C-R", manager=manager)
    cyan_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][1]:.2f}")
    cyan_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, attraction_matrix_y+250), (50, 20)),
                                            text="C-G", manager=manager)
    cyan_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][2]:.2f}")
    cyan_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, attraction_matrix_y+250), (50, 20)),
                                            text="C-B", manager=manager)
    cyan_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][3]:.2f}")
    cyan_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, attraction_matrix_y+250), (50, 20)),
                                            text="C-P", manager=manager)
    cyan_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][4]:.2f}")
    cyan_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, attraction_matrix_y+250), (50, 20)),
                                            text="C-Y", manager=manager)
    cyan_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][5]:.2f}")
    cyan_cyan_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, attraction_matrix_y+250), (50, 20)),
                                            text="C-C", manager=manager)
    
    red_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, particule_num_y), (50, 20)),
                                            text="RED", manager=manager)
    red_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{red_count}")
    green_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, particule_num_y), (50, 20)),
                                            text="GRN", manager=manager)
    green_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{green_count}")
    blue_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, particule_num_y), (50, 20)),
                                            text="BLU", manager=manager)
    blue_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{blue_count}")
    purple_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, particule_num_y), (50, 20)),
                                            text="PUR", manager=manager)
    purple_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{purple_count}")
    yellow_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, particule_num_y), (50, 20)),
                                            text="YEL", manager=manager)
    yellow_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{yellow_count}")
    cyan_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, particule_num_y), (50, 20)),
                                            text="CYN", manager=manager)
    cyan_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{cyan_count}")


    running = True
    while running:
        t0 = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle slider events
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == slider_beta:
                    beta = float(event.value)
                    text_beta.set_text(f"Beta: {beta:.2f}")
                elif event.ui_element == slider_friction:
                    friction_half_life = float(event.value)
                    friction_factor = 0.5 ** (dt/friction_half_life)
                    text_friction.set_text(f"Friction: {friction_half_life:.2f}")
                elif event.ui_element == slider_force:
                    force_factor = float(event.value)
                    text_force.set_text(f"Force: {force_factor:.2f}")
                elif event.ui_element == slider_rmax:
                    rmax = float(event.value)
                    text_rmax.set_text(f"rMax: {rmax:.2f}")
            
            # Handle text entry changes
            if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                if event.ui_element == red_red_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[0][0] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == red_green_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[0][1] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == red_blue_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[0][2] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == red_purple_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[0][3] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == red_yellow_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[0][4] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == red_cyan_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[0][5] = float(event.text)
                    except ValueError:
                        pass
                
                elif event.ui_element == green_red_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[1][0] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == green_green_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[1][1] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == green_blue_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[1][2] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == green_purple_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[1][3] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == green_yellow_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[1][4] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == green_cyan_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[1][5] = float(event.text)
                    except ValueError:
                        pass
                
                elif event.ui_element == blue_red_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[2][0] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == blue_green_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[2][1] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == blue_blue_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[2][2] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == blue_purple_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[2][3] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == blue_yellow_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[2][4] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == blue_cyan_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[2][5] = float(event.text)
                    except ValueError:
                        pass
                
                elif event.ui_element == purple_red_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[3][0] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == purple_green_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[3][1] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == purple_blue_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[3][2] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == purple_purple_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[3][3] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == purple_yellow_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[3][4] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == purple_cyan_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[3][5] = float(event.text)
                    except ValueError:
                        pass
                
                elif event.ui_element == yellow_red_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[4][0] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == yellow_green_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[4][1] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == yellow_blue_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[4][2] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == yellow_purple_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[4][3] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == yellow_yellow_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[4][4] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == yellow_cyan_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[4][5] = float(event.text)
                    except ValueError:
                        pass
                
                elif event.ui_element == cyan_red_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[5][0] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == cyan_green_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[5][1] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == cyan_blue_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[5][2] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == cyan_purple_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[5][3] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == cyan_yellow_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[5][4] = float(event.text)
                    except ValueError:
                        pass
                elif event.ui_element == cyan_cyan_entry:
                    try:
                        if float(event.text) >= -1 and float(event.text) <= 1:
                            attract_matrix[5][5] = float(event.text)
                    except ValueError:
                        pass
                
            # Handle button click
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == reset_button:
                    beta = default_beta
                    slider_beta.set_current_value(beta)
                    text_beta.set_text(f"Beta: {beta:.2f}")

                    friction_half_life = default_friction_half_life
                    friction_factor = 0.5 ** (dt/friction_half_life)
                    slider_friction.set_current_value(friction_half_life)
                    text_friction.set_text(f"Friction: {friction_half_life:.2f}")

                    force_factor = default_force_factor
                    slider_force.set_current_value(force_factor)
                    text_force.set_text(f"Force: {force_factor:.2f}")

                    rmax = default_rmax
                    slider_rmax.set_current_value(rmax)
                    text_rmax.set_text(f"rMax: {rmax:.2f}")

                    x_positions, y_positions, x_velocity, y_velocity, particle_color, red_count, green_count, blue_count, purple_count, yellow_count, cyan_count = make_random_particles(num_particles)

                elif event.ui_element == new_matrix_button:
                    attract_matrix = new_matrix(num_colors)
                    red_red_entry.set_text(f"{attract_matrix[0][0]:.2f}")
                    red_green_entry.set_text(f"{attract_matrix[0][1]:.2f}")
                    red_blue_entry.set_text(f"{attract_matrix[0][2]:.2f}")
                    red_purple_entry.set_text(f"{attract_matrix[0][3]:.2f}")
                    red_yellow_entry.set_text(f"{attract_matrix[0][4]:.2f}")
                    red_cyan_entry.set_text(f"{attract_matrix[0][5]:.2f}")

                    green_red_entry.set_text(f"{attract_matrix[1][0]:.2f}")
                    green_green_entry.set_text(f"{attract_matrix[1][1]:.2f}")
                    green_blue_entry.set_text(f"{attract_matrix[1][2]:.2f}")
                    green_purple_entry.set_text(f"{attract_matrix[1][3]:.2f}")
                    green_yellow_entry.set_text(f"{attract_matrix[1][4]:.2f}")
                    green_cyan_entry.set_text(f"{attract_matrix[1][5]:.2f}")

                    blue_red_entry.set_text(f"{attract_matrix[2][0]:.2f}")
                    blue_green_entry.set_text(f"{attract_matrix[2][1]:.2f}")
                    blue_blue_entry.set_text(f"{attract_matrix[2][2]:.2f}")
                    blue_purple_entry.set_text(f"{attract_matrix[2][3]:.2f}")
                    blue_yellow_entry.set_text(f"{attract_matrix[2][4]:.2f}")
                    blue_cyan_entry.set_text(f"{attract_matrix[2][5]:.2f}")

                    purple_red_entry.set_text(f"{attract_matrix[3][0]:.2f}")
                    purple_green_entry.set_text(f"{attract_matrix[3][1]:.2f}")
                    purple_blue_entry.set_text(f"{attract_matrix[3][2]:.2f}")
                    purple_purple_entry.set_text(f"{attract_matrix[3][3]:.2f}")
                    purple_yellow_entry.set_text(f"{attract_matrix[3][4]:.2f}")
                    purple_cyan_entry.set_text(f"{attract_matrix[3][5]:.2f}")

                    yellow_red_entry.set_text(f"{attract_matrix[4][0]:.2f}")
                    yellow_green_entry.set_text(f"{attract_matrix[4][1]:.2f}")
                    yellow_blue_entry.set_text(f"{attract_matrix[4][2]:.2f}")
                    yellow_purple_entry.set_text(f"{attract_matrix[4][3]:.2f}")
                    yellow_yellow_entry.set_text(f"{attract_matrix[4][4]:.2f}")
                    yellow_cyan_entry.set_text(f"{attract_matrix[4][5]:.2f}")

                    cyan_red_entry.set_text(f"{attract_matrix[5][0]:.2f}")
                    cyan_green_entry.set_text(f"{attract_matrix[5][1]:.2f}")
                    cyan_blue_entry.set_text(f"{attract_matrix[5][2]:.2f}")
                    cyan_purple_entry.set_text(f"{attract_matrix[5][3]:.2f}")
                    cyan_yellow_entry.set_text(f"{attract_matrix[5][4]:.2f}")
                    cyan_cyan_entry.set_text(f"{attract_matrix[5][5]:.2f}")

            manager.process_events(event)

        # Update particle color numbers
        red_count_entry.set_text(f"{red_count}")
        green_count_entry.set_text(f"{green_count}")
        blue_count_entry.set_text(f"{blue_count}")
        purple_count_entry.set_text(f"{purple_count}")
        yellow_count_entry.set_text(f"{yellow_count}")
        cyan_count_entry.set_text(f"{cyan_count}")

        # Fill the background color
        screen.fill(BLACK)
        panel.fill(BLACK)
        simulation_screen.fill(BLACK)

        pygame.draw.rect(panel, WHITE, pygame.Rect(0, 0, panel_size_x, screen_size_y), width=3)

        # Draw all particles onto the simulation_screen surface
        for i in range(num_particles):
            pygame.draw.circle(simulation_screen, particle_color[i], (x_positions[i], y_positions[i]), particle_size)
        
        # Update the control panel, draw the control panel, and paste the control panel and simulation surfaces onto the main screen
        manager.update(dt)        
        manager.draw_ui(panel)
        screen.blit(panel, (0,0))
        screen.blit(simulation_screen, (panel_size_x,0))
        pygame.display.flip()

        # Update particle velocities
        for i in range(num_particles):
            accel_x = 0
            accel_y = 0
            for j in range(num_particles):
                if i == j:
                    continue
                else:
                    rx = x_positions[i]-x_positions[j]
                    if rx <= rmax:
                        ry = y_positions[i]-y_positions[j]
                        if ry <= rmax:
                            r = (rx**2 + ry**2)**(1/2)
                            if r < rmax:
                                n = color_dict[particle_color[i]]
                                m = color_dict[particle_color[j]]
                                attraction = attract_matrix[n][m]
                                f = force(attraction, r/rmax, beta)
                                if r == 0:
                                    r = .0000001 
                                accel_x += rx/r * f
                                accel_y += ry/r * f

            # Make particles repel off the walls
            distance_to_right_wall = simulation_size_x - x_positions[i]
            distance_to_bottom_wall = screen_size_y - y_positions[i]

            if distance_to_right_wall < wall_repel_distance and distance_to_right_wall > 0:
                accel_x -= (1.5 - distance_to_right_wall/wall_repel_distance)
            elif distance_to_right_wall < 0:
                accel_x -= 1.5 * (1 - distance_to_right_wall/wall_repel_distance)

            if distance_to_bottom_wall < wall_repel_distance and distance_to_bottom_wall > 0:
                accel_y -= (1.5 - distance_to_bottom_wall/wall_repel_distance)
            elif distance_to_bottom_wall < 0:
                accel_y -= 1.5 * (1-distance_to_bottom_wall/wall_repel_distance)

            if x_positions[i] < wall_repel_distance and x_positions[i] > 0:
                accel_x += 1.5 - x_positions[i]/wall_repel_distance
            elif x_positions[i] < 0:
                accel_x += 1.5 * (1 - x_positions[i]/wall_repel_distance)

            if y_positions[i] < wall_repel_distance and y_positions[i] > 0:
                accel_y += 1.5 - y_positions[i]/wall_repel_distance
            elif y_positions[i] < 0:
                accel_y += 1.5 * (1 - y_positions[i]/wall_repel_distance)
            
            # Scaling factor for the strength of the attraction or repulsion force
            accel_x *= rmax * force_factor
            accel_y *= rmax * force_factor
            
            # Slow the particles down to account for friction
            x_velocity[i] *= friction_factor
            y_velocity[i] *= friction_factor

            # Update velocity based on x and y acceleration and the time step
            x_velocity[i] += accel_x * dt
            y_velocity[i] += accel_y * dt

        # Update particle positions based on x and y velocity and the time step
        for i in range(num_particles):
            x_positions[i] += x_velocity[i]*dt
            y_positions[i] += y_velocity[i]*dt

        # Kill off 1 particles per second
        if kill == True:
            event_timer -= dt
            if event_timer <= 0:
                num_particles -= 1
                if num_particles == 0:
                    running = False
                i = random.randint(0, num_particles - 1)
                x_positions.pop(i)
                y_positions.pop(i)
                x_velocity.pop(i)
                y_velocity.pop(i)
                match particle_color[i]:
                    case (255,0,0):
                        red_count -=1
                    case (0,255,0):
                        green_count -=1
                    case (0,0,255):
                        blue_count -=1
                    case(255,0,255):
                        purple_count -=1
                    case(255,255,0):
                        yellow_count -=1
                    case(0,255,255):
                        cyan_count -=1
                particle_color.pop(i)
                event_timer = 1

        # Controls frame rate
        clock.tick(rate)

        #Determine length of time it took this iteration of the game loop to run and calculate actual FPS
        t1 = time.time()
        actual_rate = 1/(t1-t0) 
        fps_rate.set_text(f"{actual_rate:.2f}")  

    pygame.quit()

if __name__ == "__main__":
    main()