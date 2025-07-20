#!/usr/bin/env python3

import os

output_dir = "output"
input_file = "warped.png"
block_size = 1024
num_images = 3

def unmerge_image(image_file_name, num_images, output_dir):
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  offset = 0
  with open(image_file_name, "rb") as f:
    while True:
      for i in range(num_images):
        image_data = f.read(block_size)
        if not image_data:
          return
        with open(f"{output_dir}/image{i}.png", "ab") as image:
          image.write(image_data)

unmerge_image(input_file, num_images, output_dir)