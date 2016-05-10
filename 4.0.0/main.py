import pygame
from pygame.locals import *
import sys, os, traceback
if sys.platform in ["win32","win64"]: os.environ["SDL_VIDEO_CENTERED"]="1"
import random
from math import *

import asteroid, asteroid2, asteroid3, player
from math_helpers import *

import PAdLib.occluder as occluder
import PAdLib.particles as particles

pygame.mixer.pre_init(44100, 16, 2, 4096) #frequency, size, channels, buffersize
pygame.init() #turn all of pygame on.
pygame.display.init()
pygame.font.init()

screen_size = [900,600]
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
pygame.display.set_caption("Asteroids III - v.0.1.0 - Trey Jacobsen - 2014")
surface = pygame.display.set_mode(screen_size)
stars = pygame.image.load('Hyades.jpg')
ast = pygame.image.load('Asteroid100px.png')
ast2 = pygame.image.load('Asteroid60px.png')
ast3 = pygame.image.load('Asteroid30px.png')
astrect = ast.get_rect()
ast2rect = ast2.get_rect()
ast3rect = ast3.get_rect()
surface.blit(stars,      (1, 1))
lr = pygame.mixer.Sound('leftrightturn.wav')
f = pygame.mixer.Sound('forward.wav')
b = pygame.mixer.Sound('bull.wav')

fonts = {
    16 : pygame.font.SysFont("Times New Roman",16,True),
    32 : pygame.font.SysFont("Times New Roman",32,True)
}

fire_colors = [(255,0,0),(255,255,0),(255,200,0),(255,128,0),(128,0,0),(0,0,0)]

emitter_rocket = particles.Emitter()
emitter_rocket.set_particle_emit_density(0)
emitter_rocket.set_particle_emit_speed([300.0,400.0])
emitter_rocket.set_particle_emit_life([1.2,2.2])
emitter_rocket.set_particle_emit_colors(fire_colors)

emitter_turn1 = particles.Emitter()
emitter_turn1.set_particle_emit_density(0)
emitter_turn1.set_particle_emit_speed([40.0,200.0])
emitter_turn1.set_particle_emit_life([0.05,0.05])
emitter_turn1.set_particle_emit_colors(fire_colors)

emitter_turn2 = particles.Emitter()
emitter_turn2.set_particle_emit_density(0)
emitter_turn2.set_particle_emit_speed([50.0,250.0])
emitter_turn2.set_particle_emit_life([0.05,0.05])
emitter_turn2.set_particle_emit_colors(fire_colors)

emitter_shock = particles.Emitter()
emitter_shock.set_particle_emit_density(0)
emitter_shock.set_particle_emit_angle(0.0,360.0)
emitter_shock.set_particle_emit_speed([55.0,440.0])
emitter_shock.set_particle_emit_life([0.5,0.8])
emitter_shock.set_particle_emit_colors([(255,255,255),(0,0,0)])

emitter_hit = particles.Emitter()
emitter_hit.set_particle_emit_density(0)
emitter_hit.set_particle_emit_angle(0.0,390.0)
emitter_hit.set_particle_emit_speed([100.0,100.0])
emitter_hit.set_particle_emit_life([0.5,1.0])
emitter_hit.set_particle_emit_colors([(255,255,255),(255,255,0),(0,0,255),(0,0,0)])

emitter_die = particles.Emitter()
emitter_die.set_particle_emit_density(0)
emitter_die.set_particle_emit_angle(0.0,360.0)
emitter_die.set_particle_emit_speed([55.0,111.0])
emitter_die.set_particle_emit_life([1.0,2.5])
emitter_die.set_particle_emit_colors(fire_colors)

particle_system = particles.ParticleSystem()
particle_system.add_emitter(emitter_rocket,"rocket")
particle_system.add_emitter(emitter_turn1,"turn1")
particle_system.add_emitter(emitter_turn2,"turn2")
particle_system.add_emitter(emitter_shock,"shock")
particle_system.add_emitter(emitter_hit,"hit")
particle_system.add_emitter(emitter_die,"die")

level_text_brightness = 0

def load_hs():
    global hs
    try:
        f = open("hs.txt","rb")
        hs = int(f.read())
        f.close()
    except:
        hs = 0
def write_hs():
    f = open("hs.txt","wb")
    f.write(str(hs).encode())
    f.close()

def reset_game():
    global level, player1
    level = 0

    player1 = player.Player([screen_size[0]/2.0,screen_size[1]/2.0])

    next_level()
