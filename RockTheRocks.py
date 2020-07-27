import simplegui
import math
import random


class ImageInfo:
    """Class holds info on image and sound assets."""

    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated


debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# Program begins here.---------------------------------------------- #

# Helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# Ship class ------------------------------------------------------- #
class Ship:
    """Ship class to define ship position and movement."""
    def __init__(self, pos, vel, angle, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = angle
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()           
        if sound:
            self.sound = ship_thrust_sound
            self.sound.rewind()
        # Not passed init values.    
        self.thrust = False
        self.shoot = False        
        self.angle_vel = 0  
        self.forward = [0, 1]
        self.left = False
        self.right = False
               
    def draw(self,canvas):
        """Draws ship (with or without flames), and plays thrust sound."""
        t = [90 if self.thrust else 0]
        [self.sound.play() if self.thrust else self.sound.rewind()]
        canvas.draw_image(self.image, (self.image_center[0]+t[0], 
                          self.image_center[1]), self.image_size, self.pos, 
                          self.image_size, self.angle)

    def update(self):
        """Updates ship position. Modulo "%" wraps ship around canvas size."""
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        # Do the angle update
        if self.right and not self.left:
            self.angle += 0.05
        if self.left and not self.right:
            self.angle -= 0.05

        # Updates ship position using angle_to_vector calculation.   
        for i in (0, 1):
            self.forward[i] = angle_to_vector(self.angle)[i]
            self.vel[i] *= (1 - .2)  
            if self.thrust:
                self.vel[i] += self.forward[i]
                
    def key_event(self, key, dir):
        """Uses alias, "key_map" refers to 'simplegui.KEY_MAP'."""
        key_map = simplegui.KEY_MAP
        # key_map is a local variable.
        if key == key_map["right"]:
            self.right = True if dir == "down" else False
        if key == key_map["left"]:
            self.left = True if dir == "down" else False
        if key == key_map["up"]:
            self.thrust = True if dir == "down" else False            
        # Implements one missile function, per space-bar down.          
        if key == key_map["space"] and dir == "down":         
            shoot()
            
# Helper function shoot() and missile_group. ---------------------- #            
def shoot():
    # Do not need 'global game, missile' declaration.
    # missile_pos and missile_vel are local variables.
    # game class missile_group changed, not assigned value, no global.
    missile_pos = [0, 0]
    missile_vel = [0, 0]
    for i in (0, 1):         
        missile_pos[i] = ship.pos[i] + ship.forward[i]*40
        missile_vel[i] = ship.vel[i] + ship.forward[i]*5  
    missile = Sprite(missile_pos, missile_vel, 0, 0, 
                     missile_image, missile_info, missile_sound)
    missile.sound.play()  
    game.missile_group.add(missile)

# Sprite class ----------------------------------------------------- #
class Sprite:
    """Sprite class defines missile, rock, and explosion."""
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.animated = info.get_animated()
        if sound:
            self.sound = sound
            sound.rewind()
        # age and lifespan initial values    
        self.age = 0
        self.lifespan = info.get_lifespan()
        self.die = False  
        self.collide = False
        
    def draw(self, canvas):
        if self.animated == False:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        elif self.animated:  
            # Draws explosion image.
            current_center = [self.image_center[0] + self.age 
                              * self.image_size[0], self.image_center[1]]
            canvas.draw_image(self.image, current_center, self.image_size, 
                              self.pos, self.image_size)             
    
    def update(self):
        self.angle -= self.angle_vel        
        # Modified (x, y) to allow partial object to stay on edge of canvas.
        self.pos[0] = (self.pos[0] + self.vel[0]) % (WIDTH + self.radius)
        self.pos[1] = (self.pos[1] + self.vel[1]) % (HEIGHT + self.radius)           
        self.age += 1
        if self.age > self.lifespan:
            self.die = True   

    def collide(self, other):
        # Determines collision between rock/missile and other object.
        if dist(self.pos, other.pos) < self.radius + other.radius:
            self.collide = True
        return self.collide

# timer handler that spawns a rock. ------------------------------- # 
def rock_spawner():
    ship_radius = ship_info.get_radius()
    rock_radius = asteroid_info.get_radius()
    # Maximum rocks at any time is 10.    
    if game.started and len(game.rock_group) < 10:        
        rock_pos = [random.randrange(50, WIDTH - 50), 
                    random.randrange(50, HEIGHT - 50)]
        rock_vel = [random.randrange(-7, 7) * game.time / 8000, 
                    random.randrange(-6, 6) * game.time / 8000]
        rock_anglevel = random.random() * .05 - .05                
        # Only spawn new rock if collision with ship is false.
        if dist(rock_pos, ship.pos) > (ship_radius + rock_radius + 3):  
            rock = Sprite(rock_pos, rock_vel, 0, rock_anglevel, 
                          asteroid_image, asteroid_info)  
            game.rock_group.add(rock)            
               
# process sprite group and group_collide helper functions. --------- #

def process_sprite_group(group, canvas):   
    # Get canvas passed in from Game.draw.
    copyset = set(group)
    for obj in copyset:
        obj.draw(canvas)
        # Call to obj.draw draws whole sprite group.
        obj.update()
        if obj.die:
            group.remove(obj)
            
def group_collide(group, other_obj): 
    collide = False
    copyset = set(group)
    for obj in copyset:        
         if Sprite.collide(obj, other_obj):
            collide = True    
            group.remove(obj)                    
            # Create explosion object, add to explosion_group.
            explosion = Sprite(other_obj.pos, other_obj.vel, 
                               other_obj.angle, other_obj.angle_vel, 
                               explosion_image, explosion_info, 
                               explosion_sound)
            game.explosion_group.add(explosion)
            explosion.sound.play()
    return collide            

def group_group_collide(group_a, group_b):
    collide = False
    copyset = set(group_b)    
    for obj in copyset:
        if group_collide(group_a, obj):
            group_b.remove(obj)
            collide = True
    return collide  

# Game class to handle game state variable. ------------------------ #
class Game:
    """Game class keeps track of game state & main draw function."""
    
    high_score = 0
    # Class variable, used to calculate high_score.
    
    def __init__(self, started, lives, score, soundtrack = None): 
        """Moves global game state variables to Game class."""
        self.started = started
        self.lives = lives
        self.score = score        
        # Compare stored high_score with current game score.
        self.__class__.high_score = max(score, self.__class__.high_score)  
        if soundtrack:
            self.soundtrack = soundtrack
            self.soundtrack.rewind()  
        # variables not passed in.    
        self.rock_group = set([])
        self.missile_group = set([])
        self.explosion_group = set([])
        self.time = 0.5                
        
    def draw(self, canvas):
        """Main draw handler function."""    
        
        # animiate background
        self.time += 1
        center = debris_info.get_center()
        size = debris_info.get_size()
        wtime = (self.time / 8) % center[0]
        canvas.draw_image(nebula_image, nebula_info.get_center(), 
                      nebula_info.get_size(), 
                      [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
        canvas.draw_image(debris_image, [center[0] - wtime, center[1]], 
                      [size[0] - 2 * wtime, size[1]], 
                      [WIDTH / 2 + 1.25 * wtime, HEIGHT / 2], 
                      [WIDTH - 2.5 * wtime, HEIGHT])    
        # Error on this debris field, non-positive image size.  
        canvas.draw_image(debris_image, [size[0] - wtime, center[1]], 
                      [2 * wtime, size[1]], [1.25 * wtime, HEIGHT / 2], 
                      [2.5 * wtime, HEIGHT])
        
        # Draw & update ship. Process rocks, missiles, explosions.
        ship.draw(canvas) 
        ship.update()
        process_sprite_group(self.rock_group, canvas) 
        process_sprite_group(self.missile_group, canvas) 
        process_sprite_group(self.explosion_group, canvas)
           
        # Update lives, score
        if group_collide(self.rock_group, ship):
            self.lives -= 1
        if group_group_collide(self.missile_group, self.rock_group):
            self.score += 1
        if self.lives == 0:
            # If lives drops to 0, call self.__init__ ,
            # but keep current lives & score until splash screen is clicked.
            self.__init__(False, self.lives, self.score, soundtrack)
                       
        # Draw lives and score.
        canvas.draw_text("Lives = " + str(self.lives), [25, 25], 20, "White")
        canvas.draw_text("Score = " + str(self.score), [WIDTH - 300, 25], 20, 
                         "White")
        canvas.draw_text("High Score = " + str(self.__class__.high_score), 
                         [WIDTH - 175, 25], 20, "Yellow")
              
        # Draw splash screen.
        if not self.started:
            canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [CENTER[0], CENTER[1]], 
                          splash_info.get_size())

# Mouse click handler. -------------------------------------------- #
def click(pos):
    """Mouse click handler - reset lives/score, redraw splash."""
    size = splash_info.get_size()
    inwidth = (CENTER[0] - size[0]/2) < pos[0] < (CENTER[0] + size[0]/2)
    inheight = (CENTER[1] - size[1]/2) < pos[1] < (CENTER[1] + size[1]/2)
    if (not game.started) and inwidth and inheight:
        game.started = True
        game.lives = 3
        game.score = 0    
        game.soundtrack.play()
            
# Globals for frame dimensions. ------------------------------------ # 
WIDTH = 800
HEIGHT = 600
CENTER = [WIDTH/2, HEIGHT/2]

# Initialize ship, rock, missile, & game --------------------------- #
ship = Ship([CENTER[0], CENTER[1]], [0, 0], math.pi, ship_image, ship_info, 
            ship_thrust_sound)
rock = Sprite([WIDTH / 3, HEIGHT / 3], [0, 0], 0, 0, asteroid_image, 
              asteroid_info)
missile = Sprite([CENTER[0], CENTER[1]], [0,0], math.pi, 0, missile_image, 
                 missile_info, missile_sound)
game = Game(False, 3, 0, soundtrack)
    # Game class moves game state vars from globals to class fields. 
                     
# Initialize frame -------------------------------------------------- #
frame = simplegui.create_frame("Rice Rocks - Asteroids", WIDTH, HEIGHT)
frame.add_label("Click splash screen to begin.")
frame.add_label(" ")
frame.add_label("space-bar: missile")
frame.add_label("up arrow: thrust")
frame.add_label("left arrow: rotate left")
frame.add_label("right arrow: rotate right")

# Register handlers ------------------------------------------------- #
frame.set_keydown_handler(lambda key: ship.key_event(key, "down"))
frame.set_keyup_handler(lambda key: ship.key_event(key, "up"))
frame.set_mouseclick_handler(click)
frame.set_draw_handler(game.draw)
timer = simplegui.create_timer(1100, rock_spawner)

# Start frame and timer.
timer.start()
frame.start()