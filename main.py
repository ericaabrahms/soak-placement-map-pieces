from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
from typing import List, Dict
from enum import Enum, auto
import math
from datastore import read_csv, CampInfo, Kids, Food, InteractivityTime, CampType, SoundZone, SoundSize, SoundZoneHardPreference
import textwrap


# CONSTANTS
PIXELS_PER_FOOT = 2.4
SMALL_FONT_SIZE = 6
LARGE_FONT_SIZE = 20

DEFAULT_FONT = './RobotoMono-Regular.ttf'
FANCY_FONT = './Eilis-Regular.ttf'
# System dependent. There is a default if we don't specify any font thing.
def get_font(size=SMALL_FONT_SIZE, font_name=None):
    font=DEFAULT_FONT
    if font_name is not None: 
        font = font_name
    return ImageFont.truetype(font=font, size=size)

BORDER_WIDTH = 2

#  COLOR V
COLORS = {
    "SZ 1": "#6D9EEB",
    "SZ 2": "#C9DAF8",
    "SZ 3": "#00FFFF",
    "#N/A": "#00FF00", # doesn't have a sound zone set (e.g. Unicorn Ranch)
}

white='#FFFFFF'
black='#000000'
pink='#ff00ff'
red = "#FF0000"
grey = '#DDDDDD'
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

interactivity_morning = "#ffff00"
interactivity_afternoon = "#f4cbcc"
interactivity_night = "#a0c4e8"
interactivity_support = "#b6d7a8"

# BASIC HELPERS
def get_pixels_from_feet(distance_in_feet):
  return distance_in_feet * PIXELS_PER_FOOT

def create_rectangle(drawer, text, width, height, color=black, bg=pink, font=12, align='left', font_name=None):
    i = Image.new("RGB", (width, height), bg)
    drawer = ImageDraw.Draw(i)
    drawer.multiline_text((width/2, height/2), text, fill=color, font=get_font(font, font_name), anchor='mm', align=align)

    return i

def add_obj_to_image(image, rect, top_left):
    image.paste(rect, box=top_left)

def create_circle_with_number(number, diam, font=8):
    # TODO FIGURE OUT TRANSPARENT BG
    i = Image.new("RGB", (diam, diam), white)
    drawer = ImageDraw.Draw(i)

    tl = math.floor((diam - font) / 2)
    drawer.arc((0,0, diam, diam), 0, 360, fill=black, width=BORDER_WIDTH)
    drawer.text((tl, tl), str(number), fill=black, font=get_font(font))

    return i

# BORDER BARS
class BorderBarPosition(Enum):
    LEFT = auto()
    RIGHT = auto()
    BOTTOM = auto()
    NONE = auto()
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

# SHENNANIGANS
def get_interactivity_time_color(camp: CampInfo):
    if 'morning' in camp.interactivity_time.lower():
        return interactivity_morning
    if 'afternoon' in camp.interactivity_time.lower():
        return interactivity_afternoon
    if 'night' in camp.interactivity_time.lower():
        return interactivity_night
    if 'support' in camp.interactivity_time.lower():
        return interactivity_support
    return white

def get_font_size_for_area(text: str, width: int, height: int):
    ratio = math.floor(width/len(text))
    size = 10
    wrap = len(text)
    if ratio > 5:
        # print(f'>=5 : {ratio} {text}')

        size = math.floor(ratio * 1.8)
        if size > (math.floor(height / 2)):
            size = math.floor(height / 2)
    elif ratio >= 4:
        size = math.floor(ratio * 3)
        if size > (math.floor(height / 2)):
            size = math.floor(height / 2)
        wrap = math.floor(len(text) * 3 / 5)
    elif ratio >= 3:
        size = math.floor(ratio * 3)
        if size > (math.floor(height / 2)):
            size = math.floor(height / 2)
        wrap = math.floor(len(text) * 2 / 3)
    elif ratio >= 2:
        size = math.floor(ratio * 2)
        if size > (math.floor(height / 2)):
            size = math.floor(height / 2)
        wrap = math.floor(len(text) * 2 / 3)
    else:
        size = math.floor(ratio * 2)
        if size > (math.floor(height / 2)):
            size = math.floor(height / 2)
        wrap = math.floor(len(text) / 2)
    return {'size': size, 'break': wrap}

