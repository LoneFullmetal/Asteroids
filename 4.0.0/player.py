import pygame
from math import *

import bullet
import random

class Player:
    thrust = 360.0
    
    def __init__(self, position):
        self.position = list(position)
        self.velocity = [0.0,0.0]

        self.angle = 180.0

        self.fire = 0.0
        self.bullets = []

        #List of (angle,radius) pairs.
        self.rel_points = [[0, 20], [-140, 20], [180, 7.5], [140, 20]]
        scale = 0.5
        for i in range(len(self.rel_points)):
            self.rel_points[i] = (radians(self.rel_points[i][0]),scale*self.rel_points[i][1])
        
        self.thrust_append = 0

        self.alive = True
        self.dying = False
        self.lives = 1
        self.time_invincibility = 0

        self.score = 0
        
    def level_up(self, new_level):
        
        self.bullets = []
        
        if new_level % 5 == 0:
            self.lives += 1

        self.time_invincibility = 1.5

    def shoot(self):
        if self.fire <= 0.0:
            angle_rad = radians(-self.angle+90)
            pos = [
                self.position[0] + 7.5*cos(angle_rad),
                self.position[1] + 7.5*sin(angle_rad)
            ]
            #self.bullets.append(bullet.Bullet(pos,angle_rad))
            self.bullets.append(bullet.Bullet(pos,angle_rad-0.1))
            self.bullets.append(bullet.Bullet(pos,angle_rad+0.1))

            self.fire += 0.1
    def update(self, dt, screen_size):
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] *= -0.5
        elif self.position[0] > screen_size[0]:
            self.position[0] = screen_size[0]
            self.velocity[0] *= -0.5
        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] *= -0.5
        elif self.position[1] > screen_size[1]:
            self.position[1] = screen_size[1]
            self.velocity[1] *= -0.5

        if self.time_invincibility > 0.0:
            self.time_invincibility -= dt
        if self.fire > 0.0:
            self.fire -= dt
        if self.dying != False:
            self.dying -= dt
            if self.dying < 0.0:
                self.dying = False
                
                self.position = [screen_size[0]/2,screen_size[1]/2]
                self.velocity = [0.0,0.0]
                self.time_invincibility = 2.5

                self.lives -= 1
                if self.lives >= 0:
                    self.alive = True

        for b in self.bullets:
            b.update(dt)
            if b.time > 5.0:
                self.bullets.remove(b)
                continue

        self.real_points = []
        for point_angle,point_radius in self.rel_points:
            angle = radians(self.angle) + point_angle
            xp = point_radius * sin(angle)
            yp = point_radius * cos(angle)
            self.real_points.append((
                self.position[0] + xp,
                self.position[1] + yp
            ))
    def collide_bullets(self, asteroids, particle_system, dt):
        for bullet in self.bullets:
            for asteroid in asteroids:
                if asteroid.occluder.intersects(bullet.position):
                    emitter = particle_system.emitters["hit"]
                    emitter.set_position(bullet.position)
                    emitter.set_particle_emit_density(100)
                    emitter._padlib_update(particle_system,dt)
                    emitter.set_particle_emit_density(0)
                        
                    asteroid.hit()
                    
                    self.score += 25
                    
                    if asteroid.health == 0:
                        emitter = particle_system.emitters["shock"]
                        emitter.set_position(asteroid.position)
                        emitter.set_particle_emit_density(100)
                        emitter._padlib_update(particle_system,dt)
                        emitter.set_particle_emit_density(0)
                    
                        asteroids.remove(asteroid)
                        self.score += 250
                        
                    self.bullets.remove(bullet)
                    break
    def collide_asteroids(self, asteroids, particle_system):
        if self.dying: return True
        if self.time_invincibility > 0.0: return True
        
        for asteroid in asteroids:
            for point in self.real_points:
                if asteroid.occluder.intersects(point):
                    asteroids.remove(asteroid)
                    self.score += 250
                    
                    particle_system.emitters["rocket"].set_particle_emit_density(0)
                    particle_system.emitters["turn1"].set_particle_emit_density(0)
                    particle_system.emitters["turn2"].set_particle_emit_density(0)
                    
                    particle_system.emitters["die"].set_position(self.position)
                    particle_system.emitters["die"].set_particle_emit_density(100)
                    particle_system.emitters["die"]._padlib_update(particle_system,0.1)
                    particle_system.emitters["die"].set_particle_emit_density(0)
                    
                    self.dying = 1.0
                    self.alive = False

                    return

    def draw(self, surface):
        for b in self.bullets:
            b.draw(surface)

        if self.alive:        
            color = (0,255,255)
            if self.time_invincibility > 0.0:
                if self.time_invincibility % 0.1 < 0.03:
                    style = random.randint(1, 3)
                    if style == 1:
                        color = (0,0,255)
                    elif style == 2:
                        color = (0,255,0)
                    else:
                        color = (255,0,0)
            pygame.draw.aalines(surface,color,True,self.real_points,True)
























