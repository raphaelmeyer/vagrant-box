#!/usr/bin/python

import os

from image.image import Image

def main():
  script_dir = os.path.dirname(os.path.realpath(__file__))

  image = Image(script_dir, 'config.json')
  image.create()

if __name__ == "__main__":
  main()