def get_alias(camp: CampInfo):
    name = camp.name
    lowercase_name = name.lower()
    replacements = {
        'astro shack': 'Astro Shack',
        'bowlovfarts': 'Bowlovfarts',
        'black rock observatory': 'BR Obsv',
        'black rock center for unlearning': 'Center for Unlearning',
        'brother monk': 'Brother Monk\'s',
        'community conch': 'Cmty Conch ASC',
        'clusterfuck': 'Clusterfuck',
        'cbgb': 'CBGB',
        'costco': 'Costco',
        'dogs n recreation': 'Dogs n Rec',
        'super happy invincible titanic': 'SHIT',
        'teenie weenie art tent': 'TWAT',
        'you are here': 'U R Here',
        'cult of the peach': 'Cult of the Peach',
        'absinthe minded': 'Absinthe',
        'camp chai': 'Cp Chai',
        'cracked pot': 'Crkd Pot',
        'divisional spaces': 'Divis. Spaces',
        'elation station': 'Elat\'n Stn.',
        'flower bower': 'Flower Bower  ',
        'hedgehog hegemony': 'HHH',
        'smash that': 'I Smsh Tht',
        'krampus': 'krampus',
        'polyjamorous': 'Polyjamorous',
        'principles fantastica': 'P\'s Fantastica',
        'second rodeo': 'Second Rodeo    ',
        'adventurer\'s respite': 'Adventurer\'s Respite',
        'garden of otherworldly delights': 'Gd Other- worldly Del',
        'secret of mems': 'Secret of Mems',
        'tiny tramp': 'Tiny Tramp Espr',
        'unityhaven': 'Unity Haven   '
    }

    for substr, replacement in replacements.items():
        if substr in lowercase_name:
            return replacement
    return name


def gen_sign_for_camp(camp: CampInfo):

    # size of camp sign png
    landscape_width_in_px = 3301
    landscape_height_in_px = 2551

    img = Image.new("RGB", (landscape_width_in_px, landscape_height_in_px), white)
    draw = ImageDraw.Draw(img)

    HEADER_HEIGHT = 50
    smaller_sixth = 200
    frontage_in_px = 100
    depth_in_px = 100

    # BG Image
    add_obj_to_image(
        img,
        Image.open('./sign_assets/1-Sign-Blank.png').resize((landscape_width_in_px, landscape_height_in_px)),
        (0, 0) # start at bottom left, offset by how tall the rectangle is.
    )

    def get_sign_font_size(camp): 
        return
        # Camp Name
    sw = get_font_size_for_area(camp.name, 1970, 890)
    print(sw)
    camp_name_size = sw["size"]
    camp_name_wrap = sw["break"]

    wrapped_name = '\n'.join(textwrap.wrap(camp.name, camp_name_wrap))
    add_obj_to_image(
        img,
        create_rectangle(draw, wrapped_name, 1970, 890, bg=black, font=camp_name_size, color=white, align='center', font_name=FANCY_FONT),
        (625, 110),
    )

    

    return img

