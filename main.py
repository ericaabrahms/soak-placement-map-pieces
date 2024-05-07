from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
from typing import List, Dict
from enum import Enum, auto
import math
from datastore import read_csv, read_art_csv, ArtInfo, CampInfo, Kids, Food, InteractivityTime, CampType, SoundZone, SoundSize, SoundZoneHardPreference, Placeable
import textwrap
import argparse
from timing import timing

DEBUG=True

# CONSTANTS
PIXELS_PER_FOOT = 2.4
SMALL_FONT_SIZE = 6
LARGE_FONT_SIZE = 20

landscape_width_in_px = 3301
landscape_height_in_px = 2551
SIGN_TEXT_HEIGHT = 880
SIGN_TEXT_WIDTH = 1970

DEFAULT_FONT = './RobotoMono-Regular.ttf'
FANCY_FONT = './Eilis-Regular.ttf'
HARLEQUIN_FONT = './HarlequinFLF.ttf'

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
def text_contains(text, names): 
    for name in names: 
        if name in text.lower():
            return True
    return False

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


def get_sign_alias(thing: Placeable):
    # TODO: Delete this. It's moved into placeable.
    return thing.name


def get_camp_sign_font_size(camp): 
    text = get_sign_alias(camp)

    height = SIGN_TEXT_HEIGHT
    width = SIGN_TEXT_WIDTH

    ratio = math.floor(width/len(text))
    size = 450
    wrap = 8

    camp_name_words = text.split(' ')

    if len(camp_name_words) > 3: 
        wrap = 12
        size = 350
        
    for word in camp_name_words: 
        if len(word) >=15: 
            wrap = 15
            size = 280
        elif len(word) >=13:
            wrap = 14
            size = 290
        elif len(word) >= 12: 
            wrap=13
            size= 310
        elif len(word) == 11:
            wrap = 12
            size = 350
        elif len(word) >= 9:
            wrap = 11
            size = 400


    # Handle special camp names that don't behave nicely
    # Mega long names

    if text_contains(text, ['wharf', 'conch', 'bowlovfarts', 'costco', 'sex positivity', 'cbgb']): 
        wrap = 14
        size = 280
    elif text_contains(text, ['observatory']): 
        wrap = 16
        size = 280 
    elif text_contains(text, ['teenie weenie', 'monkey business', 'dtf', 'mbs', 'super happy', 'unlearning', 'snail trail', 'ranger meadow', 'temple', 'second hand booze bar']):  # 3 lines max height
        size = 305
    elif text_contains(text, ['talk with strangers']):
        size = 340            
    elif text_contains(text, ['black hole', 'butt hurt',  'church of cheese', 'cirque de licious', 'dr. bev', 'noods', 'smash that', 'hell bake']): 
        size = 400
        wrap = 11
    elif text_contains(text, ['clusterfuck']): 
        size = 400
    elif text_contains(text, ['hypnodrome']): 
        size = 360

    return {'size': size, 'break': wrap}

def gen_sign_for_camp(camp: CampInfo):
    img = gen_sign_generic(camp, get_camp_sign_font_size)

    icon_y_offset = 525
    icon_x_offset = 525
    icon_dimensions = 350

    icon_top = landscape_height_in_px - icon_y_offset
    # Icons
    if camp.fire or camp.fire_circle: 
        add_obj_to_image(
            img, 
            Image.open('./sign_assets/2-Fire-Icon.png').resize((icon_dimensions, icon_dimensions)),
            (landscape_width_in_px - icon_x_offset, icon_top)
        )
        icon_x_offset += 350

    if camp.xxx: 
        add_obj_to_image(
            img, 
            Image.open('./sign_assets/3-Eighteen-Icon.png').resize((icon_dimensions, icon_dimensions)),
            (landscape_width_in_px - icon_x_offset, icon_top)
        )
        icon_x_offset += 350

    if camp.food != Food.NONE: 
        add_obj_to_image(
            img, 
            Image.open('./sign_assets/4-Food-Icon.png').resize((icon_dimensions, icon_dimensions)),
            (landscape_width_in_px - icon_x_offset, icon_top)
        )
        icon_x_offset += 350

    if camp.bar:
        add_obj_to_image(
            img, 
            Image.open('./sign_assets/6-Drink-Icon.png').resize((icon_dimensions, icon_dimensions)),
            (landscape_width_in_px - icon_x_offset, icon_top)
        )
        icon_x_offset += 350

    if camp.sound_size != SoundSize.NONE:
        add_obj_to_image(
            img, 
            Image.open('./sign_assets/7-Music-Icon.png').resize((icon_dimensions, icon_dimensions)),
            (landscape_width_in_px - icon_x_offset, icon_top)
        )


    return img


def gen_sign_for_art(art: ArtInfo):
    img = gen_sign_generic(art, get_art_sign_font_size)

    if art.number: 
        icon_y_offset = 525
        icon_x_offset = 525
        icon_dimensions = 350
        icon_top = landscape_height_in_px - icon_y_offset
        draw = ImageDraw.Draw(img)

        add_obj_to_image(
            img,
            create_rectangle(draw, art.number, 600, icon_dimensions, bg=black, font=350, color=white, align='right', font_name=HARLEQUIN_FONT),
            (landscape_width_in_px - 750, icon_top),
        )

    
    return img

