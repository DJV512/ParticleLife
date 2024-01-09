# from python import Python
from random import randint
from random import choice
import pygame
   
fn main():

    let BLACK: Tuple[Int, Int, Int] = (0,0,0)
    let WHITE: Tuple[Int, Int, Int] = (255,255,255)

    # Controls frame rate
    let rate: Float32 = 30.0
    let dt: Float32 = 1/rate

    # Set default values for changeable parameters
    let rmax: Int = 100
    let friction_half_life: Float32 = 0.04
    let friction_factor: Float32 = one_half ** (dt/friction_half_life)
    let beta: Float32 = 0.3
    let force_factor: Int = 5

    let num_particles: Int = 50
    let wall_repel_distance: Int = 30


    var x: Float32
    var y: Float32
    var x_vel: Float32
    var y_vel: Float32
    var size: Int
    var color: Int
    var r: Float32
    var rx: Float32
    var ry: Float32

    var COLORS: ListLiteral[Tuple[Int, Int, Int], Tuple[Int, Int, Int], 
                            Tuple[Int, Int, Int], Tuple[Int, Int, Int], 
                            Tuple[Int, Int, Int], Tuple[Int, Int, Int]]

    var attract_matrix: ListLiteral[ListLiteral[Float32]]

    COLORS = [(255,0,0), (0,255,0), (0,0,255), (255,0,255), (255,255,0), (0,255,255)]

    fn make_random_particles() -> ListLiteral:
        x = random() * 1000
        y = random() * 1000
        x_vel = 0
        y_vel = 0
        size = 2
        color = randint(0,5)
        return attract_matrix


    fn intra_particle_dist(rmax: Float32) -> Float32:
        '''
        Determines the distance between two particles.
        '''
        r = 1000
        ry = 1000
        rx = x - other_particle.x
        if rx < rmax:
            ry = y - other_particle.y
            if ry < rmax:
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

    fn draw(screen: Surface):
        pygame.draw.circle(screen, COLORS[color], (x, y), size)

    #Make num_particles particles
    var x_positions: ListLiteral[Float32]
    
    #Make random attraction matrix
    var attract_matrix: ListLiteral[ListLiteral[Float32]]
    for i in range(6):
            for j in range(6):
                attract_matrix[i][j] = random() * 2 - 1 

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
        for particle in particles:
            particle.draw(screen)
        
        # Update the screen
        pygame.display.flip()

        # Update particle velocities
        for particle1 in particles:
            var accel_x: Float32 = 0
            var accel_y: Float32 = 0
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


        # Controls frame rate
        clock.tick(rate)


    pygame.quit()