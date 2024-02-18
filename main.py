from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
import csv
from typing import List
from enum import Enum

# CONSTANTS
PIXELS_PER_FOOT = 2.4
# System dependent. There is a default if we don't specify any font thing.
SMALL_FONT = ImageFont.truetype(font='Roboto-Regular.ttf', size=6)
LARGE_FONT = ImageFont.truetype(font='Roboto-Regular.ttf', size=20)

COLORS = {
    "SZ 1": "#6D9EEB",
    "SZ 2": "#C9DAF8",
    "SZ 3": "#00FFFF",
}


# default vars for sample line
frontage = 60
depth = 120

def get_pixels_from_feet(distance_in_feet):
  return distance_in_feet * PIXELS_PER_FOOT

def create_rectangle(drawer, text, width, height, color="#000000", bg="#FF00FF", gradient=None):
    i = Image.new("RGB", (height, width), bg)
    drawer = ImageDraw.Draw(i)
    # TODO: Font
    drawer.text((5, 5), text)

    return i

def rotate(thing_to_rotate, rotation = 0):
    # expand means "make the image bigger if necessary to accomodate"
    rotated = thing_to_rotate.rotate(rotation, expand=1)
    return rotated

def add_rectangle_to_image(image, rect, top_left):
    image.paste(rect, box=top_left)

def determine_rectangle_placement():
    return (50, 50);

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


def create_horizontal_rectangle(drawer, text, fill, x=0, y=0, width=0, height=0):
    drawer.rectangle((x, y, width, height), outline="#000000", width=1, fill=fill)
    drawer.text((x+5, y+5), text=text, fill="#000000", font=SMALL_FONT)

def create_sz_rectangle(drawer, sz):
    create_horizontal_rectangle(drawer, text=sz, width=100, fill=COLORS[sz], height=30)

def vertical_rectangle(text, width, height, color):
    # width and height are explicitly reversed b/c we're going to rotate the box to be vertical
    i = Image.new("RGB", (height, width), color)
    drawer = ImageDraw.Draw(i)
    # TODO: Font
    drawer.text(text)
    # expand means "make the image bigger if necessary to accomodate"
    rotated = i.rotate(-90, expand=1)

    # You can use img.paste(vertical_rectangle(...)) to put this on the image in the right spot
    return rotated


def gen_image():
    frontage_in_px = round(get_pixels_from_feet(frontage))
    depth_in_px = round(get_pixels_from_feet(depth))

    img = Image.new("RGB", (frontage_in_px, depth_in_px), "#FFFFFF")

    draw = ImageDraw.Draw(img)

    create_sz_rectangle(draw, "SZ 1")

    test_rect = create_rectangle(draw, "TEST", frontage_in_px, 25, gradient='green')
    add_rectangle_to_image(img, test_rect, determine_rectangle_placement())

    return img

# Draw "works!" at 10,10  and fill it with black using our pre-defined font.
# draw.text((10, 10), text="Works!", fill=(0, 0, 0), font=FNT)

# # Draw a 40x40 rectangle starting at 30,20
# draw.rectangle((30, 30, 70, 70), fill="#FF0000")

# # rotated text happens with an in-memory "image" via https://stackoverflow.com/a/245892
# rot = Image.new('L', (50, 50))

# # https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#PIL.ImageDraw.ImageDraw.multiline_text
# d = ImageDraw.Draw(rot)
# d.multiline_text((0,0), "This is the\nrotated\ntext", fill=255)

# # https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.rotate
# w = rot.rotate(-90, expand=1)

# # Paste temporary image "w"'s top-left corner at 120,120.
# img.paste(w, box=(120, 120))
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
                width=row['Frontage'],
                height=row['Depth'],
                name=row[' '],
                camp_type=camp_type, sound_zone=sound_zone, interactivity_time=interactivity_time, sound_size=sound_size,
                neighborhood_preference=row['neighborhood'].split(' '),
                coffee=bool_get('Coffee'),food=bool_get('Food'), fire=bool_get('Fire'), fire_circle=bool_get('Fire Circle'),
                kids=bool_get('Kids'),bar=bool_get('Bar'), ada=bool_get('ADA'), xxx=bool_get('XXX'),
                uneven_ground=bool_get('Uneven Ground Data'), trees=bool_get('Trees'),
                rv_count=rv_count
            ))
    return camps




# with open('img.jpg', 'w') as f:
#     img.save(f)
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'csv':
        camps = read_csv()
        import pdb; pdb.set_trace()
    else:
        img = gen_image()
        img.show()