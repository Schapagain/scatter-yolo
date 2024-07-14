from os import listdir
from os.path import isfile, join
import random
import math


class Utility:

    @staticmethod
    def getFilePathsFromDirectory(dir_path: str):
        return [
            join(dir_path, f) for f in listdir(dir_path) if isfile(join(dir_path, f))
        ]

    @staticmethod
    def randomizeWithinVariance(val: int | float, maxVariance=0.2) -> int | float:
        new_val = round(val * (1 + random.uniform(-maxVariance, 0)))
        return new_val

    @staticmethod
    def centerToBoundingBox(
        center_coords: tuple[int, int], size: tuple[int, int]
    ) -> tuple[int, int, int, int]:
        center_x, center_y = center_coords
        width, height = size
        top_left_x = round(center_x - width / 2)
        top_left_y = round(center_y - height / 2)
        bot_right_x = round(center_x + width / 2)
        bot_right_y = round(center_y + height / 2)
        return (top_left_x, top_left_y, bot_right_x, bot_right_y)

    @staticmethod
    def boundingBoxToCenter(
        box_coords: tuple[int, int, int, int], box_size: tuple[int, int]
    ) -> tuple[int, int]:
        top_left_x, top_left_y, *_ = box_coords
        center_x = round(top_left_x + box_size[0] / 2)
        center_y = round(top_left_y + box_size[1] / 2)
        return (center_x, center_y)

    @staticmethod
    def getRandomCoordinate(
        center: tuple[int, int], max_radius: int
    ) -> tuple[int, int]:
        random_radius = random.randrange(0, max_radius)
        random_angle = random.random() * math.pi * 2
        center_x, center_y = center
        random_coord = (
            round(center_x + random_radius * math.sin(random_angle)),
            round(center_y + random_radius * math.cos(random_angle)),
        )
        return random_coord

    @staticmethod
    def translateBoxInPolarCoords(
        curr_bounds: tuple[int, int, int, int], deltaR: float | int, dir: float
    ):
        top_left_x, top_left_y, bot_right_x, bot_right_y = curr_bounds
        next_top_left_x = deltaR * math.sin(dir) + top_left_x
        next_top_left_y = deltaR * math.cos(dir) + top_left_y
        next_bot_right_x = deltaR * math.sin(dir) + bot_right_x
        next_bot_right_y = deltaR * math.cos(dir) + bot_right_y
        next_bounds = tuple(
            map(
                lambda x: round(x),
                (next_top_left_x, next_top_left_y, next_bot_right_x, next_bot_right_y),
            )
        )
        return next_bounds
