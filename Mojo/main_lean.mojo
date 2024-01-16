# from python import Python
import random
import pygame
   
def main():

    let BLACK: Tuple[Int, Int, Int] = (0,0,0)
    let WHITE: Tuple[Int, Int, Int] = (255,255,255)

    # Controls frame rate
    let rate: Float32 = 30.0
    let dt: Float32 = 1/rate

    # Set default values for changeable parameters
    let one_half: Float32 = 1.0/2.0
    let rmax: Int = 100
    let friction_half_life: Float32 = 0.04
    let friction_factor: Float32 = one_half ** (dt/friction_half_life)
    let beta: Float32 = 0.3
    let force_factor: Int = 5

    let num_particles: Int = 2
    let wall_repel_distance: Int = 30


    var x_pos: ListLiteral[Float32, Float32]
    var y_pos: ListLiteral[Float32, Float32]
    var x_vel: ListLiteral[Float32, Float32]
    var y_vel: ListLiteral[Float32, Float32]
    var sizes: ListLiteral[Int, Int]
    var colors: ListLiteral[Int, Int]
    var r: Float32
    var rx: Float32
    var ry: Float32

    var COLORS: ListLiteral[Tuple[Int, Int, Int], Tuple[Int, Int, Int], 
                            Tuple[Int, Int, Int], Tuple[Int, Int, Int], 
                            Tuple[Int, Int, Int], Tuple[Int, Int, Int]]

    var attract_matrix: ListLiteral[ListLiteral[Float32]]

    COLORS = [(255,0,0), (0,255,0), (0,0,255), (255,0,255), (255,255,0), (0,255,255)]

    fn make_random_particles() -> ListLiteral, ListLiteral, ListLiteral, ListLiteral, ListLiteral, ListLiteral:
        for _ in range(num_particles):
            x_pos.append(random.random() * 1000)
            y_pos.append(random.random() * 1000)
            x_vel.append(0)
            y_vel.append(0)
            sizes.append(2)
            colors.append(random.randint(0,5))
        return x_pos, y_pos, x_vel, y_vel, sizes, colors


    fn intra_particle_dist(rmax: Float32, i: Int, j: Int) -> Float32:
        '''
        Determines the distance between two particles.
        '''
        rx = x_pos[i]-x_pos[j]
        ry = y_pos[i]-y_pos[j]
        r = (rx**2 + ry**2)**(1/2)
        return rx, ry, r

    fn force(attraction: Float32, scaled_dist: Float32, beta: Float32) -> Float32:
        '''
        Determines the force applied by one particle on another based on their distance apart and attraction value.
        '''
        if scaled_dist < beta:
            return 1 - (scaled_dist/beta)
        elif scaled_dist < 1:
            return attraction * (1 - abs(2 * scaled_dist - 1 - beta)/(1 - beta))

    #Make num_particles particles
    var x_positions: ListLiteral[Float32]
    
    #Make random attraction matrix
    var attract_matrix: ListLiteral[ListLiteral[Float32]]
    for i in range(6):
        for j in range(6):
            attract_matrix[i][j] = random.random() * 2 - 1 

    pygame.init()
    var clock: Clock = pygame.time.Clock()
    
    pygame.display.set_caption("Particle Life")
    var screen: Surface = pygame.display.set_mode([1000,1000])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            manager.process_events(event)

        # Fill the background color
        screen.fill(BLACK)

        # Draw all particles onto the simulation_screen surface
        for i in range(num_particles):
            pygame.draw.circle(screen, COLORS[colors[i]], (x_pos[i], y_pos[i]), sizes[i])
        
        # Update the screen
        pygame.display.flip()

        # Update particle velocities
        for i in range(num_particles):
            var accel_x: Float32 = 0
            var accel_y: Float32 = 0
            for j in range(num_particles):
                if i == j:
                    continue
                else:
                    var rx: Float32
                    var ry: Float32
                    var r: Float32
                    rx, ry, r = intra_particle_dist(rmax, i, j)
                    if r < rmax:
                        var f: Float32
                        f = force(attract_matrix[color[i]][color[j]], r/rmax, beta)
                        if r == 0:
                            r = 0.00001
                        accel_x += rx/r * f
                        accel_y += ry/r * f
            
            # Scaling factor for the strength of the attraction or repulsion force
            accel_x *= rmax * force_factor
            accel_y *= rmax * force_factor
            
            # Slow the particles down to account for friction
            x_vel[i] *= friction_factor
            y_vel[i] *= friction_factor

            # Update velocity based on x and y acceleration and the time step
            x_vel[i] += (accel_x * dt)
            y_vel[i] += (accel_y * dt)

        # Update all particle positions based on x and y velocity and the time step
        for i in range(num_particles):
            x_pos[i] += (x_vel[i] * dt)
            y_pos[i] += (y_vel[i] * dt)


        # Controls frame rate
        clock.tick(rate)


    pygame.quit()