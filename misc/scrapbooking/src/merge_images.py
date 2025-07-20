#!/usr/bin/env python3

import os

class ImageMerger:
  def __init__(self, image_directory, block_size):
    self.image_directory = image_directory
    self.block_size = block_size

  # list all images in the dir
  def list_images(self):
    images = sorted(os.listdir(self.image_directory))
    return images

  def get_largest_image_size(self):
    # get the largest image size
    largest_size = 0
    for image in self.list_images():
      size = os.path.getsize(f'{self.image_directory}/{image}')
      if size > largest_size:
        largest_size = size
    return largest_size

  def merge_images(self, output_file_name):
    output = open(output_file_name, "wb")
    num_blocks = (self.get_largest_image_size() // self.block_size) + 1

    for block_num in range(num_blocks):
      for image in self.list_images():
        with open(f'{self.image_directory}/{image}', "rb") as f:
          offset = block_num * self.block_size
          data_remaining = os.path.getsize(f'{self.image_directory}/{image}') - offset
          if data_remaining <= 0:
            output.write(b'\x00' * self.block_size)
            continue
          f.seek(block_num * self.block_size)
          if data_remaining < self.block_size:
            padding = self.block_size - (os.path.getsize(f'{self.image_directory}/{image}') - offset)
            output.write(f.read(data_remaining))
            output.write(b'\x00' * padding)
          else:
            output.write(f.read(self.block_size))
    output.close()

def main():
  image_directory = "images"
  merger = ImageMerger(image_directory, 1024)
  merger.merge_images("warped.png") 

if __name__ == "__main__":
    main()