def get_art_sign_font_size(art): 
    text = art.name

    height = SIGN_TEXT_HEIGHT
    width = SIGN_TEXT_WIDTH

    ratio = math.floor(width/len(text))
    size = 450
    wrap = 8

    camp_name_words = text.split(' ')

    if len(camp_name_words) > 3: 
        wrap = 12
        size = 350
        
    for word in camp_name_words: 
        if len(word) >= 16: 
            print(word)
            wrap = 18
            size = 200
        elif len(word) >=15: 
            wrap = 15
            size = 280
        elif len(word) >=13:
            wrap = 14
            size = 290
        elif len(word) >= 12: 
            wrap=13
            size= 310
        elif len(word) == 11:
            wrap = 12
            size = 350
        elif len(word) >= 9:
            wrap = 11
            size = 400


    # # Handle special camp names that don't behave nicely

    if text_contains(text, ['projection']): 
        wrap = 15
        size = 280
    elif text_contains(text, ['cosmic fire turtle', 'swim the smack']):
        wrap = 16
        size = 280
    elif text_contains(text, ['plankton']): 
        wrap = 16
        size = 305
    elif text_contains(text, ['celestial', 'cosmic portal', 'jellyfish on the bluff', 'love thy beast', 'sad lonely museum', 'bright, bob', 'principles fantastica', 'zen generator', 'wisdom willow']):  # 3 lines max height
        size = 305
    elif text_contains(text, ['talk with strangers', 'school of dreams', 'slow camera']):
        size = 340            
    elif text_contains(text, ['short bus', 'soak sign shop']):  
        size = 400
        wrap = 11
    elif text_contains(text, ['clusterfuck']): 
        size = 400
    elif text_contains(text, ['hypnodrome']): 
        size = 360

    print( {'size': size, 'break': wrap})
    return {'size': size, 'break': wrap}


def gen_sign_generic(thing: Placeable, sizer): 
     # size of camp sign png
    landscape_width_in_px = 3301
    landscape_height_in_px = 2551
    SIGN_TEXT_HEIGHT = 880
    SIGN_TEXT_WIDTH = 1970

    img = Image.new("RGB", (landscape_width_in_px, landscape_height_in_px), white)
    draw = ImageDraw.Draw(img)

        # BG Image
    add_obj_to_image(
        img,
        Image.open('./sign_assets/1-Sign-Blank.png').resize((landscape_width_in_px, landscape_height_in_px)),
        (0, 0) # start at bottom left, offset by how tall the rectangle is.
    )

    

    sw = sizer(thing)
    art_name_size = sw["size"]
    art_name_wrap = sw["break"]
    
    wrapped_name = '\n'.join(textwrap.wrap(thing.get_name(), art_name_wrap))
    add_obj_to_image(
        img,
        create_rectangle(draw, wrapped_name, SIGN_TEXT_WIDTH, SIGN_TEXT_HEIGHT, bg=black, font=art_name_size, color=white, align='center', font_name=HARLEQUIN_FONT),
        (625, 120),
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

def main_art(arts, substring_match):
    for i, art in enumerate(arts):
            if substring_match and substring_match.lower() not in art.name.lower():
                continue
            with timing('gen sign for %s' % art.name, debug=True):
                img = gen_sign_for_art(art)

            with open(art.to_filename('sign_images/art', suffix="_sign"), 'w') as f:
                with timing('saving image', debug=DEBUG):
                    img.save(f, subsampling=0, quality=100)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='soak-placement',
                        description='Generates map pieces and signs for soak')
    subparsers = parser.add_subparsers(help='sub-command help', required=True, dest='subcommand')

    parser_pieces = subparsers.add_parser('pieces', help='pieces help')
    parser_pieces.add_argument('--substring', help='Substring match. Without, it generates everything')


    parser_art = subparsers.add_parser('art', help='art help')
    parser_art.add_argument('--substring', help='Substring match. Without, it generates everything')

    parser_camps = subparsers.add_parser('camps', help='camps help')
    parser_camps.add_argument('--substring', help='Substring match. Without, it generates everything')

    args = parser.parse_args()

    import sys

    if args.subcommand == 'art': 
        print('art')
        with timing("reading csv", debug=DEBUG):
            arts = read_art_csv()
        with timing("doing all images", debug=DEBUG):
            main_art(arts, args.substring)
        sys.exit(0)

    camps = read_csv()
    if args.subcommand == 'pieces':
        for i, camp in enumerate(camps):
            if args.substring and args.substring.lower() not in camp.name.lower():
                continue
            # TODO handle tiny camps
            if camp.is_tiny():
                print(f"Skipping {camp} because their frontage is too small for now.")
                continue

            img = gen_image_for_camp(camp)
            # img.show()
            with open(camp.to_filename('images'), 'w') as f:
                img.save(f, subsampling=0, quality=100)
    else: # camps
        print('camps')
        assert args.subcommand == 'camps'
        for i, camp in enumerate(camps):
            if args.substring and args.substring.lower() not in camp.name.lower():
                continue

            img = gen_sign_for_camp(camp)
            with open(camp.to_filename('sign_images', suffix="_sign"), 'w') as f:
                img.save(f, subsampling=0, quality=100)

