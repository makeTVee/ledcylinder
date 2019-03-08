# WS2812 LED Matrix Cylinder
# by M Oehler
# https://hackaday.io/project/162035-led-matrix-cylinder
# Released under a "Simplified BSD" license

import time, random, sys
import argparse
from font5x3 import font5x3
from itertools import chain
import numpy

# False for simulation mode, True for using a Raspberry PI
PI=False

if PI:
    from neopixel import *
else:
    import pygame
    from pygame.locals import *

SIZE=20;
FPS = 15
WINDOWWIDTH = 400
WINDOWHEIGHT = 100
BOXSIZE = 20
BOARDWIDTH = 20
BOARDHEIGHT = 5
BLANK = '.'

mask = bytearray([1,2,4,8,16,32,64,128])

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (255,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 255,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 255)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (255, 255,   0)
LIGHTYELLOW = (175, 175,  20)
CYAN        = (  0, 255, 255)
MAGENTA     = (255,   0, 255)
ORANGE      = (255, 100,   0)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (BLUE,GREEN,RED,YELLOW,CYAN,MAGENTA,ORANGE)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)

# LED strip configuration:
LED_COUNT      = 100     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

if PI:
    # Create NeoPixel object 
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Init lib
    strip.begin()
else:
    strip=[]

# Zig-Zag resorting array for cylinder matrix
matrix =  [0, 9, 10, 19, 20, 29, 30, 39, 40, 49, 50, 59, 60, 69, 70, 79, 80, 89, 90, 99,
	1, 8, 11, 18, 21, 28, 31, 38, 41, 48, 51, 58, 61, 68, 71, 78, 81, 88, 91, 98,
	2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 82, 87, 92, 97,
	3, 6, 13, 16, 23, 26, 33, 36, 43, 46, 53, 56, 63, 66, 73, 76, 83, 86, 93, 96,
	4, 5, 14, 15, 24, 25, 34, 35, 44, 45, 54, 55, 64, 65, 74, 75, 84, 85, 94, 95]

display_cursor = 0 ;

display = [[0 for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHT)]

# Main program logic follows:
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    if not PI:
		# init pygame simualator
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        DISPLAYSURF = pygame.display.set_mode((20*SIZE, 5*SIZE))
        BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
        BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
        pygame.display.set_caption('Pi Cylinder')
        DISPLAYSURF.fill(BGCOLOR)
        pygame.display.update()
    try:

        while True:
            if not PI:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
            print ('Color wipe animations.')

            scroll_text_display('LED MATRIX CYLINDER',random.randrange(0,0xFFFFFF,2),40)
            colorRandom(strip, 5000)
            clear_display()
            colorWipe(strip, 0, 255, 0,25)  # Blue wipe
            colorWipe(strip, 0, 0, 255,25)  # Green wipe
            colorWipe(strip, 255, 0, 0,25)  # Blue wipe
            clear_display()

    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, 0,0,0, 10)

def colorWipe(strip, r,g,b, wait_ms=50):
    for i in range(LED_COUNT):
        draw_pixel(int(i%20),int(i/20),r,g,b)
        time.sleep(wait_ms/1000.0)

def colorRandom(strip, cycles):
    for i in range(0,cycles):
        a= random.randrange(0,200,1);
        c=random.randrange(0,0xFFFFFF,1);
        drawPixel(int(a%20),int(a/20),c)
        time.sleep(1/1000.0)

def drawPixel(x,y,color):
    if color == BLANK:
        return
    if PI:
        if (x>=0 and y>=0 and color >=0):
            strip.setPixelColor(y*20+x,color)
            strip.show()
    else:
        pygame.draw.rect(DISPLAYSURF, (color>>16,(color>>8)&0xFF,color&0xFF), (x*SIZE+1, y*SIZE+1, SIZE-2, SIZE-2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()

def clear_display():
    global display
    display = [[0 for x in range(BOARDWIDTH)] for y in range(BOARDHEIGHT)]
    draw_display()

def draw_display():
    if PI:
        for x in range(0,20):
            for y in range(0,5):
                strip.setPixelColor(matrix[y*20+x],(Color(display[y][x]>>8)&0xFF, display[y][x]>>16, display[y][x]&0xFF))
        strip.show()
    else:
        for x in range (0,20):
            for y in range(0,5):
                pygame.draw.rect(DISPLAYSURF, (display[y][x]>>16,(display[y][x]>>8)&0xFF,display[y][x]&0xFF), (x*SIZE+1, y*SIZE+1, SIZE-2, SIZE-2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()

def print_char(char,cursor):
    for i in range(0,3):
        a=font5x3[ord(char)][i]
        for j in range(0,5):
            if a&mask[j]:
                draw_pixel(cursor+i,j,255,0,0)
            else:
                draw_pixel(cursor+i,j,0,0,0)

def scroll_text_display(string,color,wait_ms):
    global display
    cursor=0
    for c in range(0,len(string)):
        for i in range(0,3):
            a=font5x3[ord(string[c])][i]
            for j in range(0,5):
                if a&mask[j]:
                    display[j][19]=color;
                else:
                    display[j][19] =0;
            draw_display()
            display = numpy.roll(display,-1,axis=1)
            time.sleep(wait_ms / 1000.0)
        # add zero coulumn after every letter
        for j in range(0, 5):
            display[j][19] = 0;
        draw_display()
        display = numpy.roll(display,-1,axis=1)
        time.sleep(wait_ms / 1000.0)
    #shift text out of display (20 pixel)
    for i in range(0,20):
        for j in range(0, 5):
            display[j][19] = 0;
        draw_display()
        display = numpy.roll(display, -1, axis=1)
        time.sleep(wait_ms / 1000.0)


def draw_pixel(x,y,r,g,b):
    if PI:
        strip.setPixelColor(matrix[y*20+x],Color(g, r, b))
        strip.show()
    else:
        pygame.draw.rect(DISPLAYSURF, (r,g,b), (x*SIZE+1, y*SIZE+1, SIZE-2, SIZE-2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()


if __name__ == '__main__':
    main()