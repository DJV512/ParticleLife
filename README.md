# Particle Life
## By David Vance

### My own implementation of Particle Life, in Python, inspired by many others.

This project was initially implemented in one file (main.py, now located within Original). I then challenged myself to 
refactor the code to make particles into a class, which has successfully been completed. I've since implemented many 
other goals, including saving and loading simulations, particles of different sizes, and a very primitive "evolution"
system. The evolution system at this point kills off particles after a certain age, and allows a percentage of particles
with "many neighbors" to reproduce an identical particle. The plan eventually is for every particle to have it's own
attraction matrix, rather than just one that governs all particles, and that thosee values, along with size and color, will be mutatable when particles reproduce. I still need to figure out what makes a particle "fit" enough to reproduce. I don't
love the "many neighbors" test. I may end up adding some kind of "food."

Finally, I'm trying to learn the new language Mojo, and I want to re-implement the entire project in Mojo to see if 
I can get it to run faster (and therefore have more particles on screen at once).

This project is still a work in progress, and will change frequently. Please feel free to reach out with questions or
suggestions!

### NOTE:
The code within Javascript/main.js is entirely copied from the YouTube video "The code behind Particle Life" by Tom Mohr.
I copied that code first just to see how it works, before implementing my own version in Python.
I claim no ownership of the javascript code. See these links instead:
https://github.com/tom-mohr/particle-life-app
https://www.youtube.com/watch?v=scvuli-zcRc&t=440s
