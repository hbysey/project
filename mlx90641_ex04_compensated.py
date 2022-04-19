import seeed_mlx9064x
import cv2

import os
import math
import time

import numpy as np
import pygame
import busio
import board

from scipy.interpolate import griddata
from colour import Color

import RPi.GPIO as GPIO

TrigPin = 16
EchoPin = 20
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TrigPin,GPIO.OUT)
GPIO.setup(EchoPin, GPIO.IN)

# low range of the sensor (this will be blue on the screen)
MINTEMP = 10.0

# high range of the sensor (this will be red on the screen)
MAXTEMP = 35.0

# how many color values we can have
COLORDEPTH = 1024

os.putenv("SDL_FBDEV", "/dev/fb1")
# pylint: disable=no-member
pygame.init()
# pylint: enable=no-member

# pylint: disable=invalid-slice-index
points = [(math.floor(ix / 16), (ix % 16)) for ix in range(0, 192)]
grid_x, grid_y = np.mgrid[0:11:48j, 0:15:36j]
# pylint: enable=invalid-slice-index

# sensor is an 8x8 grid so lets do a square
height = 360
width = 480

# the list of colors we can choose from
blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

# create the array of colors
colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

displayPixelWidth = width / 30
displayPixelHeight = height / 30

lcd = pygame.display.set_mode((width, height))

lcd.fill((255, 0, 0))

pygame.display.update()
pygame.mouse.set_visible(False)

lcd.fill((0, 0, 0))
pygame.display.update()

# some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def distance():
    GPIO.output(TrigPin, True)
    time.sleep(0.00001)
    GPIO.output(TrigPin, False)
    
    while GPIO.input(EchoPin) == 0 :
        start_time = time.time()
    
    while GPIO.input(EchoPin) == 1 :
        end_time = time.time()
    
    duration = end_time - start_time
    distanceCm = duration * 17000
    distanceCm = round(distanceCm, 2)
    return distanceCm

# let the sensor initialize
time.sleep(0.1)

def main():
    mlx = seeed_mlx9064x.grove_mxl90641()
    frame = [0] * 192
    mlx.refresh_rate = seeed_mlx9064x.RefreshRate.REFRESH_8_HZ  # The fastest for raspberry 4 
    time.sleep(1)
    
    while True:
        mlx.getFrame(frame)
        if frame[0] != 'nan':
            
            pixels = frame
            pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
            bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")
            
            # draw everything
            for ix, row in enumerate(bicubic):
                for jx, pixel in enumerate(row):
                    pygame.draw.rect(
                        lcd,
                        colors[constrain(int(pixel), 0, COLORDEPTH - 1)],
                        (
                            displayPixelHeight * ix,
                            displayPixelWidth * jx,
                            displayPixelHeight,
                            displayPixelWidth,
                        ),
                    )

            pygame.display.update()
            
            max_temp = float(max(frame))
            message = round(max_temp, 2)
            print("Max_temp = " , message)
            
            result = [num for num in frame if num < 35.0]
            
            result.sort(reverse=True)
            mean_temp = sum(result[0:5])/5.0           
            print("mean_temp = ", round(mean_temp, 2))
            
            distanceCm = distance()
            print("cm:",distanceCm)
            if distanceCm > 50.0:
                distanceCm = 50.0
            compen_temp = round((mean_temp + (2.0 + distanceCm/25)), 2)
            print("compen_temp = ", compen_temp)
            
            
        if cv2.waitKey(1) == ord('q'):
            break
        
        
    cv2.destoryAllWindows()
    GPIO.cleanup()
    
if __name__  == '__main__':
    main()
    