from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
import csv
from typing import List
from enum import Enum

# CONSTANTS
PIXELS_PER_FOOT = 2.4
SMALL_FONT_SIZE = 6
LARGE_FONT_SIZE = 20
# System dependent. There is a default if we don't specify any font thing.
SMALL_FONT = ImageFont.truetype(font='Roboto-Regular.ttf', size=SMALL_FONT_SIZE)
LARGE_FONT = ImageFont.truetype(font='Roboto-Regular.ttf', size=LARGE_FONT_SIZE)

CIRCLE_HEIGHT = 25
BORDER_WIDTH = 2

HEADER_HEIGHT = 25
SIDE_HEIGHT = 15

COLORS = {
    "SZ 1": "#6D9EEB",
    "SZ 2": "#C9DAF8",
    "SZ 3": "#00FFFF",
    "BLACK": "#000000",
    "WHITE": "#FFFFFF",
    "PINK": "#FF00FF",
}

# default vars for sample line
frontage = 60
depth = 120

def get_pixels_from_feet(distance_in_feet):
  return distance_in_feet * PIXELS_PER_FOOT

def create_rectangle(drawer, text, width, height, color=COLORS["BLACK"], bg=COLORS["PINK"], gradient=None):
    i = Image.new("RGB", (width, height), bg)
    drawer = ImageDraw.Draw(i)
    # TODO: Font
    # TODO: add a border
    # TODO: Wrap text
    drawer.text((5, 5), text, fill=color)

    return i

def rotate(thing_to_rotate, rotation = 0):
    # expand means "make the image bigger if necessary to accomodate"
    return thing_to_rotate.rotate(rotation, expand=1)

def add_obj_to_image(image, rect, top_left):
    image.paste(rect, box=top_left)

def determine_rectangle_placement():
    return (50, 50);

def create_circle_with_number(number, diam):
    # TODO FIGURE OUT TRANSPARENT BG
    i = Image.new("RGB", (diam, diam), COLORS["WHITE"])
    drawer = ImageDraw.Draw(i)

    tl = round((CIRCLE_HEIGHT - SMALL_FONT_SIZE) / 2)
    # TODO: Font
    # TODO: add a border
    # TODO: Wrap text
    drawer.arc((0,0, diam, diam), 0, 360, fill=COLORS["BLACK"], width=BORDER_WIDTH)
    drawer.text((tl, tl), str(number), fill=COLORS["BLACK"])

    return i

# def add_gradient(drawer, rect):
#     print (rect)
#     def interpolate(f_co, t_co, interval):
#         det_co =[(t - f) / interval for f , t in zip(f_co, t_co)]
#         for i in range(interval):
#             yield [round(f + det * i) for f, det in zip(f_co, det_co)]

#     gradient = Image.new('RGBA', rect.size, color=0)

#     f_co = (13, 255, 154)
#     t_co = (4, 128, 30)
#     for i, color in enumerate(interpolate(f_co, t_co, rect.width * 2)):
#         draw.line([(i, 0), (0, i)], tuple(color), width=1)

#     return

def bool_fetcher(row):
    def bool_is_set(key):
        return row[key].strip() != '' or row[key].lower() == 'no'
    return bool_is_set

class SoundZone(Enum):
    SZ_1 = 'SZ 1'
    SZ_2 = 'SZ 2'
    SZ_3 = 'SZ 3'
    NA   = '#N/A'

class CampType(Enum):
    WORK_SUPPORT = 'Work Support Camp'
    ART_SUPPORT = 'Art Support Camp'
    THEME_CAMP = 'Theme Camp'

    @classmethod
    def from_string(s: str) -> 'CampType':
        if s == 'Work Support Camp':
            return CampType.WORK_SUPPORT
        if s == 'Art Support Camp':
            return CampType.ART_SUPPORT
        return CampType.THEME_CAMP

class InteractivityTime(Enum):
    ART_SUPPORT = 'Art Support Camp'
    WORK_SUPPORT = 'Work Support Camp'
    MORNING = 'Morning'
    AFTERNOON = 'Afternoon'
    LATE_AFTERNOON = 'Late Afternoon'
    EVENING = 'Evening'
    LATE_NIGHT = 'Late Night'
    EMPTY = ''
    # TODO: Blank string?

class SoundSize(Enum):
    SMALL = 1
    MEDIUM = 2
    EMPTY = 3

