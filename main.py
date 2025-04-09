import pygame
import random
import math
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import tkinter as tk

def on_close():
    global solar_system_sim, planets_sim
    solar_system_sim = solar_system_sim.get()
    planets_sim = planets_sim.get()
    root.destroy()

root = tk.Tk()

solar_system_sim = tk.BooleanVar(value=False)
planets_sim = tk.BooleanVar(value=False)

solar_system_sim_label = tk.Label(root,text="solar system simulation")
solar_system_sim_label.pack()
check_solar_system_sim = tk.Checkbutton(root,variable=solar_system_sim)
check_solar_system_sim.pack()

planet_sim_label = tk.Label(root,text="random planet simulation")
planet_sim_label.pack()
check_planet_sim_label = tk.Checkbutton(root,variable=planets_sim)
check_planet_sim_label.pack()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

pygame.init()
display = (1200, 800)
pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

camera_distance = 30
camera_x = 0
camera_y = 0
G = 0.00989

PLANETS = [
    ("mercury", 0.1, 0.0166, (169, 169, 169)),
    ("venus", 0.15, 0.2447, (255, 198, 73)),
    ("earth", 0.2, 0.3, (100, 149, 237)),
    ("mars", 0.12, 0.0323, (188, 39, 50)),
    ("jupiter", 0.4, 9.5388, (255, 165, 0)),
    ("saturn", 0.35, 2.8562, (238, 232, 205)),
    ("uranus", 0.25, 0.4364, (173, 216, 230)),
    ("neptune", 0.23, 0.5273, (0, 0, 128)),
    #("white hole", 1, -50000, (255,255,255)),
    #("black hole", 1, 50000, (0,0,0)),
    ("sun", 0.5, 10000.0, (255, 255, 0))
]

solar_system = [
    ("sun", 0.5, 10000.0, (255, 255, 0), (0, 0, 0), (0, 0, 0), [0, 0, 0]),
    #("mercury", 0.1, 0.0166, (169, 169, 169), (0.387, 0, 0), [0, 15.984, 0]),
    ("venus", 0.07, 0.2447, (255, 198, 73), (0.723, 0, 0), [0, 11.69, 0]),
    ("earth", 0.075, 0.3, (100, 149, 237), (1.0, 0, 0), [0, 9.94, 0]),
    ("mars", 0.04, 0.0323, (188, 39, 50), (1.524, 0, 0), [0, 8.06, 0]),
    ("jupiter", 0.25, 9.5388, (255, 165, 0), (5.201, 0, 0), [0, 4.37, 0]),
    ("saturn", 0.22, 2.8562, (238, 232, 205), (9.553, 0, 0), [0, 3.22, 0]),
    ("uranus", 0.12, 0.4364, (173, 216, 230), (19.188, 0, 0), [0, 2.27, 0]),
    ("neptune", 0.11, 0.5273, (0, 0, 128), (30.107, 0, 0), [0, 1.81, 0])
]

class Planet:
    def __init__(self, name, radius, mass, color, position, velocity):
        self.name = name
        self.radius = radius
        self.mass = mass
        self.color = color
        self.position = list(position)
        if velocity == 0:
            if name != "sun":
                self.velocity = [random.random(), 5*(random.random()), (random.random())]
            else:
                self.velocity = [0, 0, 0]
        else:
            self.velocity = list(velocity)

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glColor3f(self.color[0] / 255, self.color[1] / 255, self.color[2] / 255)
        quad = gluNewQuadric()
        gluSphere(quad, self.radius, 32, 32)
        glPopMatrix()

    def update_position(self, planets, dt):
        for other in planets:
            if other != self:
                dx = other.position[0] - self.position[0]
                dy = other.position[1] - self.position[1]
                dz = other.position[2] - self.position[2]
                distance = math.sqrt(dx * dx + dy * dy + dz * dz)

                if distance < (self.radius + other.radius):
                    continue

                force = G * (self.mass * other.mass) / (distance ** 2)

                v_multi = force / distance / self.mass * dt
                self.velocity[0] += v_multi * dx
                self.velocity[1] += v_multi * dy
                self.velocity[2] += v_multi * dz

        self.position = [self.position[i]+self.velocity[i]*dt for i in range(3)]


planets = []

sun = Planet("sun", 0.5, 10000.0, (255, 255, 0), (0.0, 0.0, 0.0), 0)

def get_world_coordinates(x, y):
    viewport = glGetIntegerv(GL_VIEWPORT)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)

    y = viewport[3]-y

    wx1, wy1, wz1 = gluUnProject(x, y, 1, modelview, projection, viewport)
    wx2, wy2, wz2 = gluUnProject(x, y, 0, modelview, projection, viewport)

    ray_dir = [wx2 - wx1, wy2 - wy1, wz2 - wz1]
    length = math.sqrt(sum(d * d for d in ray_dir))
    ray_dir = [d / length for d in ray_dir]

    t = -wz1 / ray_dir[2]
    print([wx1 + ray_dir[0] * t,wy1 + ray_dir[1] * t,0],"1")
    return [wx1 + ray_dir[0] * t,wy1 + ray_dir[1] * t,0]

def spawn_planet(x, y, L):
    world_pos = get_world_coordinates(x, y)
    #print(world_pos)
    if L != 1:
        planet_data = random.choice(PLANETS)
    else:
        planet_data = PLANETS[-1]
    new_planet = Planet(planet_data[0], planet_data[1], planet_data[2], planet_data[3], world_pos, 0)
    planets.append(new_planet)

glEnable(GL_DEPTH_TEST)

l = 1
dt = 0.0005
running = True
while running and planets_sim:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                spawn_planet(event.pos[0], event.pos[1],l)
                l += 1

        if event.type == pygame.MOUSEMOTION:
            if event.buttons[2]:
                camera_x += event.rel[0] * 0.03
                camera_y -= event.rel[1] * 0.03

        if event.type == pygame.MOUSEWHEEL:
            camera_distance -= event.y * 1.0
            camera_distance = max(5.0, min(camera_distance, 100.0))

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            planets = []
            l = 1

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
    glTranslatef(camera_x, camera_y, -camera_distance)

    for planet in planets:
        planet.update_position(planets, dt)
        planet.draw()

    pygame.display.flip()

solar_system_objects = []
def spawn_planet2(planet_data):
    new_planet = Planet(planet_data[0],planet_data[1],planet_data[2],planet_data[3],planet_data[4],planet_data[5])
    solar_system_objects.append(new_planet)

camera_distance = 50
n = 1
while running and solar_system_sim:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            if event.buttons[2]:
                camera_x += event.rel[0] * 0.03
                camera_y -= event.rel[1] * 0.03

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if n == 1:
                    for i in solar_system:
                        spawn_planet2(i)
                    n += 1
                #else:
                    #spawn_planet(event.pos[0],event.pos[1],n)


        if event.type == pygame.MOUSEWHEEL:
            camera_distance -= event.y * 1.0
            camera_distance = max(5.0, min(camera_distance, 100.0))

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluPerspective(45, (display[0] / display[1]), 0.1, 90.0)
    glTranslatef(camera_x, camera_y, -camera_distance)

    for celestial_object in solar_system_objects:
        celestial_object.update_position(solar_system_objects,dt)
        celestial_object.draw()

    pygame.display.flip()