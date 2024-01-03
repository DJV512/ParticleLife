import numpy as np
import pygame
import pygame_gui
import random


blue = (0,0,255)
red = (255,0,0)
green = (0,255,0)
purple = (255,0,255)
yellow = (255,255,0)
background = (0,0,0)
screen_size_x = 1300
screen_size_y = 1000
panel_size = 300
particle_size = 1
num_particles = 350
rate = 60
dt = 1/rate
initial_speed = 0
default_rmax = screen_size_y/10
default_friction_half_life = 0.04
default_beta = 0.1
default_force_factor = 20
border = 0

color_dict = {
        red: 0,
        green: 1,
        blue: 2,
        purple: 3,
        yellow: 4,
    }

    
def force(attraction, scaled_distance, beta):
    if scaled_distance < beta:
        return (scaled_distance/beta) + 1
    elif beta < scaled_distance and scaled_distance < 1:
        return attraction * (1 - abs(2 * scaled_distance - 1 - beta)/ (1 - beta))
    else:
        return 0


def new_matrix():
    attract_matrix = np.ndarray(shape=(5,5), dtype=float)
    for i in range(5):
        for j in range(5):
            attract_matrix[i][j] = random.random()*2 - 1  
    return attract_matrix  


def make_random_particles(num_particles):
    x_positions = []
    y_positions = []
    x_velocity = []
    y_velocity = []
    particle_color = []

    for i in range(num_particles):
        x_positions.append(float(random.randint(0,screen_size_x)))
        y_positions.append(float(random.randint(0,screen_size_y)))
        x_velocity.append(float(random.randint(-initial_speed,initial_speed)))
        y_velocity.append(float(random.randint(-initial_speed,initial_speed)))
        color = random.choice([red, blue, green, yellow, purple])
        particle_color.append(color)
    
    return x_positions, y_positions, x_velocity, y_velocity, particle_color