def next_level():
    global asteroids, asteroids2, asteroids3, bullets, level, level_text_brightness

    level += 1

    player1.level_up(level)

    asteroids = []
    asteroids2 = []
    asteroids3 = []
    for i in range(1*level):
        asteroids.append(asteroid.Asteroid([
            random.randint(0,screen_size[0]),
            random.randint(0,screen_size[1])]))

    level_text_brightness = 1.0

turning = None
count = 0
def more_troids2():
    player1.level_up(level)
    for i in range(2*level):
        asteroids2.append(asteroid2.Asteroid2([
        random.randint(0,screen_size[0]),
        random.randint(0,screen_size[1])]))
    more_troids2.has_been_called = True
    pass
more_troids2.has_been_called = False

def more_troids3():
    player1.level_up(level)
    for i in range(4*level):
        asteroids3.append(asteroid3.Asteroid3([
        random.randint(0,screen_size[0]),
        random.randint(0,screen_size[1])]))
    more_troids3.has_been_called = True
    pass
more_troids3.has_been_called = False

def get_input(dt):
    global turning, count
    keys_pressed = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_position = pygame.mouse.get_pos()
    mouse_rel = pygame.mouse.get_rel()
    for event in pygame.event.get():
        if   event.type == QUIT: return False
        elif event.type == KEYDOWN:
            if   event.key == K_ESCAPE: return False
            elif event.key == K_F2 and not player1.alive:
                reset_game()

    if player1.alive:
        def reset():
            for emitter in [emitter_turn1,emitter_turn2]:
                emitter._padlib_update(particle_system,dt)
                emitter.set_particle_emit_density(0)
        def set_pos_rot():
            def get_vec(rel,angle_delta):
                rotated = rotate_point(rel,radians(player1.angle+angle_delta))
                return player1.position[0] + rotated[0], player1.position[1] - rotated[1]
            if count > 0:
                emitter_turn1.set_position(get_vec([-3,-8],0))
                emitter_turn2.set_position(get_vec([ 7,6],0))
                emitter_turn1.set_particle_emit_angle(-player1.angle+180,15.0)
                emitter_turn2.set_particle_emit_angle(-player1.angle,15.0)
            else:
                emitter_turn1.set_position(get_vec([ 3,-8],0))
                emitter_turn2.set_position(get_vec([-7,6],0))
                emitter_turn1.set_particle_emit_angle(-player1.angle,15.0)
                emitter_turn2.set_particle_emit_angle(-player1.angle+180,15.0)
        def set_left():
            global count
            emitter_turn1.set_particle_emit_density(777)
            emitter_turn2.set_particle_emit_density(777)
            count =  5
        def set_right():
            global count
            emitter_turn1.set_particle_emit_density(777)
            emitter_turn2.set_particle_emit_density(777)
            count = -5
        if keys_pressed[K_LEFT]:
            player1.angle += 5.0
            if turning == None:
                set_left()
                turning = "left"
            lr.play()
            b.stop()
        if keys_pressed[K_RIGHT]:
            player1.angle -= 5.0
            if turning == None:
                set_right()
                turning = "right"
            lr.play()
            b.stop()
        if not keys_pressed[K_LEFT] and not keys_pressed[K_RIGHT]:
            if turning != None:
                if turning == "left":
                    set_right()
                else:
                    set_left()
                turning = None
            lr.stop()
        if count != 0:
            if count < 0: count += 1
            else:         count -= 1
            if count == 0: reset()
        set_pos_rot()

        if keys_pressed[K_UP]:
            player1.velocity[0] += dt*player.Player.thrust*sin(radians(player1.angle))
            player1.velocity[1] += dt*player.Player.thrust*cos(radians(player1.angle))
            emitter_rocket.set_particle_emit_density(50)
            emitter_rocket.set_particle_emit_angle(-player1.angle-90,5.0)
            f.play()
            b.stop()
        if not keys_pressed[K_UP]:
            emitter_rocket.set_particle_emit_density(0)
            f.stop()
        if keys_pressed[K_DOWN]:
            player1.velocity[0] *= .99
            player1.velocity[1] *= .99

        if keys_pressed[K_SPACE]:
            player1.shoot()
            b.play()
        if not keys_pressed[K_SPACE]:
            b.stop()

    return True

