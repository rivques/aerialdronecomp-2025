import math
import pygame
from codrone_edu.drone import * 
import time
print("pairing with drone...")
drone = Drone()
drone.pair()
print("paired")

pygame.init()

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

last_update = time.time()
time.sleep(0.1)
angle_offset = 0
last_angle = 0
last_angle_update = time.time()

def repeat_speed_change(speed, n=5, dt=0.01):
    for i in range(n):
        drone.speed_change(speed)
        time.sleep(dt)

while True:
    done = False
    for event in pygame.event.get(): # this is needed for some reason
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("slowing down...")
                repeat_speed_change(1)
            elif event.key == pygame.K_s:
                print("override: slowing down...")
                repeat_speed_change(1)
            elif event.key == pygame.K_f:
                print("override: speeding up...")
                repeat_speed_change(3)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                print("speeding up...")
                repeat_speed_change(3)
    if done:
        break