def main():
    rmax = default_rmax
    friction_half_life = default_friction_half_life
    beta = default_beta
    force_factor = default_force_factor

    friction_factor = 0.5 ** (dt/friction_half_life)

    x_positions, y_positions, x_velocity, y_velocity, particle_color = make_random_particles(num_particles)
    attract_matrix = new_matrix()


    pygame.init()
    clock = pygame.time.Clock()
    
    pygame.display.set_caption("Particle Life")
    screen = pygame.display.set_mode([screen_size_x, screen_size_y])
    simulation_screen = pygame.Surface((screen_size_x, screen_size_y))
    panel = pygame.Surface((300,1000))
    manager = pygame_gui.UIManager((panel_size, screen_size_y), 'theme.json')


    pygame_gui.elements.UILabel(relative_rect=pygame.Rect((0, 980), (300, 20)),
                                            text="Particle Life, by David Vance, 2024",
                                            manager=manager)

    reset_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((25, 10), (120, 30)),
                                            text='Reset', manager=manager)
    new_matrix_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((145, 10), (120, 30)),
                                            text='New Forces', manager=manager)
    slider_beta = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 70), (250, 20)),
                                                  start_value=beta, value_range=(0, 1),
                                                  manager=manager)
    text_beta = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((25, 50), (80, 20)),
                                            text=f"Beta: {slider_beta.get_current_value():.2f}",
                                            manager=manager)
    slider_friction = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 120), (250, 20)),
                                                  start_value=friction_half_life, value_range=(0.0001, 3),
                                                  manager=manager)
    text_friction = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 100), (120, 20)),
                                            text=f"Friction: {slider_friction.get_current_value():.2f}",
                                            manager=manager)
    slider_force = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 170), (250, 20)),
                                                  start_value=force_factor, value_range=(0, 50),
                                                  manager=manager)
    text_force = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 150), (100, 20)),
                                            text=f"Force: {slider_force.get_current_value():.2f}",
                                            manager=manager)
    slider_rmax = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((20, 220), (250, 20)),
                                                  start_value=rmax, value_range=(0, screen_size_y) ,
                                                  manager=manager)
    text_rmax = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 200), (100, 20)),
                                            text=f"rMax: {slider_rmax.get_current_value():.2f}",
                                            manager=manager)
    red_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,260),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][0]:.2f}")
    red_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 240), (50, 20)),
                                            text="R-R", manager=manager)
    red_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,260),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][1]:.2f}")
    red_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, 240), (50, 20)),
                                            text="R-G", manager=manager)
    red_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,260),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][2]:.2f}")
    red_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, 240), (50, 20)),
                                            text="R-B", manager=manager)
    red_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,260),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][3]:.2f}")
    red_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, 240), (50, 20)),
                                            text="R-P", manager=manager)
    red_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,260),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[0][4]:.2f}")
    red_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 240), (50, 20)),
                                            text="R-Y", manager=manager)
    
    green_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,310),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][0]:.2f}")
    green_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 290), (50, 20)),
                                            text="G-R", manager=manager)
    green_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,310),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][1]:.2f}")
    green_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, 290), (50, 20)),
                                            text="G-G", manager=manager)
    green_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,310),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][2]:.2f}")
    green_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, 290), (50, 20)),
                                            text="G-B", manager=manager)
    green_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,310),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][3]:.2f}")
    green_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, 290), (50, 20)),
                                            text="G-P", manager=manager)
    green_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,310),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[1][4]:.2f}")
    green_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 290), (50, 20)),
                                            text="G-Y", manager=manager)

    blue_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,360),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][0]:.2f}")
    blue_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 340), (50, 20)),
                                            text="B-R", manager=manager)
    blue_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,360),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][1]:.2f}")
    blue_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, 340), (50, 20)),
                                            text="B-G", manager=manager)
    blue_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,360),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][2]:.2f}")
    blue_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, 340), (50, 20)),
                                            text="B-B", manager=manager)
    blue_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,360),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][3]:.2f}")
    blue_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, 340), (50, 20)),
                                            text="B-P", manager=manager)
    blue_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,360),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[2][4]:.2f}")
    blue_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 340), (50, 20)),
                                            text="B-Y", manager=manager)
    
    purple_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,410),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][0]:.2f}")
    purple_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 390), (50, 20)),
                                            text="P-R", manager=manager)
    purple_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,410),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][1]:.2f}")
    purple_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, 390), (50, 20)),
                                            text="P-G", manager=manager)
    purple_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,410),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][2]:.2f}")
    purple_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, 390), (50, 20)),
                                            text="P-B", manager=manager)
    purple_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,410),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][3]:.2f}")
    purple_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, 390), (50, 20)),
                                            text="P-P", manager=manager)
    purple_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,410),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[3][4]:.2f}")
    purple_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 390), (50, 20)),
                                            text="P-Y", manager=manager)
    
    yellow_red_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((20,460),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][0]:.2f}")
    yellow_red_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((20, 440), (50, 20)),
                                            text="Y-R", manager=manager)
    yellow_green_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((70,460),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][1]:.2f}")
    yellow_green_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((70, 440), (50, 20)),
                                            text="Y-G", manager=manager)
    yellow_blue_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((120,460),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][2]:.2f}")
    yellow_blue_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((120, 440), (50, 20)),
                                            text="Y-B", manager=manager)
    yellow_purple_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((170,460),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][3]:.2f}")
    yellow_purple_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((170, 440), (50, 20)),
                                            text="Y-P", manager=manager)
    yellow_yellow_entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((220,460),(50,30)),
                                                        manager=manager, initial_text=f"{attract_matrix[4][4]:.2f}")
    yellow_yellow_text = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((220, 440), (50, 20)),
                                            text="Y-Y", manager=manager)

    running = True
    while running:

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
                        else:
                            red_red_entry.set_text(float(f"{attract_matrix[0][0]:.2f}"))
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

                    x_positions, y_positions, x_velocity, y_velocity, particle_color = make_random_particles(num_particles)

                elif event.ui_element == new_matrix_button:
                    attract_matrix = new_matrix()
                    red_red_entry.set_text(f"{attract_matrix[0][0]:.2f}")
                    red_green_entry.set_text(f"{attract_matrix[0][1]:.2f}")
                    red_blue_entry.set_text(f"{attract_matrix[0][2]:.2f}")
                    red_purple_entry.set_text(f"{attract_matrix[0][3]:.2f}")
                    red_yellow_entry.set_text(f"{attract_matrix[0][4]:.2f}")

                    green_red_entry.set_text(f"{attract_matrix[1][0]:.2f}")
                    green_green_entry.set_text(f"{attract_matrix[1][1]:.2f}")
                    green_blue_entry.set_text(f"{attract_matrix[1][2]:.2f}")
                    green_purple_entry.set_text(f"{attract_matrix[1][3]:.2f}")
                    green_yellow_entry.set_text(f"{attract_matrix[1][4]:.2f}")

                    blue_red_entry.set_text(f"{attract_matrix[2][0]:.2f}")
                    blue_green_entry.set_text(f"{attract_matrix[2][1]:.2f}")
                    blue_blue_entry.set_text(f"{attract_matrix[2][2]:.2f}")
                    blue_purple_entry.set_text(f"{attract_matrix[2][3]:.2f}")
                    blue_yellow_entry.set_text(f"{attract_matrix[2][4]:.2f}")

                    purple_red_entry.set_text(f"{attract_matrix[3][0]:.2f}")
                    purple_green_entry.set_text(f"{attract_matrix[3][1]:.2f}")
                    purple_blue_entry.set_text(f"{attract_matrix[3][2]:.2f}")
                    purple_purple_entry.set_text(f"{attract_matrix[3][3]:.2f}")
                    purple_yellow_entry.set_text(f"{attract_matrix[3][4]:.2f}")

                    yellow_red_entry.set_text(f"{attract_matrix[4][0]:.2f}")
                    yellow_green_entry.set_text(f"{attract_matrix[4][1]:.2f}")
                    yellow_blue_entry.set_text(f"{attract_matrix[4][2]:.2f}")
                    yellow_purple_entry.set_text(f"{attract_matrix[4][3]:.2f}")
                    yellow_yellow_entry.set_text(f"{attract_matrix[4][4]:.2f}")

            manager.process_events(event)

        screen.fill(background)
        panel.fill(background)
        simulation_screen.fill(background)

        # Draw all particles
        for i in range(num_particles):
            pygame.draw.circle(simulation_screen, particle_color[i], (x_positions[i],y_positions[i]), particle_size)
        
        manager.update(dt)        
        manager.draw_ui(panel)
        screen.blit(panel, (0,0))
        screen.blit(simulation_screen, (300,0))
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
                    ry = y_positions[i]-y_positions[j]
                    r = (rx**2 + ry**2)**(1/2)
                    n = color_dict[particle_color[i]]
                    m = color_dict[particle_color[j]]
                    attraction = attract_matrix[n][m]
                    f = force(attraction, r/rmax, beta)
                    if r == 0:
                        r = .0000001 
                    accel_x += rx/r * f
                    accel_y += ry/r * f
            
            accel_x *= rmax * force_factor
            accel_y *= rmax * force_factor
            
            x_velocity[i] *= friction_factor
            y_velocity[i] *= friction_factor

            x_velocity[i] += accel_x * dt
            y_velocity[i] += accel_y * dt

        # Update particle positions based on x and y velocities and the time step
        for i in range(num_particles):
            x_positions[i] += x_velocity[i]*dt
            y_positions[i] += y_velocity[i]*dt


        # Making particles teleport to the opposite side of the screen
        # for i in range(num_particles):
        #     if (x_positions[i] - particle_size) < border:
        #         x_positions[i] = screen_size - border
        #     elif (x_positions[i] + particle_size) > (screen_size - border):
        #         x_positions[i] = border

        #     if (y_positions[i] - particle_size) < border:
        #         y_positions[i] = screen_size - border
        #     elif (y_positions[i] + particle_size) > (screen_size - border):
        #         y_positions[i] = border
            
        # Making particles bounce off the walls
        # for i in range(num_particles):
        #     if (x_positions[i] - particle_size) < border or (x_positions[i] + particle_size) > (screen_size - border):
        #         x_velocity[i] = -x_velocity[i]
        #     if (y_positions[i] - particle_size) < border or (y_positions[i] + particle_size) > (screen_size - border):
        #         y_velocity[i] = -y_velocity[i]
        
        # Controls frame rate
        clock.tick(rate)

    pygame.quit()

if __name__ == "__main__":
    main()