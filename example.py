#!/usr/bin/env python3
import time
import pygame
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import lcd

pygame.mixer.init()

image = []

sounds = {
   "tink": "sounds/Tink.aiff.wav",
   "ow": "sounds/Basso.aiff.wav",
   "submarine": "sounds/Submarine.aiff.wav"
}

def play(sound):
   pygame.mixer.music.set_volume(0.08)
   pygame.mixer.music.load(sounds[sound])
   pygame.mixer.music.play()
   while pygame.mixer.music.get_busy() == True:
      continue

def load_image():
   global image
   img = mpimg.imread('images/greg.png')
   s = ""
   pow=256
   for j in range(0,128):
      byte = 0
      line = []
      for i in range(0, 320):
         col = i + 40
         row = j + 100
         k = not int((img[row][col][0]+img[row][col][1]+img[row][col][2])/3)
         pow = pow / 2
         byte += int(k * pow)
         if pow == 1:
            x=int((i-7)/8)
            line.append(byte)
            pow = 256
            byte = 0
      # print(s)
      image.append(line)
   # imgplot = plt.imshow(img)
   # plt.show()
   image = image[::-1]

def print_image():
   for col in range(0,40):
      s=""
      for row in range(0,128):
         s += "("+str(row)+","+str(col)+","+str(image[row][col])+")"
      print(s)

def box(x0, y0, x1, y1, pixel=1):
   for y in range(y0, y1+1):
      lcd.set_pixel(x0, y, pixel)
   for x in range(x0, x1+1):
      lcd.set_pixel(x, y1, pixel)
   for y in range(y1, y0-1, -1):
      lcd.set_pixel(x1, y, pixel)
   for x in range(x1, x0-1, -1):
      lcd.set_pixel(x, y0, pixel)

def hline(x0, y0, x1, y1, pixel=1):
   for x in range(x0, x1+1):
      lcd.set_pixel(x, y0, pixel)

def image_example():
   global image
   load_image()
   lcd.clear_screen(0x55, 0xaa)
   play("tink")
   lcd.display_image(image)
   play("tink")

def box_example():
   lcd.clear_screen(0x55, 0xaa)
   play("tink")
   box(10,10,310,120, 0)
   play("tink")


def hline_example():
   lcd.defer(True)
   lcd.clear_screen(0x55, 0xaa)
   play("tink")
   for y in range(127, -1, -1):
      hline(0, y, 319, 0, 0)
   lcd.defer(False)
   play("tink")

def text_example():
   for y in range(0, 120, 8):
      lcd.clear_screen()
      lcd.print_at(y, y, "Hello World!")
      time.sleep(0.5)

lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
shortLorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do e"

def proportional_text_example():
   lcd.defer(True)
   lcd.clear_screen()
   x = 0
   y = 0
   h = 12
   uppers = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
   lowers = "abcdefghijklmnopqrstuvwxyz"
   symbols = "0123456789!@#$%^&*(){}[]|\\<>?,./:;'\"-~`=_+"
   lcd.print_at(x, y, uppers)
   y += h
   lcd.print_at(x, y, uppers, 5)
   y += h
   lcd.print_at(x, y, uppers, 0)
   y += h
   lcd.print_at(x, y, lowers)
   y += h
   lcd.print_at(x, y, lowers, 5)
   y += h
   lcd.print_at(x, y, lowers, 0)
   y += h
   lcd.print_at(x, y, symbols)
   y += h
   lcd.print_at(x, y, symbols, 5)
   y += h
   lcd.print_at(x, y, symbols, 0)
   lcd.defer(False)

def lorem_example():
   longLorem = lorem+lorem+lorem
   lcd.defer(True)
   lcd.clear_screen()
   y=120
   x=0
   for i in range(0, len(longLorem), 64):
      lcd.print_at(x, y, longLorem[i:i+64], 0)
      y -= 8
      if y<0: break
   lcd.defer(False)

def main():
   lcd.setup(0,True)
   # image_example()
   # box_example()
   # hline_example()
   proportional_text_example()
   # lorem_example()
   lcd.teardown()
   play("submarine")
main()
