from . import utils
from PIL import Image, ImageDraw, ImageOps
import math
import random
import os
import sys
from datetime import datetime


class ScatterObject:
    def __init__(self, image: Image.Image, type: int):
        self.image = image
        self.type = type


class SyntheticGenerator:
    INVALID_LOCATION = (-1, -1, -1, -1)
    OBJECT_SPACING = 3
    OVERLAP_PIXEL_THRESHOLD = 50000
    RANDOM_LOCATION_RETRIES_LIMIT = 300

    def __init__(
        self,
        object_directories: str,
        backgrounds_dir: str = None,
        object_size: int = 18,
        image_size: int = 500,
        image_padding: int = 10,
    ):
        self.image_height = image_size
        self.image_width = image_size
        self.object_size = object_size
        self.boundary_radius = math.floor(image_size / 2) - image_padding
        self.scatter_object_paths = [
            utils.getFilePathsFromDirectory(obj_dir) for obj_dir in object_directories
        ]
        self.backgrounds_path = (
            utils.getFilePathsFromDirectory(backgrounds_dir)
            if backgrounds_dir
            else None
        )
        self.has_backgrounds = self.backgrounds_path is not None

    def _getNextObject(self, scatter_ratios: list[float]) -> ScatterObject:
        r = random.random()

        cum_ratio = 0
        for i, ratio in enumerate(scatter_ratios):
            cum_ratio += ratio
            if r <= cum_ratio or i == len(scatter_ratios) - 1:
                obj_image = (
                    Image.open(random.choice(self.scatter_object_paths[i]))
                    .resize((self.object_size, self.object_size))
                    .convert("RGBA")
                )
                return ScatterObject(obj_image, i)

    def _isCoordinateEmpty(self, curr_location, pixels):
        next_location_pixels = self._calculateLocationPixels(
            pixels, (curr_location[0], curr_location[1])
        )
        next_location_pixels_sum = sum(map(lambda tup: sum(tup), next_location_pixels))
        return next_location_pixels_sum < SyntheticGenerator.OVERLAP_PIXEL_THRESHOLD

    def _isCoordinateWithinBounds(self, curr_location):
        top_left_x, top_left_y, bot_right_x, bot_right_y = curr_location
        overflows_horizontal = (
            top_left_x < 0
            or bot_right_x < 0
            or top_left_x > self.image_width - self.object_size
            or bot_right_x > self.image_width - self.object_size
        )
        overflows_vertical = (
            top_left_y < 0
            or bot_right_y < 0
            or top_left_y > self.image_height - self.object_size
            or bot_right_y > self.image_height - self.object_size
        )

        curr_center = utils.boundingBoxToCenter(
            curr_location,
            box_size=(
                self.object_size,
                self.object_size,
            ),
        )
        image_center = (self.image_width / 2, self.image_height / 2)
        overflows_bounding_circle = (
            math.dist(curr_center, image_center) > self.boundary_radius
        )
        return not (
            overflows_horizontal or overflows_vertical or overflows_bounding_circle
        )

    def _getNextSpawnLocation(
        self,
        curr_location: tuple[int, int, int, int],
        pixels: list[int],
        separation_chance: float = 0,
    ):
        next_location = SyntheticGenerator.INVALID_LOCATION
        is_next_location_empty = False
        rand_num = random.random()
        angle_choices = [i * math.pi / 4 for i in range(1, 9)]
        if (
            curr_location == SyntheticGenerator.INVALID_LOCATION
            or rand_num < separation_chance
        ):
            next_location_center = utils.getRandomCoordinate(
                (round(self.image_width / 2), round(self.image_height / 2)),
                self.boundary_radius,
            )
            next_location = utils.centerToBoundingBox(
                next_location_center,
                (self.object_size, self.object_size),
            )
        else:
            random.shuffle(angle_choices)
            next_angle = angle_choices.pop()
            next_location = utils.translateBoxInPolarCoords(
                curr_location,
                self.object_size + SyntheticGenerator.OBJECT_SPACING,
                next_angle,
            )

        is_next_location_empty = self._isCoordinateEmpty(next_location, pixels)
        is_next_location_within_bounds = self._isCoordinateWithinBounds(next_location)
        retry_count = 0
        while (
            not (is_next_location_empty and is_next_location_within_bounds)
            and retry_count < SyntheticGenerator.RANDOM_LOCATION_RETRIES_LIMIT
        ):
            if len(angle_choices) == 0:
                next_location_center = utils.getRandomCoordinate(
                    (round(self.image_width / 2), round(self.image_height / 2)),
                    self.boundary_radius,
                )
                next_location = utils.centerToBoundingBox(
                    next_location_center,
                    (
                        self.object_size,
                        self.object_size,
                    ),
                )
            else:
                next_location = utils.translateBoxInPolarCoords(
                    curr_location,
                    self.object_size + SyntheticGenerator.OBJECT_SPACING,
                    angle_choices.pop(),
                )
            is_next_location_empty = self._isCoordinateEmpty(next_location, pixels)
            is_next_location_within_bounds = self._isCoordinateWithinBounds(
                next_location
            )
            retry_count += 1

        return (
            next_location
            if is_next_location_empty and is_next_location_within_bounds
            else SyntheticGenerator.INVALID_LOCATION
        )

    def _calculateLocationPixels(self, pixels, curr_location_top):
        top_offset = self.image_width * curr_location_top[1]
        left_offset = curr_location_top[0]
        location_pixels = []

        for _ in range(self.object_size):
            location_pixels.extend(
                pixels[
                    top_offset
                    + left_offset : top_offset
                    + left_offset
                    + self.object_size
                ]
            )
            top_offset += self.image_width
        return location_pixels

    def generete(
        self,
        scatter_ratios: list[float] = None,
        number_images: int = 10,
        min_objects: int = 50,
        max_objects: int = 100,
        save_dir: str = "scatter_yolo_images",
        cluster_idx: float = 1,
        verbose: bool = False,
        animate: bool = False,
    ) -> None:
        if not scatter_ratios:
            scatter_ratios = [1 / len(self.scatter_object_paths)] * len(
                self.scatter_object_paths
            )
        image_count = 0

        if not os.path.isdir(save_dir):
            # exist_ok=True handles race conditions when run in multiple threads
            os.makedirs(save_dir, exist_ok=True)

        for i in range(number_images):
            start_time = datetime.now()
            im = Image.new("RGBA", (self.image_width, self.image_height))
            backgroundIm = (
                (
                    Image.open(random.choice(self.backgrounds_path))
                    .resize((self.image_width, self.image_height))
                    .convert("RGBA")
                    .copy()
                )
                if self.has_backgrounds
                else im
            )
            next_spawn_location = SyntheticGenerator.INVALID_LOCATION
            total_count = 0
            counts = [0] * len(self.scatter_object_paths)
            annotations = []
            animation_frames = []

            while total_count < random.randint(min_objects, max_objects) and (
                total_count == 0
                or next_spawn_location != SyntheticGenerator.INVALID_LOCATION
            ):
                next_object = self._getNextObject(scatter_ratios)
                pixels = list(im.getdata())
                next_spawn_location = self._getNextSpawnLocation(
                    next_spawn_location, pixels, separation_chance=1 - cluster_idx
                )
                next_spawn_center = utils.boundingBoxToCenter(
                    next_spawn_location,
                    (self.object_size, self.object_size),
                )
                im.paste(next_object.image, next_spawn_location, next_object.image)
                if animate:
                    bg_copy = backgroundIm.copy()
                    bg_copy.paste(im, mask=im)
                    animation_frames.append(bg_copy)
                counts[next_object.type] += 1
                annotations.append(
                    f"{next_object.type} {next_spawn_center[0]/self.image_width:.4f} {next_spawn_center[1]/self.image_height:.4f} {self.object_size/self.image_width} {self.object_size/self.image_height}\n"
                )
                total_count += 1

            file_name = f"{save_dir}/{image_count}-{'-'.join(list(map(str,counts)))}"
            if animate:
                animation_frames[0].save(
                    f"{file_name}.gif",
                    save_all=True,
                    append_images=animation_frames[1:],
                    duration=2,
                )
            backgroundIm.paste(im, mask=im)

            backgroundIm.save(f"{file_name}.png")
            if verbose:
                print(
                    f"Generated {file_name}.png in {(datetime.now() - start_time).total_seconds():.3f} seconds."
                )
            with open(f"{file_name}.txt", "w+") as f:
                f.writelines(annotations)
            image_count += 1