# MAKE THE IMAGE FOR CAMPS
def gen_image_for_camp(camp: CampInfo):

    frontage_in_px = math.floor(get_pixels_from_feet(camp.width))
    depth_in_px = math.floor(get_pixels_from_feet(camp.height))

    img = Image.new("RGB", (frontage_in_px, depth_in_px), white)

    draw = ImageDraw.Draw(img)


    wider = camp.width > camp.height
    smaller_sixth = math.floor(frontage_in_px / 6)
    if wider:
        smaller_sixth = math.floor(depth_in_px / 6)
    HEADER_HEIGHT = math.floor(depth_in_px / 6)

    smaller_sixth_font_size = smaller_sixth - 5

    # Neighborhood Preference
    neighborhood_preference = ''
    for preference in camp.neighborhood_preference:
        neighborhood_preference += f'{preference} '
    header_font_size = get_font_size_for_area(neighborhood_preference, math.floor(frontage_in_px/2), HEADER_HEIGHT)["size"]
    add_obj_to_image(
        img,
        create_rectangle(draw, neighborhood_preference, math.floor(frontage_in_px/2), HEADER_HEIGHT, bg=grey, font=header_font_size, color=black),
        (0,0) # start at top left.
    )

    # SZ Header
    fg = black
    if camp.sound_zone_hard_preference == SoundZoneHardPreference.YES:
        fg = red
    add_obj_to_image(
        img,
        create_rectangle(draw, camp.sound_zone, math.floor(frontage_in_px/2), HEADER_HEIGHT, bg=COLORS[camp.sound_zone], font=header_font_size, color=fg),
        (math.floor(frontage_in_px/2), 0) # start at top center.
    )

    # Camp Name
    camp_name = get_alias(camp)
    sw = get_font_size_for_area(camp_name, math.floor(frontage_in_px * 4 / 6), math.floor(depth_in_px * 4 / 6))
    camp_name_size = sw["size"]
    camp_name_wrap = sw["break"]

    wrapped_name = '\n'.join(textwrap.wrap(camp_name, width=camp_name_wrap))
    add_obj_to_image(
        img,
        create_rectangle(draw, wrapped_name, frontage_in_px - (2 * smaller_sixth), (2 * HEADER_HEIGHT), bg=get_interactivity_time_color(camp), font=camp_name_size),
        (smaller_sixth, HEADER_HEIGHT),
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
            height = smaller_sixth

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
                    x_position = frontage_in_px - smaller_sixth

            bar_font = smaller_sixth_font_size
            if bar_font > 12:
                bar_font = 12

            in_progress = create_rectangle(draw, bar.text, bar_width, height, bg=bar.background_color, color=bar.text_color, font=bar_font)
            add_obj_to_image(
                img,
                in_progress.rotate(rotation, expand=1),
                (x_position, y_pos)
            )
            bar_offset += bar_width

    # DIMS
    # (FRONTAGE)
    dim_font_size = smaller_sixth_font_size
    if camp.width >= 100 or camp.height >= 100:
        dim_font_size=math.floor(.6 * smaller_sixth_font_size)
    add_obj_to_image(
        img,
        create_rectangle(draw, str(camp.width), smaller_sixth, smaller_sixth, bg=white, color=black, font=dim_font_size),
        (smaller_sixth, img.height - (HEADER_HEIGHT + smaller_sixth)) # start at bottom left, offset by how tall the rectangle is.
    )
    # (DEPTH)
    add_obj_to_image(
        img,
        create_rectangle(draw, str(camp.height), smaller_sixth, smaller_sixth, bg=white, color=black, font=dim_font_size ).rotate(-90, expand=1),
        (smaller_sixth, img.height - (2 * smaller_sixth + HEADER_HEIGHT)) # start at bottom left, offset by how tall the rectangle is.
    )

    # COFFEE
    if camp.coffee:
        add_obj_to_image(
            img,
            Image.open('./assets/coffee.png').resize((smaller_sixth, smaller_sixth)),
            (frontage_in_px - (3 * smaller_sixth), depth_in_px - (HEADER_HEIGHT + smaller_sixth)) # start at bottom left, offset by how tall the rectangle is.
        )
    # TEA
    if camp.tea:
        add_obj_to_image(
            img,
            Image.open('./assets/tea.jpg').resize((smaller_sixth, smaller_sixth)),
            (frontage_in_px - (3 * smaller_sixth), depth_in_px - (HEADER_HEIGHT + smaller_sixth)) # start at bottom left, offset by how tall the rectangle is.
        )

    if camp.sound_size != SoundSize.NONE:
        add_obj_to_image(
            img,
            Image.open(f'./assets/sound_{camp.sound_size.value}.jpg').resize((smaller_sixth, smaller_sixth)),
            (frontage_in_px - (3 * smaller_sixth), depth_in_px - (HEADER_HEIGHT + (2 * smaller_sixth))) # start at bottom left, offset by how tall the rectangle is.
        )

    # RV Circle
    if camp.rv_count > 0:
        # RV Circle
        add_obj_to_image(
            img,
            create_circle_with_number(camp.rv_count, smaller_sixth, font=10),
            (frontage_in_px - (2 * smaller_sixth), depth_in_px - (HEADER_HEIGHT + smaller_sixth)) # start at bottom left, offset by how tall the rectangle is.
        )

    # print("Camp: ", camp)

    return img

if __name__ == '__main__':
    import sys
    camps = read_csv()
    seen = []

    for i, camp in enumerate(camps):
        if len(sys.argv) > 1 and sys.argv[1] in 'signs': 

            if len(sys.argv) > 2:
                substring_match = sys.argv[2]
                if substring_match.lower() not in camp.name.lower():
                    continue


            print('making signs')
            img = gen_sign_for_camp(camp)
            with open(f'sign_images/{camp.name.replace(" ", "_").lower()}_sign.jpg', 'w') as f:
                img.save(f, subsampling=0, quality=100)


        else:
            if len(sys.argv) > 1:
                substring_match = sys.argv[1]
                if substring_match.lower() not in camp.name.lower():
                    continue
            # TODO handle tiny camps
            if camp.height < 20 or camp.width < 20:
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