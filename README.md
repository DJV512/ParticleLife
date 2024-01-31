# Particle Life
## By David Vance

### My own implementation of Particle Life, in Python, inspired by many others.

This project was initially implemented in one file (main.py, now located within Original/). I then challenged myself to 
refactor the code to make particles into a class, which has successfully been completed. I've since implemented many 
other goals, including saving and loading simulations, particles of different sizes, "food" pieces that the particles
must "eat" in order to survive and/or reproduce, the ability to add, remove, move, or identify individual particles, 
the ability to add or remove walls (although it doesn't actually act as a barrier yet!), and changed the attraction matrix
from one matrix that all particles share to each particle having their own attractions and repulsions to every other color.
These changes allowed me to implement "evolution" in the sense that when a particle has eaten enough food to reproduce, their
"genes," which include size, color, attraction matrix, and whether they are attracted to food, are passed on to the
new particle, and with each new generation, one gene is randomly chosen for a slight mutation.

As a longer term goal, I'm trying to learn the new language Mojo, and I want to re-implement the entire project in Mojo to see if 
I can get it to run faster (and therefore have more particles on screen at once without devastating hits to the frame rate).

This project is still a work in progress, and will change frequently. Please feel free to reach out with questions or
suggestions!

### NOTE:
The code within Javascript/main.js is entirely copied from the YouTube video "The code behind Particle Life" by Tom Mohr.
I copied that code first just to see how it works, before implementing my own version in Python.
I claim no ownership of the javascript code. See these links instead:
https://github.com/tom-mohr/particle-life-app
https://www.youtube.com/watch?v=scvuli-zcRc&t=440s
