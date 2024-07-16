# Scatter YOLO

This is a tool to generate synthetic images where provided images of objects are scattered over a white background or over optionally provided background images.

## Installation

> As this is not yet published in PyPI, manual installation is required.

1. Clone this repository to local
   ```bash
   git clone git@github.com:schapagain/scatter-yolo.git
   ```
2. Create a new virtual environment and install `flit`

   ```bash
   conda create -n scatter-yolo flit
   ```

3. In the root project directory run:
   ```
   flit install
   ```
4. Now you can start using the tool with. To check out all the generation options, run:
   ```
   scatter-yolo generate -h
   ```

## Usage Examples

### Scatter one or more objects

    scatter-yolo generate samples/images/fish samples/images/turtles

![29fish-26turtles](./samples/images/scatter_yolo_images/0-29-26.png)

### Add backgrounds

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed

![25fish-29turtles](./samples/images/scatter_yolo_images/0-25-29.png)

### Generate multiple images

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed -c 2

![35fish-23turtles](./samples/images/scatter_yolo_images/0-35-23.png)|![28fish-27turtles](./samples/images/scatter_yolo_images/1-28-27.png)

### Change object ratios

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed -rat 0.2,0.8

![8fish-45turtles](./samples/images/scatter_yolo_images/0-8-45.png)

## Change total object count (approx\*)

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed -min 10 -max 20

![8fish-4turtles](./samples/images/scatter_yolo_images/0-8-4.png)

> \* The exact count of scattered objecs cannot be set, and only min and max counts are accepted. The max parameter is a true maximum, however there might be fewer objects than the min parameters (if there is no space to place enough objects in the image, for example). This is to vary the number of objects in each image when doing bulk generation.

## Change object size

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed -min 10 -max 20 -os 50

![7fish-5turtles](./samples/images/scatter_yolo_images/0-7-5.png)

## Add circular mask

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed -sh circ

![27fish-30turtles](./samples/images/scatter_yolo_images/0-27-30.png)

## Reduce spread

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed -cx 0.8

![28fish-26turtles](./samples/images/scatter_yolo_images/0-28-26.png)

## Generate placement animation

    scatter-yolo generate samples/images/fish samples/images/turtles -b samples/images/ocean_bed -anim yes

![24fish-31turtles](./samples/images/scatter_yolo_images/0-24-31.gif)
