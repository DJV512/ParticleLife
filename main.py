from os import execl
from particle import Particle as pt
import pygame
import pygame_gui
from random import randint
from sys import executable, argv
from time import time

def main():
    BLACK = (0,0,0)
    WHITE = (255,255,255)

    # Screen size parameters
    screen_size_x = 1340
    panel_size_x = 340
    simulation_size_x = screen_size_x - panel_size_x
    screen_size_y = 1000
    wall_repel_distance = 30

    # GUI Element Top Left positions
    particule_num_y = 30
    button_y = 120
    dropdown_y = 235
    slider_y = 280
    attraction_matrix_y = 550

    # Controls frame rate
    rate = 30
    dt = 1/rate

    #Flag to determine whether particles should die randomly
    attrition = False

    # Set default values for changeable parameters
    default_rmax = screen_size_y / 10
    default_friction_half_life = 0.04
    default_beta = 0.3
    default_force_factor = 5

    default_num_particles = 500
    num_particles = default_num_particles

    # Default values
    rmax = default_rmax
    friction_half_life = default_friction_half_life
    beta = default_beta
    # Control the friction force
    force_factor = default_force_factor
    friction_factor = 0.5 ** (dt/friction_half_life)

    #Measure actual frame_rate
    actual_rate = rate
    loop_length = 1/rate

    # Timer to ensure that something happens in the simulation every 1 second
    event_timer = 1

    # Make num_particles number of randomly positioned and colored colors, and randomize an attraction matrx for all colors
    particles = [pt(simulation_size_x, screen_size_y) for _ in range(num_particles)]
    attract_matrix = pt.new_matrix()

    pygame.init()
    clock = pygame.time.Clock()
    
    pygame.display.set_caption("Particle Life")
    screen = pygame.display.set_mode([screen_size_x, screen_size_y])
    simulation_screen = pygame.Surface((simulation_size_x, screen_size_y))
    panel = pygame.Surface((panel_size_x,screen_size_y))
    manager = pygame_gui.UIManager((panel_size_x, screen_size_y), 'theme.json')

    numbers_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0,particule_num_y-20),(330,20)),
                                               text="Number of particles of each color",
                                               manager=manager)

    red_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, particule_num_y), (50, 20)),
                                            text="RED", manager=manager)
    red_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{pt.red_count}")
    green_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, particule_num_y), (50, 20)),
                                            text="GRN", manager=manager)
    green_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{pt.green_count}")
    blue_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, particule_num_y), (50, 20)),
                                            text="BLU", manager=manager)
    blue_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{pt.blue_count}")
    purple_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, particule_num_y), (50, 20)),
                                            text="PUR", manager=manager)
    purple_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{pt.purple_count}")
    yellow_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, particule_num_y), (50, 20)),
                                            text="YEL", manager=manager)
    yellow_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{pt.yellow_count}")
    cyan_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, particule_num_y), (50, 20)),
                                            text="CYN", manager=manager)
    cyan_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,particule_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{pt.cyan_count}")
    total_count_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, particule_num_y + 55), (50, 20)),
                                            text="TOTAL", manager=manager)
    total_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,particule_num_y + 50),(50,30)),
                                                        manager=manager, initial_text=f"{num_particles}")
    


    reset_sliders_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((30, button_y), (140, 30)),
                                            text='Reset Sliders', manager=manager)
    new_matrix_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((30, button_y+30), (140, 30)),
                                            text='New Forces', manager=manager)
    new_particles_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((170, button_y), (140, 30)),
                                            text='New Particles', manager=manager)
    pause_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((170, button_y+30), (140, 30)),
                                            text='Pause Sim', manager=manager)
    restart_all_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((100, button_y+60), (140, 30)),
                                            text='Restart Sim', manager=manager)
    
    attrition_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, dropdown_y), (224,25)),
                                                 text="Particles will randomly die:",
                                                 manager=manager)
    attrition_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((250, dropdown_y), (80,25)),
                                                         options_list=["False", "True"],
                                                         starting_option="False",
                                                         manager=manager)
    
    slider_beta = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y + 20), (300, 20)),
                                                         start_value=beta, value_range=(0, 1),
                                                         manager=manager)
    text_beta = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((15, slider_y), (300, 20)),
                                            text=f"Beta (how close they can get): {slider_beta.get_current_value():.2f}",
                                            manager=manager)
    slider_friction = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y + 70), (300, 20)),
                                                             start_value=friction_half_life, value_range=(0.0001, 3),
                                                             manager=manager)
    text_friction = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((23, slider_y + 50), (290, 20)),
                                                text=f"Friction (slow down over time): {slider_friction.get_current_value():.2f}",
                                                manager=manager)
    slider_force = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y + 120), (300, 20)),
                                                          start_value=force_factor, value_range=(0, 50),
                                                          manager=manager)
    text_force = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((15, slider_y + 100), (250, 20)),
                                             text=f"Force (scalar multiple): {slider_force.get_current_value():.2f}",
                                             manager=manager)
    slider_rmax = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, slider_y+170), (300, 20)),
                                                         start_value=rmax, value_range=(0, screen_size_y) ,
                                                         manager=manager)
    text_rmax = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((15, slider_y+150), (290, 20)),
                                            text=f"rMax (dist of interaction): {slider_rmax.get_current_value():.2f}",
                                            manager=manager)

    interaction_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, attraction_matrix_y-50), (330,20)),
                                                   text="Forces between colors (changeable)",
                                                   manager=manager)
    interaction_text2 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, attraction_matrix_y-30), (330,20)),
                                                   text="Negative attracts, Positive repels",
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

    credit_line = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 970), (300, 20)),
                                            text="Particle Life, by David Vance, 2024",
                                            manager=manager)
    fps_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 950), (60, 20)),
                                            text="FPS: ", manager=manager)
    fps_rate = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, 950), (60, 20)),
                                            text=f"{actual_rate:.2f}", manager=manager)


    running = True
    paused = False
    while running:
        t0 = time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle slider events
            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == slider_beta:
                    beta = float(event.value)
                    text_beta.set_text(f"Beta (how close they can get): {beta:.2f}")
                elif event.ui_element == slider_friction:
                    friction_half_life = float(event.value)
                    friction_factor = 0.5 ** (dt/friction_half_life)
                    text_friction.set_text(f"Friction (slow down over time): {friction_half_life:.2f}")
                elif event.ui_element == slider_force:
                    force_factor = float(event.value)
                    text_force.set_text(f"Force (scalar multiple): {force_factor:.2f}")
                elif event.ui_element == slider_rmax:
                    rmax = float(event.value)
                    text_rmax.set_text(f"rMax (distance of interaction): {rmax:.2f}")
            
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

            # Handle drop down selections
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == attrition_menu:
                    if event.text == "False":
                        attrition = False
                    else:
                        attrition = True

            # Handle button click
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == reset_sliders_button:
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

                elif event.ui_element == new_matrix_button:
                    attract_matrix = pt.new_matrix()
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
                
                elif event.ui_element == new_particles_button:
                    pt.red_count = 0
                    pt.green_count = 0
                    pt.blue_count = 0
                    pt.purple_count = 0
                    pt.yellow_count = 0
                    pt.cyan_count = 0
                    num_particles = default_num_particles
                    particles = [pt(simulation_size_x, screen_size_y) for _ in range(num_particles)]
                
                elif event.ui_element == pause_button:
                    paused = not paused

                elif event.ui_element == restart_all_button:
                    execl(executable, executable, *argv)

            manager.process_events(event)

        if not paused:
            # Update particle color numbers
            red_count_entry.set_text(f"{pt.red_count}")
            green_count_entry.set_text(f"{pt.green_count}")
            blue_count_entry.set_text(f"{pt.blue_count}")
            purple_count_entry.set_text(f"{pt.purple_count}")
            yellow_count_entry.set_text(f"{pt.yellow_count}")
            cyan_count_entry.set_text(f"{pt.cyan_count}")
            total_count_entry.set_text(f"{num_particles}")

            # Fill the background color
            screen.fill(BLACK)
            panel.fill(BLACK)
            simulation_screen.fill(BLACK)

            pygame.draw.rect(panel, WHITE, pygame.Rect(0, 0, panel_size_x, screen_size_y), width=3)

            # Draw all particles onto the simulation_screen surface
            for particle in particles:
                particle.draw(simulation_screen)
            
            # Update the control panel, draw the control panel, and paste the control panel and simulation surfaces onto the main screen
            manager.update(loop_length)        
            manager.draw_ui(panel)
            screen.blit(panel, (0,0))
            screen.blit(simulation_screen, (panel_size_x,0))
            pygame.display.flip()

            # Update particle velocities
            for particle1 in particles:
                accel_x = 0
                accel_y = 0
                for particle2 in particles:
                    if particle1 == particle2:
                        continue
                    else:
                        rx, ry, r = particle1.intra_particle_dist(particle2, default_rmax)
                        if r < rmax:
                            f = pt.force(attract_matrix[particle1.color][particle2.color], r/rmax, beta)
                            if r == 0:
                                r = 0.00001
                            accel_x += rx/r * f
                            accel_y += ry/r * f

                # Make particles repel off the walls
                distance_to_right_wall = simulation_size_x - particle1.x
                distance_to_bottom_wall = screen_size_y - particle1.y

                if distance_to_right_wall < wall_repel_distance and distance_to_right_wall > 0:
                    accel_x -= (1.2 - distance_to_right_wall/wall_repel_distance)
                elif distance_to_right_wall < 0:
                    accel_x -= 1.2 * (1 - distance_to_right_wall/wall_repel_distance)

                if distance_to_bottom_wall < wall_repel_distance and distance_to_bottom_wall > 0:
                    accel_y -= (1.2 - distance_to_bottom_wall/wall_repel_distance)
                elif distance_to_bottom_wall < 0:
                    accel_y -= 1.2 * (1-distance_to_bottom_wall/wall_repel_distance)

                if particle1.x < wall_repel_distance and particle1.x > 0:
                    accel_x += 1.2 - particle1.x/wall_repel_distance
                elif particle1.x < 0:
                    accel_x += 1.2 * (1 - particle1.x/wall_repel_distance)

                if particle1.y < wall_repel_distance and particle1.y > 0:
                    accel_y += 1.2 - particle1.y/wall_repel_distance
                elif particle1.y < 0:
                    accel_y += 1.2 * (1 - particle1.y/wall_repel_distance)
                
                # Scaling factor for the strength of the attraction or repulsion force
                accel_x *= rmax * force_factor
                accel_y *= rmax * force_factor
                
                # Slow the particles down to account for friction
                particle1.x_vel *= friction_factor
                particle1.y_vel *= friction_factor

                # Update velocity based on x and y acceleration and the time step
                particle1.x_vel += (accel_x * dt)
                particle1.y_vel += (accel_y * dt)

            # Update all particle positions based on x and y velocity and the time step
            for particle in particles:
                particle.x += (particle.x_vel * dt)
                particle.y += (particle.y_vel * dt)

            # Kill off 1 particles per second
            if attrition:
                event_timer -= dt
                if event_timer <= 0:
                    if num_particles == 0:
                        running = False
                    i = randint(0, num_particles - 1)
                    match particles[i].color:
                        case 0:
                            pt.red_count -=1
                        case 1:
                            pt.green_count -=1
                        case 2:
                            pt.blue_count -=1
                        case 3:
                            pt.purple_count -=1
                        case 4:
                            pt.yellow_count -=1
                        case 5:
                            pt.cyan_count -=1
                    particles.pop(i)
                    num_particles -= 1
                    event_timer = 1

        # Controls frame rate
        clock.tick(rate)

        #Determine length of time it took this iteration of the game loop to run and calculate actual FPS
        t1 = time()
        loop_length = t1-t0
        actual_rate = 1/loop_length
        fps_rate.set_text(f"{actual_rate:.2f}")  

    pygame.quit()

if __name__ == "__main__":
    main()