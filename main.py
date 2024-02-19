from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
from typing import List, Dict
from enum import Enum, auto
import math
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
    "#N/A": "#00FF00", # doesn't have a sound zone set (e.g. Unicorn Ranch)

    "BLACK": "#000000",
    "WHITE": "#FFFFFF",
    "PINK": "#FF00FF",

}

white='#FFFFFF'
black='#000000'
pink='#ff00ff'
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
xxx = pink


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

def create_rectangle(drawer, text, width, height, color=black, bg=pink, gradient=None, font=SMALL_FONT):
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
    drawer.arc((0,0, diam, diam), 0, 360, fill=black, width=BORDER_WIDTH)
    drawer.text((tl, tl), str(number), fill=black, font=get_font(8))

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

    add_if_true(camp.trees, "Trees", tree_green, position=LEFT)
    add_if_true(camp.uneven_ground, "UnEvEn GrOuNd", uneven_ground_brown, position=LEFT)

    add_if_true(camp.fire, "Fire", fire_red, position=RIGHT)
    add_if_true(camp.fire_circle, "Fire Circle", fire_circle_red, position=RIGHT)

    add_if_true(camp.bar, "BAR", fg=white, bg=black, position=BOTTOM)
    add_if_true(camp.xxx, "XXX", xxx, position=BOTTOM)
    add_if_true(camp.kids == Kids.KIDS, "Kids", fg=black, bg=kids_yellow, position=BOTTOM)
    add_if_true(camp.kids == Kids.KIDS_PLUS, "Kids+", fg=black, bg=kids_plus_yellow, position=BOTTOM)

    add_if_true(camp.ada, "ADA", ada_blue)
    add_if_true(camp.food == Food.FOOD, "Food", fg=black, bg=food)
    add_if_true(camp.food == Food.FOOD_PLUS, "Food+", fg=black, bg=food_plus)

    return bars

def place_bars(bars: List[BorderBar]) -> Dict[BorderBarPosition, List[BorderBar]]:
    """
    Some things have a preference. Honor that preference if we can. For leftovers,
    try to keep it to 2 items per side. If we absolutely must, go to 3 items on the right side.
    """
    output = {
        BorderBarPosition.LEFT: [],
        BorderBarPosition.RIGHT: [],
        BorderBarPosition.BOTTOM: [],
    }

    leftovers = []

    for bar in bars:
        if bar.preferential_position != BorderBarPosition.NONE:
            output[bar.preferential_position].append(bar)
        else:
            leftovers.append(bar)

    if len(leftovers) > 0:
        pass
        sorted_positions = sorted(output, key= lambda k: len(output[k]))

        for position in sorted_positions:
            pass
            if len(output[position]) < 2 and len(leftovers) > 0:
                output[position].append(leftovers.pop())

    for l in leftovers:
        output[BorderBarPosition.RIGHT].append(l)
        # sort the dictionary entries based on the length of their borderboxes.
        # loop over it
        # if the len(values) are < 2, delete them from leftovers and put them in that value.
        # if after that's done, we still have leftovers.. shove it in the right side.
        # if len(output[BorderBarPosition.LEFT]) < 2
    return output


def gen_image_for_camp(camp: CampInfo):
    frontage_in_px = round(get_pixels_from_feet(camp.width))
    depth_in_px = round(get_pixels_from_feet(camp.height))

    img = Image.new("RGB", (frontage_in_px, depth_in_px), COLORS["WHITE"])

    draw = ImageDraw.Draw(img)


    # SZ Header
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

    # Border Bars
    border_bars = place_bars(generate_border_bars_for_camp(camp))
    side_bar_width = depth_in_px - (HEADER_HEIGHT*2)


    for position, bars in border_bars.items():
        if len(bars) == 0:
            continue


        if position == BorderBarPosition.BOTTOM:
            width = frontage_in_px
            height = HEADER_HEIGHT
        else:
            width = depth_in_px - (HEADER_HEIGHT*2)
            height = SIDE_HEIGHT

        bar_sections = len(bars)
        bar_width = math.floor(width/bar_sections)

        rotation = -90
        if position == BorderBarPosition.BOTTOM:
            rotation = 0

        bar_offset = 0 # space occupied by other bar splits.

        for bar in bars:

            if position == BorderBarPosition.BOTTOM:
                y_pos = depth_in_px - HEADER_HEIGHT
                x_position = bar_offset
            else:
                y_pos = HEADER_HEIGHT + bar_offset
                x_position = 0
                if position == BorderBarPosition.RIGHT:
                    x_position = frontage_in_px - SIDE_HEIGHT

            in_progress = create_rectangle(draw, bar.text, bar_width, height, bg=bar.background_color, color=bar.text_color)
            add_obj_to_image(
                img,
                in_progress.rotate(rotation, expand=1),
                (x_position, y_pos)
            )
            bar_offset += bar_width

    # DIMS
    # (FRONTAGE)
    add_obj_to_image(
        img,
        create_rectangle(draw, str(camp.width), HEADER_HEIGHT, HEADER_HEIGHT, bg=COLORS["WHITE"], color=black, font=get_font(8)),
        (SIDE_HEIGHT, img.height - (2 * HEADER_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )
    # (DEPTH)
    add_obj_to_image(
        img,
        create_rectangle(draw, str(camp.height), HEADER_HEIGHT, HEADER_HEIGHT, bg=COLORS["WHITE"], color=black, font=get_font(8)).rotate(-90, expand=1),
        (SIDE_HEIGHT, img.height - (3 * HEADER_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )

    # RV Circle
    if camp.rv_count > 0:
        # RV Circle
        add_obj_to_image(
            img,
            create_circle_with_number(camp.rv_count, CIRCLE_HEIGHT),
            (frontage_in_px - (SIDE_HEIGHT + CIRCLE_HEIGHT), img.height - (HEADER_HEIGHT + CIRCLE_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
        )

    print("Camp: ", camp)

    return img



if __name__ == '__main__':
    import sys
    camps = read_csv()
    seen = []
    for i, camp in enumerate(camps):
        if len(sys.argv) > 0:
            substring_match = sys.argv[1]
            if substring_match.lower() not in camp.name.lower():
                continue
        if camp.height < 30 or camp.width < 30:
            print(f"Skipping {camp} because their frontage is too small for now.")
            continue

        bbar = generate_border_bars_for_camp(camp)
        count = len(bbar)
        seen.append((count, camp, bbar))
        # if i == 3:
        #     sys.exit()
        img = gen_image_for_camp(camp)
        # img.show()
        with open(f'images/{camp.name.replace(" ", "_").lower()}.jpg', 'w') as f:
            img.save(f, subsampling=0, quality=100)


    print([x for x in seen if x[0] >= 6])