class CampInfo(object):
    def __init__(
            self, width: int, height: int, name: str, camp_type: CampType,
            sound_zone: SoundZone, interactivity_time: InteractivityTime,
            sound_size: SoundSize, neighborhood_preference: List[str],
            coffee: bool, food: bool, fire: bool, fire_circle: bool, kids: bool,
            bar: bool, ada: bool, xxx: bool, trees: bool, uneven_ground: bool,
            rv_count: int):
        self.width = width
        self.height = height
        self.name = name
        self.camp_type = camp_type
        self.sound_zone = sound_zone
        self.interactivity_time = interactivity_time
        self.sound_size = sound_size
        self.neighborhood_preference = neighborhood_preference
        self.coffee = coffee
        self.food = food
        self.fire = fire
        self.fire_circle = fire_circle
        self.kids = kids
        self.bar = bar
        self.ada = ada
        self.xxx = xxx
        self.trees = trees
        self.uneven_ground = uneven_ground
        self.rv_count = rv_count

    def __repr__(self):
        return f'<CampInfo: {self.name}>'

def read_csv():
    with open('./placement-temp.csv') as f:
        reader = csv.DictReader(f)
        camps = []
        for row in reader:
            bool_get = bool_fetcher(row)

            try:
                rv_count = int(row['RVs'])
            except ValueError:
                rv_count = 0
            camp_type = row['Camp Type']  # e.g.  "Theme Camp"
            interactivity_time = row['Interactivity Time/Name Highlight Color']
            sound_size = row['Sound'] # how big their soundsystem is: small, medium, nothing
            sound_zone = row['Sound Zone'] # e.g. "SZ 2"

            camps.append(CampInfo(
                width=int(row['Frontage']),
                height=int(row['Depth']),
                name=row[' '],
                camp_type=camp_type, sound_zone=sound_zone, interactivity_time=interactivity_time, sound_size=sound_size,
                neighborhood_preference=row['neighborhood'].split(' '),
                coffee=bool_get('Coffee'),food=bool_get('Food'), fire=bool_get('Fire'), fire_circle=bool_get('Fire Circle'),
                kids=bool_get('Kids'),bar=bool_get('Bar'), ada=bool_get('ADA'), xxx=bool_get('XXX'),
                uneven_ground=bool_get('Uneven Ground Data'), trees=bool_get('Trees'),
                rv_count=rv_count
            ))
    return camps


def gen_image_for_camp(camp: CampInfo):
    frontage_in_px = round(get_pixels_from_feet(camp.width))
    depth_in_px = round(get_pixels_from_feet(camp.height))

    img = Image.new("RGB", (frontage_in_px, depth_in_px), COLORS["WHITE"])

    draw = ImageDraw.Draw(img)


    # Header
    add_obj_to_image(
        img,
        create_rectangle(draw, camp.sound_zone, frontage_in_px, HEADER_HEIGHT),
        (0,0) # start at top left.
    )

    # Camp Name
    add_obj_to_image(
        img,
        create_rectangle(draw, camp.name, frontage_in_px - SIDE_HEIGHT *2, HEADER_HEIGHT, bg=COLORS["WHITE"]),
        (SIDE_HEIGHT, HEADER_HEIGHT),
    )

    # Left Bar
    left = create_rectangle(draw, "LEFT BAR", depth_in_px - (HEADER_HEIGHT*2), SIDE_HEIGHT)
    add_obj_to_image(
        img,
        left.rotate(-90, expand=1),
        (0, HEADER_HEIGHT) # start at top left of left column
    )

    # Right Bar
    right = create_rectangle(draw, "RIGHT BAR", depth_in_px - (HEADER_HEIGHT*2), SIDE_HEIGHT)
    add_obj_to_image(
        img,
        right.rotate(-90, expand=1),
        (frontage_in_px-SIDE_HEIGHT, HEADER_HEIGHT) # start at top left of right column
    )

    # Footer
    add_obj_to_image(
        img,
        create_rectangle(draw, "FOOTER", frontage_in_px, HEADER_HEIGHT),
        (0, img.height - HEADER_HEIGHT) # start at bottom left, offset by how tall the rectangle is.
    )

    # DIMS
    # (FRONTAGE)
    add_obj_to_image(
        img,
        create_rectangle(draw, str(camp.width), HEADER_HEIGHT, HEADER_HEIGHT, bg=COLORS["WHITE"], color=COLORS["BLACK"]),
        (SIDE_HEIGHT, img.height - (2 * HEADER_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )
    # (DEPTH)
    add_obj_to_image(
        img,
        create_rectangle(draw, str(camp.height), HEADER_HEIGHT, HEADER_HEIGHT, bg=COLORS["WHITE"], color=COLORS["BLACK"]).rotate(-90, expand=1),
        (SIDE_HEIGHT, img.height - (3 * HEADER_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )

    # RV Circle
    add_obj_to_image(
        img,
        create_circle_with_number(3, CIRCLE_HEIGHT),
        (frontage_in_px - (SIDE_HEIGHT + CIRCLE_HEIGHT), img.height - (HEADER_HEIGHT + CIRCLE_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )

    return img



# with open('img.jpg', 'w') as f:
#     img.save(f)
if __name__ == '__main__':
    camps = read_csv()
    camp = camps[0]
    img = gen_image_for_camp(camp)
    img.show()