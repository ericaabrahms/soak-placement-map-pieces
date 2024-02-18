from PIL import Image, ImageDraw, ImageFont
from pprint import pprint

# CONSTANTS
PIXELS_PER_FOOT = 2.4

# default vars for sample line
frontage = 60
depth = 120




def get_pixels_from_feet(distance_in_feet):
  return distance_in_feet * PIXELS_PER_FOOT

frontage_in_px = round(get_pixels_from_feet(frontage))
depth_in_px = round(get_pixels_from_feet(depth))

img = Image.new("RGB", (frontage_in_px, depth_in_px), "#FFFFFF")


# System dependent. There is a default if we don't specify any font thing.
fnt = ImageFont.truetype(font='Roboto-Regular.ttf', size=20)

# draw = ImageDraw.Draw(img)
# # Draw "works!" at 10,10  and fill it with black using our pre-defined font.
# draw.text((10, 10), text="Works!", fill=(0, 0, 0), font=fnt)

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
