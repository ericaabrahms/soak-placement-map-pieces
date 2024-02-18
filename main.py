from PIL import Image, ImageDraw, ImageFont
from pprint import pprint

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

def create_horizontal_rectangle(text, fill, x=0, y=0, width=0, height=0):
    draw.rectangle((x, y, width, height), outline="#000000", width=1, fill=fill)
    draw.text((x+5, y+5), text=text, fill="#000000", font=SMALL_FONT)

def create_vertical_rectangle(text, fill, x=0, y=0, width=0, height=0):
    # See Justin's shenanigan's below
    draw.rectangle((x, y, width, height), outline="#000000", width=1, fill=fill)
    draw.text((x+5, y+5), text=text, fill="#000000", font=SMALL_FONT)

def create_sz_rectangle(sz):
    create_horizontal_rectangle(text=sz, width=frontage_in_px, fill=COLORS[sz], height=30)



frontage_in_px = round(get_pixels_from_feet(frontage))
depth_in_px = round(get_pixels_from_feet(depth))

img = Image.new("RGB", (frontage_in_px, depth_in_px), "#FFFFFF")

draw = ImageDraw.Draw(img)

create_sz_rectangle("SZ 1")

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

img.show()



# with open('img.jpg', 'w') as f:
#     img.save(f)
