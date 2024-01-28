from json import dump, load
from math import atan2, cos, sin
from operator import attrgetter
from os import execl
from particle import Particle as pt
import pygame
import pygame_gui
from random import random
from sys import executable, argv
from time import time
from wall import Wall

# Freezes everything until a button is pushed
def wait_for_button_down():
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            return
        if event.type == pygame.KEYDOWN:
            return


def main():
    BLACK = (0,0,0)
    WHITE = (255,255,255)

    # Screen size parameters
    screen_size_x = 1540
    panel_size_x = 540
    simulation_size_x = screen_size_x - panel_size_x
    screen_size_y = 1000
    particle_repel_force = 8

    # GUI Element Top Left positions
    credit_y = 10
    button_y = 50
    particle_num_y = 120
    dropdown_y = 200
    slider_y = 260
    attraction_matrix_x = 100
    attraction_matrix_y = 530
    footer_y = 950

    # Controls frame rate
    rate = 60
    dt = 1/rate

    # Flag to determine whether evolution is on or off
    evolution = True

    # Distance to neighbors, for evolution purposes
    neighbor_dist = 25

    # Number of neighbors within neighbor_dist that triggers reproduction
    neighbor_num = 10

    # Number of loops bewteen evolution steps
    life_expect_loops = 750

    # Counters for the total number of loops and total time
    total_num_loops = 0
    ttotal_min = 0
    ttotal_sec = 0
    loaded_clock = False
    total_time = 0

    # Set default values for changeable parameters
    default_rmax = screen_size_y / 10
    default_friction_half_life = 0.04
    default_beta = 0.1
    default_force_factor = 5

    # Starting number of particle defaults
    default_num_particles = 300
    num_particles = default_num_particles
    oldest_particle = 0
    red_count = 0
    green_count = 0
    blue_count = 0
    purple_count = 0
    yellow_count = 0
    cyan_count = 0

    # Default values
    rmax = default_rmax
    friction_half_life = default_friction_half_life
    beta = default_beta
    # Control the friction force
    force_factor = default_force_factor
    friction_factor = 0.5 ** (dt/friction_half_life)

    # Variables to measure the actual frame_rate
    actual_rate = rate
    loop_length = 1/rate

    # Save and load flags
    SAVE = False
    LOAD = False

    # Mouse parameters
    mouse_mode = "grab"
    mouse_radius = 50
    grab = False
    add_particles = False
    remove_particles = False
    draw_wall = False
    remove_wall = False
    walls = []
    num_walls = 0

    # Make num_particles number of randomly positioned and colored parrticles
    particles = [pt() for _ in range(num_particles)]

    # Randomize an attraction matrix for all colors
    attract_matrix = pt.new_matrix()

    # Initialize the game and set the clock
    pygame.init()
    clock = pygame.time.Clock()
    
    # Window size and options
    pygame.display.set_caption("Particle Life")
    screen = pygame.display.set_mode([screen_size_x, screen_size_y])
    simulation_screen = pygame.Surface((simulation_size_x, screen_size_y))
    panel = pygame.Surface((panel_size_x, screen_size_y))
    manager = pygame_gui.UIManager((panel_size_x, screen_size_y), 'theme.json')

    # Control panel text and values
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, credit_y), (540, 30)),
                                text="Particle Life, by David Vance, 2024",
                                manager=manager)
    
    pause_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((15, button_y), (120, 30)),
                                            text='Pause Sim', manager=manager)
    restart_all_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((145, button_y), (120, 30)),
                                            text='Restart Sim', manager=manager)
    save_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((275, button_y), (120, 30)),
                                            text='Save Sim', manager=manager)
    load_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((405, button_y), (120, 30)),
                                            text='Load Sim', manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0,particle_num_y-20),(330,20)),
                                               text="Number of particles of each color",
                                               manager=manager)

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, particle_num_y), (50, 20)),
                                            text="RED", manager=manager)
    red_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,particle_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{red_count}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, particle_num_y), (50, 20)),
                                            text="GRN", manager=manager)
    green_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,particle_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{green_count}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, particle_num_y), (50, 20)),
                                            text="BLU", manager=manager)
    blue_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,particle_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{blue_count}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, particle_num_y), (50, 20)),
                                            text="PUR", manager=manager)
    purple_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,particle_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{purple_count}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, particle_num_y), (50, 20)),
                                            text="YEL", manager=manager)
    yellow_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,particle_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{yellow_count}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, particle_num_y), (50, 20)),
                                            text="CYN", manager=manager)
    cyan_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((270,particle_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{cyan_count}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((340, particle_num_y), (50, 20)),
                                            text="TOTAL", manager=manager)
    total_count_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((340,particle_num_y + 20),(50,30)),
                                                        manager=manager, initial_text=f"{num_particles}")
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((400, particle_num_y), (150,20)),
                                                 text="Evolution", manager=manager)
    evolution_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((435, particle_num_y+20), (80,30)),
                                                         options_list=["On", "Off"], starting_option="On",
                                                         manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((25, dropdown_y), (100,30)),
                                                 text="Mouse Mode", manager=manager)
    mouse_mode_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((125, dropdown_y), (200,30)),
                                                         options_list=["Grab Particles", "Add Particles", "Remove Particles", "Add Wall", "Remove Wall"], starting_option="Grab Particles",
                                                         manager=manager)
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((355, dropdown_y), (100,30)),
                                                 text="Mouse Size", manager=manager)
    mouse_radius_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((455, dropdown_y), (50,30)),
                                                         options_list=["10","30","50","70","90"], starting_option="50",
                                                         manager=manager)
    
    text_beta = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, slider_y), (300, 20)),
                                            text=f"Beta (how close they can get): {default_beta:.2f}",
                                            manager=manager)
    slider_beta = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((35, slider_y + 20), (300, 20)),
                                                         start_value=beta, value_range=(0, 1), manager=manager)

    text_friction = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((38, slider_y + 50), (290, 20)),
                                                text=f"Friction (slow down over time): {default_friction_half_life:.2f}",
                                                manager=manager)
    slider_friction = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((35, slider_y + 70), (300, 20)),
                                                             start_value=friction_half_life, value_range=(0.0001, 3),
                                                             manager=manager)
    
    text_force = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, slider_y + 100), (250, 20)),
                                             text=f"Force (scalar multiple): {default_force_factor:.2f}",
                                             manager=manager)
    slider_force = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((35, slider_y + 120), (300, 20)),
                                                          start_value=force_factor, value_range=(0, 50),
                                                          manager=manager)
    
    text_rmax = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, slider_y+150), (290, 20)),
                                            text=f"rMax (dist of interaction): {default_rmax:.2f}",
                                            manager=manager)
    slider_rmax = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((35, slider_y+170), (300, 20)),
                                                         start_value=rmax, value_range=(0, screen_size_y) ,
                                                         manager=manager)
    
    reset_sliders_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((355, slider_y+40), (140, 30)),
                                            text='Reset Sliders', manager=manager)
    new_particles_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((355, slider_y+90), (140, 30)),
                                            text='New Particles', manager=manager)
    new_matrix_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((355, slider_y+140), (140, 30)),
                                            text='New Forces', manager=manager)

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x, attraction_matrix_y-50), (330,20)),
                                                   text="Forces between colors (changeable)", manager=manager)
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x, attraction_matrix_y-30), (330,20)),
                                                   text="Negative attracts, Positive repels", manager=manager)

    red_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+20,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][0]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+20, attraction_matrix_y), (50, 20)),
                                            text="R-R", manager=manager)
    red_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+70,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][1]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+70, attraction_matrix_y), (50, 20)),
                                            text="R-G", manager=manager)
    red_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+120,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][2]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+120, attraction_matrix_y), (50, 20)),
                                            text="R-B", manager=manager)
    red_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+170,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][3]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+170, attraction_matrix_y), (50, 20)),
                                            text="R-P", manager=manager)
    red_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+220,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][4]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+220, attraction_matrix_y), (50, 20)),
                                            text="R-Y", manager=manager)
    red_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+270,attraction_matrix_y+20),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][5]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+270, attraction_matrix_y), (50, 20)),
                                            text="R-C", manager=manager)
    
    green_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+20,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][0]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+20, attraction_matrix_y+50), (50, 20)),
                                            text="G-R", manager=manager)
    green_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+70,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][1]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+70, attraction_matrix_y+50), (50, 20)),
                                            text="G-G", manager=manager)
    green_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+120,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][2]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+120, attraction_matrix_y+50), (50, 20)),
                                            text="G-B", manager=manager)
    green_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+170,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][3]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+170, attraction_matrix_y+50), (50, 20)),
                                            text="G-P", manager=manager)
    green_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+220,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][4]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+220, attraction_matrix_y+50), (50, 20)),
                                            text="G-Y", manager=manager)
    green_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+270,attraction_matrix_y+70),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][5]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+270, attraction_matrix_y+50), (50, 20)),
                                            text="G-C", manager=manager)

    blue_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+20,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][0]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+20, attraction_matrix_y+100), (50, 20)),
                                            text="B-R", manager=manager)
    blue_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+70,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][1]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+70, attraction_matrix_y+100), (50, 20)),
                                            text="B-G", manager=manager)
    blue_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+120,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][2]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+120, attraction_matrix_y+100), (50, 20)),
                                            text="B-B", manager=manager)
    blue_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+170,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][3]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+170, attraction_matrix_y+100), (50, 20)),
                                            text="B-P", manager=manager)
    blue_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+220,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][4]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+220, attraction_matrix_y+100), (50, 20)),
                                            text="B-Y", manager=manager)
    blue_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+270,attraction_matrix_y+120),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][5]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+270, attraction_matrix_y+100), (50, 20)),
                                            text="B-C", manager=manager)
    
    purple_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+20, attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][0]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+20, attraction_matrix_y+150), (50, 20)),
                                            text="P-R", manager=manager)
    purple_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+70,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][1]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+70, attraction_matrix_y+150), (50, 20)),
                                            text="P-G", manager=manager)
    purple_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+120,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][2]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+120, attraction_matrix_y+150), (50, 20)),
                                            text="P-B", manager=manager)
    purple_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+170,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][3]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+170, attraction_matrix_y+150), (50, 20)),
                                            text="P-P", manager=manager)
    purple_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+220,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][4]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+220, attraction_matrix_y+150), (50, 20)),
                                            text="P-Y", manager=manager)
    purple_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+270,attraction_matrix_y+170),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][5]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+270, attraction_matrix_y+150), (50, 20)),
                                            text="P-C", manager=manager)
    
    yellow_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+20,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][0]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+20, attraction_matrix_y+200), (50, 20)),
                                            text="Y-R", manager=manager)
    yellow_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+70,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][1]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+70, attraction_matrix_y+200), (50, 20)),
                                            text="Y-G", manager=manager)
    yellow_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+120,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][2]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+120, attraction_matrix_y+200), (50, 20)),
                                            text="Y-B", manager=manager)
    yellow_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+170,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][3]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+170, attraction_matrix_y+200), (50, 20)),
                                            text="Y-P", manager=manager)
    yellow_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+220,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][4]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+220, attraction_matrix_y+200), (50, 20)),
                                            text="Y-Y", manager=manager)
    yellow_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+270,attraction_matrix_y+220),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][5]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+270, attraction_matrix_y+200), (50, 20)),
                                            text="Y-C", manager=manager)
    
    cyan_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+20,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][0]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+20, attraction_matrix_y+250), (50, 20)),
                                            text="C-R", manager=manager)
    cyan_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+70,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][1]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+70, attraction_matrix_y+250), (50, 20)),
                                            text="C-G", manager=manager)
    cyan_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+120,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][2]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+120, attraction_matrix_y+250), (50, 20)),
                                            text="C-B", manager=manager)
    cyan_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+170,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][3]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+170, attraction_matrix_y+250), (50, 20)),
                                            text="C-P", manager=manager)
    cyan_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+220,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][4]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+220, attraction_matrix_y+250), (50, 20)),
                                            text="C-Y", manager=manager)
    cyan_cyan_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((attraction_matrix_x+270,attraction_matrix_y+270),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[5][5]:.2f}")
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((attraction_matrix_x+270, attraction_matrix_y+250), (50, 20)),
                                                text="C-C", manager=manager)


    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, footer_y), (120, 20)),
                                text="Total Time: ", manager=manager)
    total_time_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((90, footer_y), (60, 20)),
                                           text=f"{f"{ttotal_min}:{ttotal_sec:02d}"}", manager=manager)

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((163, footer_y), (158, 20)),
                                text="Oldest: ", manager=manager)
    oldest_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, footer_y), (60, 20)),
                                           text=f"{oldest_particle}", manager=manager)

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, footer_y+20), (60, 20)),
                                text="FPS: ", manager=manager)
    fps_rate = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((35, footer_y+20), (60, 20)),
                                           text=f"{actual_rate:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, footer_y+20), (105, 20)),
                                text="Total Loops: ", manager=manager)
    loops_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((270, footer_y+20), (60, 20)),
                                             text=f"{total_num_loops}", manager=manager)
    


    # Start the game loop
    running = True
    paused = False
    tstart = time()
    while running:
        t0 = time()

        # Controls maximum frame rate
        clock.tick(rate)

        # Cycle through all user initiated events that happen during the simulation
        for event in pygame.event.get():

            # Handle ending the simulation
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

                # Turn evolution on or off
                if event.ui_element == evolution_menu:
                    if event.text == "Off":
                        evolution = False
                    else:
                        evolution = True
                
                # Handles changes in mouse mode
                elif event.ui_element == mouse_mode_menu:
                    if event.text == "Grab Particles":
                        mouse_mode = "grab"
                    elif event.text == "Add Particles":
                        mouse_mode = "add"
                    elif event.text == "Remove Particles":
                        mouse_mode = "remove"
                    elif event.text == "Add Wall":
                        mouse_mode = "wall"
                    elif event.text == "Remove Wall":
                        mouse_mode = "remove_wall"
                
                # Handles changes in mouse size
                elif event.ui_element == mouse_radius_menu:
                    if event.text == "10":
                        mouse_radius = 10
                    elif event.text == "30":
                        mouse_radius = 30
                    elif event.text == "50":
                        mouse_radius = 50
                    elif event.text == "70":
                        mouse_radius = 70
                    elif event.text == "90":
                        mouse_radius = 90
            
            #Handle mouse clicks
            elif event.type == pygame.MOUSEBUTTONDOWN:

                # When grab is selected, mouse clicking grabs all particles in mouse radius
                if mouse_mode == "grab" and not grab and not paused:
                    paused = True
                    grab = True
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    grabbed = []
                    for particle in particles:
                        r = ((particle.x-m_x)**2 + (particle.y-m_y)**2)**(1/2)
                        if r < mouse_radius:
                            grabbed.append(particle)
                    m_x_current = m_x
                    m_y_current = m_y

                # When add is selected, mouse clicking makes a new random particle
                elif mouse_mode == "add":
                    add_particles = True
                    m_x, m_y = pygame.mouse.get_pos()
                    particles.append(pt(x=m_x-panel_size_x, y=m_y))
                    num_particles += 1
                
                # When remove is selected, mouse clicking removes all particles in the mouse radius
                elif mouse_mode == "remove":
                    remove_particles = True
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    for particle in particles.copy():
                        r = ((particle.x-m_x)**2 + (particle.y-m_y)**2)**(1/2)
                        if r < mouse_radius:
                            particles.remove(particle)
                            num_particles -= 1

                # When wall is selected, mouse clicking will draw wall
                elif mouse_mode == "wall":
                    draw_wall = True
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    walls.append(Wall(m_x, m_y, mouse_radius))
                    num_walls += 1
                
                # When remove wall is selected, mouse clicking will remove wall
                elif mouse_mode == "remove_wall":
                    remove_wall = True
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    for wall in walls.copy():
                        r = ((wall.x-m_x)**2 + (wall.y-m_y)**2)**(1/2)
                        if r < mouse_radius:
                            walls.remove(wall)
                            num_walls -= 1

                    
            # Handle mouse motion 
            elif event.type == pygame.MOUSEMOTION:

                # Mouse dragging moves all particles in mouse radius
                if grab:
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    change_x = m_x - m_x_current
                    change_y = m_y - m_y_current
                    for particle in grabbed:
                        particle.x += change_x
                        particle.y += change_y
                    m_x_current = m_x
                    m_y_current = m_y

                # Mouse dragging continues removing particles
                elif remove_particles:
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    for particle in particles.copy():
                        r = ((particle.x-m_x)**2 + (particle.y-m_y)**2)**(1/2)
                        if r < mouse_radius:
                            particles.remove(particle)
                            num_particles -= 1

                # Mouse dragging continues to add new particles
                elif add_particles:
                    m_x, m_y = pygame.mouse.get_pos()
                    particles.append(pt(x=m_x-panel_size_x, y=m_y))
                    num_particles += 1
                
                # Mouse dragging draws more wall pieces
                elif draw_wall:
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    walls.append(Wall(m_x, m_y, mouse_radius))
                    num_walls += 1

                # Mouse dragging removes more wall pieces
                elif remove_wall:
                    m_x, m_y = pygame.mouse.get_pos()
                    m_x -= panel_size_x
                    for wall in walls.copy():
                        r = ((wall.x-m_x)**2 + (wall.y-m_y)**2)**(1/2)
                        if r < mouse_radius:
                            walls.remove(wall)
                            num_walls -= 1

            # Handle releasing mouse button
            elif event.type == pygame.MOUSEBUTTONUP:
            
                # Letting go of mouse button releases all grabbed particles
                if grab:
                    grabbed = []
                    grab = False
                    paused = False
                
                # Letting go stops drawing particles
                elif add_particles:
                    add_particles = False
                
                # Letting go stops removing particles
                elif remove_particles:
                    remove_particles = False
                
                # Letting go of mouse stops drawing wall
                elif draw_wall:
                    draw_wall = False
                
                # Letting go of mouse stops removing wall
                elif remove_wall:
                    remove_wall = False


            # Handle button click
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == reset_sliders_button:
                    beta = default_beta
                    slider_beta.set_current_value(beta)
                    text_beta.set_text(f"Beta (how close they can get): {beta:.2f}")

                    friction_half_life = default_friction_half_life
                    friction_factor = 0.5 ** (dt/friction_half_life)
                    slider_friction.set_current_value(friction_half_life)
                    text_friction.set_text(f"Friction (slow down over time): {friction_half_life:.2f}")

                    force_factor = default_force_factor
                    slider_force.set_current_value(force_factor)
                    text_force.set_text(f"Force (scalar multiple): {force_factor:.2f}")

                    rmax = default_rmax
                    slider_rmax.set_current_value(rmax)
                    text_rmax.set_text(f"rMax (distance of interaction): {rmax:.2f}")

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
                    red_count = 0
                    green_count = 0
                    blue_count = 0
                    purple_count = 0
                    yellow_count = 0
                    cyan_count = 0
                    num_particles = default_num_particles
                    particles = [pt() for _ in range(num_particles)]
                
                elif event.ui_element == pause_button:
                    paused = not paused

                elif event.ui_element == restart_all_button:
                    execl(executable, executable, *argv)

                elif event.ui_element == save_button:
                    paused=True
                    game_settings = {
                        "parameters": {
                            "wall_repel_distance": edge_repel_distance,
                            "wall_repel_strength": wall_repel_strength,
                            "particle_repel_force": particle_repel_force,
                            "rate": rate,
                            "evolution": evolution,
                            "neighbor_dist": neighbor_dist,
                            "neighbor_num": neighbor_num,
                            "life_expect_loops": life_expect_loops,
                            "rmax": rmax,
                            "friction_half_life": friction_half_life,
                            "beta": beta,
                            "force_factor": force_factor,
                            "num_particles": num_particles,
                            "ttotal_min": ttotal_min,
                            "ttotal_sec": ttotal_sec,
                            "total_num_loops": total_num_loops,
                            "oldest_particle": oldest_particle
                        },

                        "particle_data": [(part.x, part.y, part.x_vel, part.y_vel, part.age, part.size, part.color) for part in particles],

                        "wall_data": [(wall.x, wall.y) for wall in walls],

                        "attract_matrix": {
                            "red_red": attract_matrix[0][0],
                            "red_green": attract_matrix[0][1],
                            "red_blue": attract_matrix[0][2],
                            "red_purple": attract_matrix[0][3],
                            "red_yellow": attract_matrix[0][4],
                            "red_cyan": attract_matrix[0][5],
                            "green_red": attract_matrix[1][0],
                            "green_green": attract_matrix[1][1],
                            "green_blue": attract_matrix[1][2],
                            "green_purple": attract_matrix[1][3],
                            "green_yellow": attract_matrix[1][4],
                            "green_cyan": attract_matrix[1][5],
                            "blue_red": attract_matrix[2][0],
                            "blue_green": attract_matrix[2][1],
                            "blue_blue": attract_matrix[2][2],
                            "blue_purple": attract_matrix[2][3],
                            "blue_yellow": attract_matrix[2][4],
                            "blue_cyan": attract_matrix[2][5],
                            "purple_red": attract_matrix[3][0],
                            "purple_green": attract_matrix[3][1],
                            "purple_blue": attract_matrix[3][2],
                            "purple_purple": attract_matrix[3][3],
                            "purple_yellow": attract_matrix[3][4],
                            "purple_cyan": attract_matrix[3][5],
                            "yellow_red": attract_matrix[4][0],
                            "yellow_green": attract_matrix[4][1],
                            "yellow_blue": attract_matrix[4][2],
                            "yellow_purple": attract_matrix[4][3],
                            "yellow_yellow": attract_matrix[4][4],
                            "yellow_cyan": attract_matrix[4][5],
                            "cyan_red": attract_matrix[5][0],
                            "cyan_green": attract_matrix[5][1],
                            "cyan_blue": attract_matrix[5][2],
                            "cyan_purple": attract_matrix[5][3],
                            "cyan_yellow": attract_matrix[5][4],
                            "cyan_cyan": attract_matrix[5][5],
                        },
                    }
                    if not loaded_clock:
                        game_settings["parameters"]["total_time"] =  time()-tstart
                    else:
                        game_settings["parameters"]["total_time"] =  total_time + (time()-load_time)

                    dialog = pygame_gui.windows.UIFileDialog(pygame.Rect((0,500),(350,300)),
                                                             window_title="Save Sim", 
                                                             initial_file_path="Interesting_Forces/",
                                                             manager=manager)
                    dialog.show()
                    SAVE = True

                elif event.ui_element == load_button:
                    paused=True
                    dialog = pygame_gui.windows.UIFileDialog(pygame.Rect((0,350),(350,300)),
                                                             window_title="Load Sim", 
                                                             initial_file_path="Interesting_Forces/",
                                                             manager=manager)
                    dialog.show()
                    LOAD = True

                       
            elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                if SAVE:
                    file = event.text
                    with open(f"{file}_save.json", "w") as f:
                        dump(game_settings, f)
                    font = pygame.font.Font(None, 36)
                    text = font.render("Game saved! Press any key to continue.", True, (0,0,0))
                    text_rect = text.get_rect(center=(850,500))
                    pygame.draw.rect(screen, (255,255,255), ((text_rect.x, text_rect.y), (480, 30)))
                    screen.blit(text, text_rect)
                    pygame.display.flip()
                    wait_for_button_down()
                    SAVE = False
                    paused = False
                elif LOAD:
                    file = event.text
                    with open(f"{file}", "r") as f:
                        data = load(f)

                    edge_repel_distance = data["parameters"]["wall_repel_distance"]
                    wall_repel_strength = data["parameters"]["wall_repel_strength"]
                    particle_repel_force = data["parameters"]["particle_repel_force"]
                    rate = data["parameters"]["rate"]
                    evolution = data["parameters"]["evolution"]
                    neighbor_dist = data["parameters"]["neighbor_dist"]
                    neighbor_num = data["parameters"]["neighbor_num"]
                    life_expect_loops = data["parameters"]["life_expect_loops"]
                    rmax = data["parameters"]["rmax"]
                    friction_half_life = data["parameters"]["friction_half_life"]
                    beta = data["parameters"]["beta"]
                    force_factor = data["parameters"]["force_factor"]
                    num_particles = data["parameters"]["num_particles"]
                    ttotal_min = data["parameters"]["ttotal_min"]
                    ttotal_sec = data["parameters"]["ttotal_sec"]
                    total_time = data["parameters"]["total_time"]
                    total_num_loops = data["parameters"]["total_num_loops"]
                    oldest_particle = data["parameters"]["oldest_particle"]

                    slider_beta.set_current_value(beta)
                    text_beta.set_text(f"Beta (how close they can get): {beta:.2f}") 
                    slider_friction.set_current_value(friction_half_life)
                    text_friction.set_text(f"Friction (slow down over time): {friction_half_life:.2f}")
                    slider_force.set_current_value(force_factor)
                    text_force.set_text(f"Force (scalar multiple): {force_factor:.2f}")
                    slider_rmax.set_current_value(rmax)
                    text_rmax.set_text(f"rMax (distance of interaction): {rmax:.2f}")

                    total_time_text.set_text(f"{ttotal_min}:{ttotal_sec:02d}")
                    oldest_text.set_text(f"{oldest_particle}")
                    loops_text.set_text(f"{total_num_loops}")

                    particles = []
                    particles = [pt(x=data["particle_data"][i][0], 
                                    y=data["particle_data"][i][1], 
                                    x_vel=data["particle_data"][i][2],
                                    y_vel=data["particle_data"][i][3],
                                    age=data["particle_data"][i][4],
                                    size=data["particle_data"][i][5],
                                    color=data["particle_data"][i][6],
                                    ) 
                                for i in range(num_particles)]
                    
                    walls = []
                    walls = [Wall(x=data["wall_data"][i][0],
                                  y=data["wall_data"][i][1],
                                  )
                            for i in range(num_walls)]
                
                    attract_matrix[0][0] = data["attract_matrix"]["red_red"]
                    attract_matrix[0][1] = data["attract_matrix"]["red_green"]
                    attract_matrix[0][2] = data["attract_matrix"]["red_blue"]
                    attract_matrix[0][3] = data["attract_matrix"]["red_purple"]
                    attract_matrix[0][4] = data["attract_matrix"]["red_yellow"]
                    attract_matrix[0][5] = data["attract_matrix"]["red_cyan"]
                    attract_matrix[1][0] = data["attract_matrix"]["green_red"]
                    attract_matrix[1][1] = data["attract_matrix"]["green_green"]
                    attract_matrix[1][2] = data["attract_matrix"]["green_blue"]
                    attract_matrix[1][3] = data["attract_matrix"]["green_purple"]
                    attract_matrix[1][4] = data["attract_matrix"]["green_yellow"]
                    attract_matrix[1][5] = data["attract_matrix"]["green_cyan"]
                    attract_matrix[2][0] = data["attract_matrix"]["blue_red"]
                    attract_matrix[2][1] = data["attract_matrix"]["blue_green"]
                    attract_matrix[2][2] = data["attract_matrix"]["blue_blue"]
                    attract_matrix[2][3] = data["attract_matrix"]["blue_purple"] 
                    attract_matrix[2][4] = data["attract_matrix"]["blue_yellow"]
                    attract_matrix[2][5] = data["attract_matrix"]["blue_cyan"]
                    attract_matrix[3][0] = data["attract_matrix"]["purple_red"]
                    attract_matrix[3][1] = data["attract_matrix"]["purple_green"]
                    attract_matrix[3][2] = data["attract_matrix"]["purple_blue"]
                    attract_matrix[3][3] = data["attract_matrix"]["purple_purple"]
                    attract_matrix[3][4] = data["attract_matrix"]["purple_yellow"]
                    attract_matrix[3][5] = data["attract_matrix"]["purple_cyan"]
                    attract_matrix[4][0] = data["attract_matrix"]["yellow_red"]
                    attract_matrix[4][1] = data["attract_matrix"]["yellow_green"]
                    attract_matrix[4][2] = data["attract_matrix"]["yellow_blue"]
                    attract_matrix[4][3] = data["attract_matrix"]["yellow_purple"]
                    attract_matrix[4][4] = data["attract_matrix"]["yellow_yellow"]
                    attract_matrix[4][5] = data["attract_matrix"]["yellow_cyan"]
                    attract_matrix[5][0] = data["attract_matrix"]["cyan_red"]
                    attract_matrix[5][1] = data["attract_matrix"]["cyan_green"]
                    attract_matrix[5][2] = data["attract_matrix"]["cyan_blue"]
                    attract_matrix[5][3] = data["attract_matrix"]["cyan_purple"]
                    attract_matrix[5][4] = data["attract_matrix"]["cyan_yellow"]
                    attract_matrix[5][5] = data["attract_matrix"]["cyan_cyan"]
                    
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

                    loaded_clock = True
                    load_time = time()
                    LOAD = False
                    paused = False

            # Removes already processed events from the list of events
            manager.process_events(event)
        
        # Fill the background color
        screen.fill(BLACK)
        panel.fill(BLACK)
        simulation_screen.fill(BLACK)

        # Draws a white rectangle under the control panel so that it appears to have a white border
        pygame.draw.rect(panel, WHITE, pygame.Rect(0, 0, panel_size_x, screen_size_y), width=3)

        # Draw all particles onto the simulation_screen surface
        for particle in particles:
            particle.draw(simulation_screen)

        # Where the magic happens
        if not paused:
            # Update particle velocities
            oldest_particle = 0
            many_neighbors = []
            old_particles = []
            red_count = 0
            green_count = 0
            blue_count = 0
            purple_count = 0
            yellow_count = 0
            cyan_count = 0

            # Determine which particle is the oldest
            oldest_particle = max(particles, key=attrgetter("age"))

            # Cycle through all particles
            for particle1 in particles:

                # Check to see if particle1 is past its life expectancy
                if particle1.age > life_expect_loops:
                    old_particles.append(particle1)
                
                # Keeps track of the number of each color of particle
                match particle1.color:
                    case 0:
                        red_count += 1
                    case 1:
                        green_count += 1
                    case 2:
                        blue_count += 1
                    case 3:
                        purple_count += 1
                    case 4:
                        yellow_count += 1
                    case 5:
                        cyan_count += 1
                accel_x = 0
                accel_y = 0
                particle1.neighbors = 0

                # Determine how much force every other particle applies to particle1
                for particle2 in particles:
                    if particle1 == particle2:
                        continue
                    else:
                        rx, ry, r_centers, r_surfaces = particle1.intra_particle_dist(particle2)
                        if r_centers < neighbor_dist:
                            particle1.neighbors += 1
                        if r_centers > rmax:
                            continue
                        elif r_centers <= rmax and r_surfaces > 0:
                            f = pt.force(attract_matrix[particle1.color][particle2.color], r_centers/rmax, beta) * particle2.size
                            theta = atan2(ry, rx)
                            accel_x += cos(theta) * f
                            accel_y += sin(theta) * f
                        elif r_surfaces < 0:
                            theta = atan2(ry, rx)
                            accel_x += cos(theta) * particle_repel_force
                            accel_y += sin(theta) * particle_repel_force

                # If particle1 has more than neighbor_sum neighbors, keep track of it (for evolution)
                if particle1.neighbors > neighbor_num:
                    many_neighbors.append(particle1)
                
                # Increment particle1's age
                particle1.age += 1

                # Scaling factor for the strength of the attraction or repulsion force
                accel_x *= rmax * force_factor
                accel_y *= rmax * force_factor
                
                # Slow particle1 down to account for friction
                particle1.x_vel *= friction_factor
                particle1.y_vel *= friction_factor

                # Update particle1 velocity based on x and y acceleration and the time step
                particle1.x_vel += (accel_x * dt)
                particle1.y_vel += (accel_y * dt)

            # Update all particle positions based on x and y velocity and the time step
            # If the particle tries to go off the screen, don't let it.
            for particle in particles:
                particle.x += (particle.x_vel * dt)
                if particle.x < 0:
                    particle.x = 0
                elif particle.x > simulation_size_x:
                    particle.x = simulation_size_x
                particle.y += (particle.y_vel * dt)
                if particle.y < 0:
                    particle.y = 0
                elif particle.y > screen_size_y:
                    particle.y = screen_size_y
            
            # Controls evolution if evolution is set to true
            if evolution:

                # If the total number of loops is a multiple of the life expectancy, do an evolution step
                if total_num_loops % life_expect_loops == 0:

                    # Particles past the "max" age will die with a probability proportional to how old they are
                    for particle in old_particles:
                        if particle.age < 2 * life_expect_loops:
                            chance = 0.15
                        elif particle.age < 4 * life_expect_loops:
                            chance = 0.3
                        elif particle.age < 6 * life_expect_loops:
                            chance = 0.45
                        elif particle.age < 8 * life_expect_loops:
                            chance = 0.6
                        elif particle.age < 10 * life_expect_loops:
                            chance = 0.75
                        elif particle.age < 12 * life_expect_loops:
                            chance = 0.90
                        else:
                            chance = 1
                        if random() < chance:
                            particles.remove(particle)
                            num_particles -= 1

                    # Particles with many neighbors will reproduce at a rate proportional to their age
                    for particle in many_neighbors:
                        if particle.age < 2 * life_expect_loops:
                            chance = 0.4
                        elif particle.age < 4 * life_expect_loops:
                            chance = 0.3
                        elif particle.age < 6 * life_expect_loops:
                            chance = 0.2
                        elif particle.age < 8 * life_expect_loops:
                            chance = 0.1
                        else:
                            chance = 0
                        if random() < chance:
                            new_particle = pt(x=particle.x+2*particle.size, y=particle.y+2*particle.size, color=particle.color, size=particle.size)
                            particles.append(new_particle)
                            num_particles += 1

                    # Check to make sure the sim should keep running
                    if num_particles == 0:
                        running = False

        # Update particle color numbers
        red_count_entry.set_text(f"{red_count}")
        green_count_entry.set_text(f"{green_count}")
        blue_count_entry.set_text(f"{blue_count}")
        purple_count_entry.set_text(f"{purple_count}")
        yellow_count_entry.set_text(f"{yellow_count}")
        cyan_count_entry.set_text(f"{cyan_count}")
        total_count_entry.set_text(f"{num_particles}")

        # Counts and prints the total number of loops in the lifetime of the current sim
        total_num_loops +=1
        loops_text.set_text(f"{total_num_loops}")

        # Updates the text to show the oldest particle in the sim
        oldest_text.set_text(f"{oldest_particle.age}")

        # Get mouse position and draw a circle around it
        m_x, m_y = pygame.mouse.get_pos()
        pygame.draw.circle(simulation_screen, WHITE, (m_x-panel_size_x, m_y), mouse_radius, 1)

        #Draw the walls, if any have been added
        if num_walls > 0:
            for wall in walls:
                wall.draw_wall(simulation_screen)

        #Determine length of time it took the current iteration of the game loop to run, and calculate actual FPS
        t1 = time()
        loop_length = t1-t0
        actual_rate = 1/loop_length
        fps_rate.set_text(f"{actual_rate:.2f}")
        if loaded_clock:
            ttotal_min = int((total_time + (t1-load_time))/60)
            ttotal_sec = int((total_time + (t1-load_time))%60)
        else:
            ttotal_min = int((t1-tstart)/60)
            ttotal_sec = int((t1-tstart)%60)
        total_time_text.set_text(f"{ttotal_min}:{ttotal_sec:02d}")

         # Update the control panel, draw the control panel, and paste the control panel and simulation surfaces onto the main screen
        manager.update(loop_length)        
        manager.draw_ui(panel)
        screen.blit(panel, (0,0))
        screen.blit(simulation_screen, (panel_size_x,0))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()