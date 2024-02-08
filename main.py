from copy import deepcopy
from food import Food
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

    color_dict = {
        0: "red",
        1: "green",
        2: "blue",
        3: "purple",
        4: "yellow",
        5: "cyan",
    }

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
    ident_part_y = 500
    footer_y = 950

    # Controls frame rate
    rate = 60
    dt = 1/rate

    # Flag to determine whether evolution is on or off
    evolution = True

    # Life expectancy of a particle, related to food intake
    life_expect_loops = 1000

    # Counters for the total number of loops and total time
    total_num_loops = 0
    ttotal_min = 0
    ttotal_sec = 0
    loaded_clock = False
    total_time = 0

    # Set default values for changeable parameters
    default_beta = 0.1
    default_force_factor = 5

    # Starting number of particle defaults
    default_num_particles = 100
    num_particles = default_num_particles
    oldest_particle = 0
    no_oldest_particle = 0
    red_count = 0
    green_count = 0
    blue_count = 0
    purple_count = 0
    yellow_count = 0
    cyan_count = 0

    # Food settings
    num_food_pieces = 500
    nutrition_to_reproduce = 4
    add_food_num_loops = 9

    # Default values
    beta = default_beta
    # Control the friction force
    force_factor = default_force_factor

    # Variables to measure the actual frame_rate
    actual_rate = rate
    loop_length = 1/rate

    # Save and load flags
    SAVE = False
    LOAD = False

    # Mouse parameters
    mouse_mode = "ident"
    mouse_radius = 10
    grab = False
    add_particles = False
    remove_particles = False
    draw_wall = False
    remove_wall = False
    walls = []
    num_walls = 0

    # Make num_particles number of randomly positioned and colored parrticles
    particles = [pt() for _ in range(num_particles)]

    # Temporarily use the first created particle as the "selected" particle until the user selects their own
    selected_particle = particles[0]

    # Randomize initial food positions
    food_pieces = [Food() for _ in range(num_food_pieces)]

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
                                                         options_list=["Ident Particles", "Grab Particles", "Add Particles", "Remove Particles"], starting_option="Ident Particles",
                                                         manager=manager)
    # Removed ", "Add Wall", "Remove Wall"" from the above menu until I can make it work right.

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((355, dropdown_y), (100,30)),
                                                 text="Mouse Size", manager=manager)
    mouse_radius_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((455, dropdown_y), (50,30)),
                                                         options_list=["10","30","50","70","90"], starting_option="10",
                                                         manager=manager)
    
    text_beta = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, slider_y), (300, 20)),
                                            text=f"Beta (how close they can get): {default_beta:.2f}",
                                            manager=manager)
    slider_beta = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((35, slider_y + 20), (300, 20)),
                                                         start_value=beta, value_range=(0, 1), manager=manager)
    
    text_force = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((30, slider_y + 50), (250, 20)),
                                             text=f"Force (scalar multiple): {default_force_factor:.2f}",
                                             manager=manager)
    slider_force = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((35, slider_y + 70), (300, 20)),
                                                          start_value=force_factor, value_range=(0, 50),
                                                          manager=manager)
    
    reset_sliders_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((355, slider_y+15), (140, 30)),
                                            text='Reset Sliders', manager=manager)
    new_particles_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((355, slider_y+65), (140, 30)),
                                            text='New Particles', manager=manager)
    new_forces_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((355, slider_y+115), (140, 30)),
                                            text='New Forces', manager=manager)


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
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0,ident_part_y), (540, 20)),
                                            text=f"Parameters of the selected particle", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+30), (90, 20)),
                                text="x-position:", manager=manager)
    ident_particle_x = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+30), (50,20)),
                                                   text=f"{selected_particle.x:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+60), (90, 20)),
                                text="y-position:", manager=manager)
    ident_particle_y = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+60), (50,20)),
                                                   text=f"{selected_particle.y:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+90), (90, 20)),
                                text="age:", manager=manager)
    ident_particle_age = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+90), (50,20)),
                                                   text=f"{selected_particle.age}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+120), (90, 20)),
                                text="color:", manager=manager)
    ident_particle_color = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+120), (50,20)),
                                                   text=f"{selected_particle.color}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+150), (90, 20)),
                                text="size:", manager=manager)
    ident_particle_size = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+150), (50,20)),
                                                   text=f"{selected_particle.size}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+180), (90, 20)),
                                text="nutrition:", manager=manager)
    ident_particle_nutrition = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+180), (50,20)),
                                                   text=f"{selected_particle.nutrition}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+210), (90, 20)),
                                text="generation:", manager=manager)
    ident_particle_history = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+210), (50,20)),
                                                   text=f"{len(selected_particle.history)+1}", manager=manager)

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+240), (90, 20)),
                                text="reproduced:", manager=manager)
    ident_particle_reproduced = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((150, ident_part_y+240), (50,20)),
                                                   text=f"{selected_particle.reproduced}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50,ident_part_y+270), (90, 20)),
                                text="ID:", manager=manager)
    ident_particle_id = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, ident_part_y+270), (100,20)),
                                                   text=f"{hex(id(selected_particle))}", manager=manager)
    

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+30), (90, 20)),
                                text="food radar:", manager=manager)
    ident_particle_food_radar = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+30), (50,20)),
                                                   text=f"{selected_particle.food_radar:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+60), (90, 20)),
                                text="rmax:", manager=manager)
    ident_particle_rmax = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+60), (50,20)),
                                                   text=f"{selected_particle.rmax:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+90), (90, 20)),
                                text="friction:", manager=manager)
    ident_particle_friction = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+90), (50,20)),
                                                   text=f"{selected_particle.friction:.2f}", manager=manager)

    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+120), (90, 20)),
                                text="red:", manager=manager)
    ident_particle_attraction0 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+120), (50,20)),
                                                   text=f"{selected_particle.attractions[0]:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+150), (90, 20)),
                                text="green:", manager=manager)
    ident_particle_attraction1 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+150), (50,20)),
                                                   text=f"{selected_particle.attractions[1]:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+180), (90, 20)),
                                text="blue:", manager=manager)
    ident_particle_attraction2 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+180), (50,20)),
                                                   text=f"{selected_particle.attractions[2]:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+210), (90, 20)),
                                text="purple:", manager=manager)
    ident_particle_attraction3 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+210), (50,20)),
                                                   text=f"{selected_particle.attractions[3]:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+240), (90, 20)),
                                text="yellow:", manager=manager)
    ident_particle_attraction4 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+240), (50,20)),
                                                   text=f"{selected_particle.attractions[4]:.2f}", manager=manager)
    
    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250,ident_part_y+270), (90, 20)),
                                text="cyan:", manager=manager)
    ident_particle_attraction5 = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((350, ident_part_y+270), (50,20)),
                                                   text=f"{selected_particle.attractions[5]:2f}", manager=manager)
    


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
                elif event.ui_element == slider_force:
                    force_factor = float(event.value)
                    text_force.set_text(f"Force (scalar multiple): {force_factor:.2f}")

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
                    if event.text == "Ident Particle":
                        mouse_mode = "ident"
                    elif event.text == "Grab Particles":
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
                
                # Get current mouse position, and only perform action if the mouse is within the simulation screen
                m_x, m_y = pygame.mouse.get_pos()
                m_x -= panel_size_x
                if m_x > 0:
                
                    # When grab is selected, mouse clicking grabs all particles in mouse radius
                    if mouse_mode == "grab" and not grab and not paused:
                        paused = True
                        grab = True
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
                        particles.append(pt(x=m_x, y=m_y))
                        num_particles += 1
                    
                    # When remove is selected, mouse clicking removes all particles in the mouse radius
                    elif mouse_mode == "remove":
                        remove_particles = True
                        for particle in particles.copy():
                            r = ((particle.x-m_x)**2 + (particle.y-m_y)**2)**(1/2)
                            if r < mouse_radius:
                                particles.remove(particle)
                                num_particles -= 1
                    
                    # When ident is selected, mouse clicking shows the parameters of the selected particle
                    elif mouse_mode == "ident":
                        min_distance = 1000
                        for particle in particles:
                            r = ((particle.x-m_x)**2 + (particle.y-m_y)**2)**(1/2)
                            if r < min_distance:
                                min_distance = r
                                selected_particle = particle

                    # When wall is selected, mouse clicking will draw wall
                    elif mouse_mode == "wall":
                        draw_wall = True
                        walls.append(Wall(m_x, m_y, mouse_radius))
                        num_walls += 1
                    
                    # When remove wall is selected, mouse clicking will remove wall
                    elif mouse_mode == "remove_wall":
                        remove_wall = True
                        for wall in walls.copy():
                            r = ((wall.x-m_x)**2 + (wall.y-m_y)**2)**(1/2)
                            if r < mouse_radius:
                                walls.remove(wall)
                                num_walls -= 1

                    
            # Handle mouse motion 
            elif event.type == pygame.MOUSEMOTION:

                # Get current mouse position, and only perform action if the mouse is within the simulation screen
                m_x, m_y = pygame.mouse.get_pos()
                m_x -= panel_size_x
                if m_x > 0:

                    # Mouse dragging moves all particles in mouse radius
                    if grab:
                        change_x = m_x - m_x_current
                        change_y = m_y - m_y_current
                        for particle in grabbed:
                            particle.x += change_x
                            particle.y += change_y
                        m_x_current = m_x
                        m_y_current = m_y

                    # Mouse dragging continues removing particles
                    elif remove_particles:
                        for particle in particles.copy():
                            r = ((particle.x-m_x)**2 + (particle.y-m_y)**2)**(1/2)
                            if r < mouse_radius:
                                particles.remove(particle)
                                num_particles -= 1

                    # Mouse dragging continues to add new particles
                    elif add_particles:
                        particles.append(pt(x=m_x, y=m_y))
                        num_particles += 1
                    
                    # Mouse dragging draws more wall pieces
                    elif draw_wall:
                        walls.append(Wall(m_x, m_y, mouse_radius))
                        num_walls += 1

                    # Mouse dragging removes more wall pieces
                    elif remove_wall:
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

                    force_factor = default_force_factor
                    slider_force.set_current_value(force_factor)
                    text_force.set_text(f"Force (scalar multiple): {force_factor:.2f}")
                
                elif event.ui_element == new_particles_button:
                    red_count = 0
                    green_count = 0
                    blue_count = 0
                    purple_count = 0
                    yellow_count = 0
                    cyan_count = 0
                    num_particles = default_num_particles
                    particles = [pt() for _ in range(num_particles)]

                elif event.ui_element == new_forces_button:
                    for particle in particles:
                        particle.attractions = [(random() * 2 - 1) for _ in range(6)]
                
                elif event.ui_element == pause_button:
                    paused = not paused

                elif event.ui_element == restart_all_button:
                    execl(executable, executable, *argv)

                elif event.ui_element == save_button:
                    paused=True
                    game_settings = {
                        "parameters": {
                            "particle_repel_force": particle_repel_force,
                            "rate": rate,
                            "evolution": evolution,
                            "life_expect_loops": life_expect_loops,
                            "beta": beta,
                            "force_factor": force_factor,
                            "num_particles": num_particles,
                            "ttotal_min": ttotal_min,
                            "ttotal_sec": ttotal_sec,
                            "total_num_loops": total_num_loops,
                            "num_walls": num_walls,
                            "num_food_pieces": num_food_pieces
                        },

                        "particle_data": [(part.x, part.y, part.x_vel, part.y_vel, part.age, part.color, part.size, part.nutrition, part.attractions, part.reproduced, part.rmax, part.food_radar, part.friction, part.history) for part in particles],

                        "wall_data": [(wall.x, wall.y) for wall in walls],

                        "food_data": [(food.x, food.y, food.size) for food in food_pieces]
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

                    particle_repel_force = data["parameters"]["particle_repel_force"]
                    rate = data["parameters"]["rate"]
                    evolution = data["parameters"]["evolution"]
                    life_expect_loops = data["parameters"]["life_expect_loops"]        
                    beta = data["parameters"]["beta"]
                    force_factor = data["parameters"]["force_factor"]
                    num_particles = data["parameters"]["num_particles"]
                    num_walls = data["parameters"]["num_walls"]
                    num_food_pieces = data["parameters"]["num_food_pieces"]
                    ttotal_min = data["parameters"]["ttotal_min"]
                    ttotal_sec = data["parameters"]["ttotal_sec"]
                    total_time = data["parameters"]["total_time"]
                    total_num_loops = data["parameters"]["total_num_loops"]

                    slider_beta.set_current_value(beta)
                    text_beta.set_text(f"Beta (how close they can get): {beta:.2f}") 
                    slider_force.set_current_value(force_factor)
                    text_force.set_text(f"Force (scalar multiple): {force_factor:.2f}")

                    total_time_text.set_text(f"{ttotal_min}:{ttotal_sec:02d}")
                    loops_text.set_text(f"{total_num_loops}")

                    particles = []
                    particles = [pt(x=data["particle_data"][i][0], 
                                    y=data["particle_data"][i][1], 
                                    x_vel=data["particle_data"][i][2],
                                    y_vel=data["particle_data"][i][3],
                                    age=data["particle_data"][i][4],
                                    color=data["particle_data"][i][5],
                                    size=data["particle_data"][i][6],
                                    nutrition=["particle_data"][i][7],
                                    attractions=["particle_data"][i][8],
                                    reproduced=["particle_data"][i][9],
                                    rmax=["particle_data"][i][10],
                                    food_radar=["particle_data"][i][11],
                                    friction=["particle_data"][i][12],
                                    history=["particle_data"][i][13],
                                    ) 
                                for i in range(num_particles)]
                    
                    walls = []
                    walls = [Wall(x=data["wall_data"][i][0],
                                  y=data["wall_data"][i][1],
                                  )
                            for i in range(num_walls)]

                    food_pieces = []
                    food_pieces = [Food(x=data["food_data"][i][0],
                                        y=data["food_data"][i][1],
                                        size=data["food_data"][i][2]
                                        )
                                    for i in range(num_food_pieces)]

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

        # Draw all food onto the simulation_screen surface
        for food in food_pieces:
            food.draw(simulation_screen)

        # Where the magic happens - Update particle velocities and positions
        if not paused:

            # Keep track of the total number of loops
            total_num_loops +=1

            # Initialize the counters for the colors
            red_count = 0
            green_count = 0
            blue_count = 0
            purple_count = 0
            yellow_count = 0
            cyan_count = 0

            # Add a new random piece of food every x loops
            if total_num_loops < 20000 and total_num_loops % (add_food_num_loops/3) == 0:
                food_pieces.append(Food())
                num_food_pieces += 1
            elif total_num_loops < 40000 and total_num_loops % (add_food_num_loops) == 0:
                food_pieces.append(Food())
                num_food_pieces += 1
            elif total_num_loops % (add_food_num_loops * 3) == 0:
                food_pieces.append(Food())
                num_food_pieces += 1

            # Determine which particle is the oldest
            if num_particles > 0:
                oldest_particle = max(particles, key=attrgetter("age"))

            # Cycle through all particles
            for particle1 in particles:
                
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

                # Initialize the particle's acceleration to 0        
                accel_x = 0
                accel_y = 0

                # Determine how much force every other particle applies to particle1
                for particle2 in particles:
                    if particle1 == particle2:
                        continue
                    else:
                        rx, ry, r_centers, r_surfaces = particle1.intra_particle_dist(particle2)
                        if r_centers > particle1.rmax:
                            continue
                        elif r_centers <= particle1.rmax and r_surfaces > 0:
                            f = pt.force(particle1.attractions[particle2.color], r_centers/particle1.rmax, beta) * particle2.size
                            theta = atan2(ry, rx)
                            accel_x += cos(theta) * f
                            accel_y += sin(theta) * f
                        elif r_surfaces < 0:
                            theta = atan2(ry, rx)
                            accel_x += cos(theta) * particle_repel_force
                            accel_y += sin(theta) * particle_repel_force
                
                # If particle1 is attracted or repulsed by food, then figure out how far it is to each food piece and calculate the effect on particle1's acceleration
                if particle1.food_radar != 0:
                    for food in food_pieces:
                        rx, ry, r_centers = particle1.particle_to_food_dist(food)
                        if r_centers > particle1.rmax:
                            continue
                        elif r_centers <= particle1.rmax:
                            f =  (1 - r_centers/particle1.rmax) * food.size * particle1.food_radar
                            theta = atan2(ry, rx)
                            accel_x += cos(theta) * f
                            accel_y += sin(theta) * f

                # Increment particle1's age
                particle1.age += 1

                # Scaling factor for the strength of the attraction or repulsion force
                accel_x *= particle1.rmax * force_factor
                accel_y *= particle1.rmax * force_factor
                
                # Slow particle1 down to account for friction
                friction_factor = 0.5 ** (dt/particle1.friction)
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

            # Check if any particles have found food
            for particle in particles:
                for food in food_pieces.copy():
                    _, _, r = particle.particle_to_food_dist(food)
                    if r < (particle.size + food.size):
                        particle.nutrition += food.size
                        food_pieces.remove(food)
                        num_food_pieces -= 1
            
            # Controls evolution if evolution is set to true
            if evolution:
                for particle in particles.copy():
                    
                    necessary_nutrition = nutrition_to_reproduce + particle.size
                    used_nutrition = necessary_nutrition * particle.reproduced
                    age_multiple = particle.age/life_expect_loops

                    # Particles with enough food reproduce
                    if particle.nutrition - used_nutrition >= necessary_nutrition:
                        num_particles += 1
                        particle.reproduced += 1
                        new_particle = pt(x=deepcopy(particle.x)+2*particle.size,
                                          y=deepcopy(particle.y)+2*particle.size,
                                          color=deepcopy(particle.color),
                                          size=deepcopy(particle.size),
                                          attractions=deepcopy(particle.attractions),
                                          rmax=deepcopy(particle.rmax),
                                          food_radar=deepcopy(particle.food_radar),
                                          friction=deepcopy(particle.friction),
                                          history=deepcopy(particle.history) + [[deepcopy(particle.attractions),
                                                                              deepcopy(particle.size),
                                                                              deepcopy(particle.rmax),
                                                                              deepcopy(particle.food_radar),
                                                                              deepcopy(particle.friction)]],
                                          )
                        new_particle.mutate()
                        particles.append(new_particle)
                    
                    # Particles that haven't found enough food to reproduce will die
                    if age_multiple > 1 and particle.reproduced < age_multiple:
                        food_pieces.append(Food(particle.x, particle.y, particle.size))
                        num_food_pieces += 1
                        particles.remove(particle)
                        num_particles -= 1
                        if particle == selected_particle:
                            if len(particles)>0:
                                selected_particle = particles[-1]

        # Update particle color numbers
        red_count_entry.set_text(f"{red_count}")
        green_count_entry.set_text(f"{green_count}")
        blue_count_entry.set_text(f"{blue_count}")
        purple_count_entry.set_text(f"{purple_count}")
        yellow_count_entry.set_text(f"{yellow_count}")
        cyan_count_entry.set_text(f"{cyan_count}")
        total_count_entry.set_text(f"{num_particles}")

        # Update the text of the parameters of the selected particle
        ident_particle_x.set_text(f"{selected_particle.x:.2f}")
        ident_particle_y.set_text(f"{selected_particle.y:.2f}")
        ident_particle_age.set_text(f"{selected_particle.age}")
        ident_particle_color.set_text(f"{color_dict[selected_particle.color]}")
        ident_particle_size.set_text(f"{selected_particle.size}")
        ident_particle_nutrition.set_text(f"{selected_particle.nutrition}")
        ident_particle_history.set_text(f"{len(selected_particle.history)+1}")
        ident_particle_reproduced.set_text(f"{selected_particle.reproduced}")
        ident_particle_id.set_text(f"{hex(id(selected_particle))}")
        ident_particle_food_radar.set_text(f"{selected_particle.food_radar:.2f}")
        ident_particle_rmax.set_text(f"{selected_particle.rmax:.2f}")
        ident_particle_friction.set_text(f"{selected_particle.friction:.2f}")
        ident_particle_attraction0.set_text(f"{selected_particle.attractions[0]:.2f}")
        ident_particle_attraction1.set_text(f"{selected_particle.attractions[1]:.2f}")
        ident_particle_attraction2.set_text(f"{selected_particle.attractions[2]:.2f}")
        ident_particle_attraction3.set_text(f"{selected_particle.attractions[3]:.2f}")
        ident_particle_attraction4.set_text(f"{selected_particle.attractions[4]:.2f}")
        ident_particle_attraction5.set_text(f"{selected_particle.attractions[5]:.2f}")


        # Updates the text for the total number of loops in the lifetime of the current sim
        loops_text.set_text(f"{total_num_loops}")

        # Updates the text to show the oldest particle in the sim
        if num_particles > 0:
            oldest_text.set_text(f"{oldest_particle.age}")
        else:
            oldest_text.set_text(f"{no_oldest_particle}")

        # Get mouse position and draw a circle around it
        m_x, m_y = pygame.mouse.get_pos()
        pygame.draw.circle(simulation_screen, WHITE, (m_x-panel_size_x, m_y), mouse_radius, 1)

        #Draw a circle around the selected particle
        pygame.draw.circle(simulation_screen, WHITE, (selected_particle.x, selected_particle.y), selected_particle.size + 4, 1)

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

        # Update the control panel, draw the control panel
        manager.update(loop_length)        
        manager.draw_ui(panel)

        # Paste the control panel and simulation surfaces onto the main screen
        screen.blit(panel, (0,0))
        screen.blit(simulation_screen, (panel_size_x,0))

        # Actually display the new control panel
        pygame.display.flip()

        # End of game loop

    pygame.quit()

if __name__ == "__main__":
    main()