def update(dt):
    global level_text_brightness, hs

    if len(asteroids) == 0 and len(asteroids2) == 0 and not more_troids2.has_been_called:
        more_troids2()
    elif len(asteroids) == 0 and len(asteroids2) == 0 and len(asteroids3) == 0 and not more_troids3.has_been_called:
        more_troids3()
    elif len(asteroids) == 0 and len(asteroids2) == 0 and len(asteroids3) == 0 and more_troids3.has_been_called and more_troids2.has_been_called:
        if level < 10:
            next_level()
        else:
            reset_game()
        more_troids3.has_been_called = False
        more_troids2.has_been_called = False
        
    for asteroid in asteroids:
        asteroid.update(dt, screen_size)
        #surface.blit(ast, astrect)
    for asteroid2 in asteroids2:
        asteroid2.update(dt, screen_size)
        #surface.blit(ast2, ast2rect)
    for asteroid3 in asteroids3:
        asteroid3.update(dt, screen_size)
        #surface.blit(ast3, ast3rect)
    player1.update(dt, screen_size)
    if player1.score > hs:
        hs = player1.score

    player1.collide_bullets(asteroids, particle_system, dt)
    player1.collide_asteroids(asteroids, particle_system)

    player1.collide_bullets(asteroids2, particle_system, dt)
    player1.collide_asteroids(asteroids2, particle_system)

    player1.collide_bullets(asteroids3, particle_system, dt)
    player1.collide_asteroids(asteroids3, particle_system)

    emitter_rocket.set_position(player1.position)
##    particle_system.set_particle_occluders([asteroid.occluder for asteroid in asteroids])
    particle_system.update(dt)

    if level_text_brightness > 0.0:
        level_text_brightness -= dt

    return True

def draw():
    surface.blit(stars, (0, 0))

    particle_system.draw(surface)

    player1.draw(surface)

    for asteroid in asteroids:
        asteroid.draw(surface)
        #surface.blit(ast, astrect)
    for asteroid2 in asteroids2:
        asteroid2.draw(surface)
        #surface.blit(ast2, ast2rect)
    for asteroid3 in asteroids3:
        asteroid3.draw(surface)
        #surface.blit(ast3, ast3rect)

    surf_level = fonts[16].render("Level: "+str(level), True, (255,255,255))
    surface.blit(surf_level,(10,10))

    surf_lives = fonts[16].render("Lives: "+str(max([player1.lives,0])), True, (255,255,255))
    surface.blit(surf_lives,(10,25))
        
    surf_score = fonts[16].render("Score: "+str(player1.score), True, (255,255,255))
    surface.blit(surf_score,(screen_size[0]-surf_score.get_width()-10,10))
    
    surf_highscore = fonts[16].render("High Score: "+str(hs), True, (255,255,255))
    surface.blit(surf_highscore,(screen_size[0]-surf_highscore.get_width()-10,25))

    if player1.lives >= 0:
        surf_remain = fonts[16].render("Asteroids Left: "+str(len(asteroids)), True, (255,255,255))
        surface.blit(surf_remain,(10,screen_size[1]-surf_remain.get_height()-10))
    
        if level_text_brightness > 0.0:
            col = rndint(255.0*level_text_brightness)
            surf_level = fonts[32].render("Level "+str(level), True, (col,col,col),(0,0,0))
            pos = [
                (screen_size[0]/2.0)-(surf_level.get_width()/2.0),
                (screen_size[1]/2.0)-(surf_level.get_height()/2.0)
            ]
            surface.blit(surf_level,pos,special_flags=BLEND_MAX)
    else:
        surf_level = fonts[32].render("F2 Starts New Game", True, (255,255,255),(0,0,0))
        pos = [
            (screen_size[0]/2.0)-(surf_level.get_width()/2.0),
            (screen_size[1]/2.0)-(surf_level.get_height()/2.0)
        ]
        surface.blit(surf_level,pos,special_flags=BLEND_MAX)

    #surf_fps = fonts[16].render("FPS: "+str(round(clock.get_fps(),1)), True, (255,255,255))
    #surface.blit(surf_fps,(screen_size[0]-surf_fps.get_width()-10,screen_size[1]-surf_fps.get_height()-10))
    
    pygame.display.flip()

def main():
    global clock

    load_hs()
    
    target_fps = 60
    dt = 1.0/float(target_fps)
    
    reset_game()
    clock = pygame.time.Clock()
    while True:
        if not get_input(dt): break
        if not update(dt): break
        draw()
        clock.tick(target_fps)
    pygame.quit()

    write_hs()
if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
        pygame.quit()
        input()
