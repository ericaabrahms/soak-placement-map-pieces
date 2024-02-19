from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
from typing import List
from enum import Enum, auto
from datastore import read_csv, CampInfo, Kids, Food, InteractivityTime, CampType, SoundZone, SoundSize


# CONSTANTS
PIXELS_PER_FOOT = 2.4
SMALL_FONT_SIZE = 6
LARGE_FONT_SIZE = 20
# System dependent. There is a default if we don't specify any font thing.
SMALL_FONT = ImageFont.truetype(font='./Roboto-Regular.ttf', size=SMALL_FONT_SIZE)
LARGE_FONT = ImageFont.truetype(font='./Roboto-Regular.ttf', size=LARGE_FONT_SIZE)
def get_font(size=SMALL_FONT_SIZE):
    return ImageFont.truetype(font='./Roboto-Regular.ttf', size=size)

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

white='#FFFFFF'
black='#000000'
tree_green = '#38761d'
uneven_ground_brown = '#b45f06'
kids_yellow = '#fff2cc'
kids_plus_yellow = '#ffd966'
ada_blue = '#0000ff'
fire_red = '#ff0000'
fire_circle_red = "#cc0000"
bar = black
food = "#b4a7d6"
food_plus = "#9900ff"
xxx = '#ff00ff'


# # default vars for sample line
# frontage = 60
# depth = 120

class BorderBarPosition(Enum):
    LEFT = auto()
    RIGHT = auto()
    BOTTOM = auto()
    NONE = auto()

def get_pixels_from_feet(distance_in_feet):
  return distance_in_feet * PIXELS_PER_FOOT

def create_rectangle(drawer, text, width, height, color=COLORS["BLACK"], bg=COLORS["PINK"], gradient=None, font=SMALL_FONT):
    i = Image.new("RGB", (width, height), bg)
    drawer = ImageDraw.Draw(i)
    # TODO: Font
    # TODO: add a border
    # TODO: Wrap text
    drawer.text((5, 5), text, fill=color, font=font)

    return i

def rotate(thing_to_rotate, rotation = 0):
    # expand means "make the image bigger if necessary to accomodate"
    return thing_to_rotate.rotate(rotation, expand=1)

def add_obj_to_image(image, rect, top_left):
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


def create_circle_with_number(number, diam):
    # TODO FIGURE OUT TRANSPARENT BG
    i = Image.new("RGB", (diam, diam), COLORS["WHITE"])
    drawer = ImageDraw.Draw(i)

    tl = round((CIRCLE_HEIGHT - SMALL_FONT_SIZE) / 2)
    # TODO: Font
    # TODO: add a border
    # TODO: Wrap text
    drawer.arc((0,0, diam, diam), 0, 360, fill=COLORS["BLACK"], width=BORDER_WIDTH)
    drawer.text((tl, tl), str(number), fill=COLORS["BLACK"], font=get_font(8))

    return i

class BorderBar(object):
    "Text to annotate the attributes of a camp. It decorates the border of the card."

    def __init__(self, text: str, text_color, background_color, preferential_position: BorderBarPosition = BorderBarPosition.NONE):
        self.text = text
        self.text_color = text_color
        self.background_color = background_color
        self.preferential_position = preferential_position

    def __repr__(self):
        return f'<BorderBar {self.text}>'


def generate_border_bars_for_camp(camp: CampInfo) -> List[BorderBar]:
    bars = []
    def add_if_true(condition: bool, txt, bg, fg=white, position=BorderBarPosition.NONE):
        if condition:
            bars.append(BorderBar(txt, fg, bg, position))

    LEFT = BorderBarPosition.LEFT
    BOTTOM = BorderBarPosition.BOTTOM
    RIGHT = BorderBarPosition.RIGHT

    add_if_true(camp.bar, "BAR", black, position=BOTTOM)
    add_if_true(camp.trees, "Trees", tree_green, position=LEFT)
    add_if_true(camp.uneven_ground, "UnEvEn GrOuNd", uneven_ground_brown, position=LEFT)
    add_if_true(camp.ada, "ADA", ada_blue)
    add_if_true(camp.kids == Kids.KIDS, "Kids", fg=black, bg=kids_yellow)
    add_if_true(camp.kids == Kids.KIDS_PLUS, "Kids+", fg=black, bg=kids_plus_yellow)
    add_if_true(camp.food == Food.FOOD, "Food", fg=black, bg=food)
    add_if_true(camp.food == Food.FOOD_PLUS, "Food+", fg=black, bg=food_plus)
    add_if_true(camp.fire, "Fire", fire_red, position=RIGHT)
    add_if_true(camp.fire_circle, "Fire Circle", fire_circle_red, position=RIGHT)
    add_if_true(camp.xxx, "XXX", xxx)
    # Food is wrong.
    # kids is wrong
    return bars


def gen_image_for_camp(camp: CampInfo):
    frontage_in_px = round(get_pixels_from_feet(camp.width))
    depth_in_px = round(get_pixels_from_feet(camp.height))

    img = Image.new("RGB", (frontage_in_px, depth_in_px), COLORS["WHITE"])

    draw = ImageDraw.Draw(img)


    # Header
    add_obj_to_image(
        img,
        create_rectangle(draw, camp.sound_zone, frontage_in_px, HEADER_HEIGHT, bg=COLORS[camp.sound_zone], font=get_font(10)),
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
        create_rectangle(draw, str(camp.width), HEADER_HEIGHT, HEADER_HEIGHT, bg=COLORS["WHITE"], color=COLORS["BLACK"], font=get_font(8)),
        (SIDE_HEIGHT, img.height - (2 * HEADER_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )
    # (DEPTH)
    add_obj_to_image(
        img,
        create_rectangle(draw, str(camp.height), HEADER_HEIGHT, HEADER_HEIGHT, bg=COLORS["WHITE"], color=COLORS["BLACK"], font=get_font(8)).rotate(-90, expand=1),
        (SIDE_HEIGHT, img.height - (3 * HEADER_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )

    if camp.rv_count > 0:
        # RV Circle
        add_obj_to_image(
            img,
            create_circle_with_number(camp.rv_count, CIRCLE_HEIGHT),
            (frontage_in_px - (SIDE_HEIGHT + CIRCLE_HEIGHT), img.height - (HEADER_HEIGHT + CIRCLE_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
        )

    print("Camp: ", camp)
    pprint(generate_border_bars_for_camp(camp=camp))

    return img


# with open('img.jpg', 'w') as f:
#     img.save(f)
if __name__ == '__main__':
    import sys
    camps = read_csv()
    for i, camp in enumerate(camps):
        if i == 3:
            sys.exit()
        img = gen_image_for_camp(camp)
        # img.show()
        print(camp.__dict__)
        print()