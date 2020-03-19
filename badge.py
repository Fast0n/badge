import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import sys
import requests
from io import BytesIO

username = sys.argv[1]
name = sys.argv[2]
profile_pic = sys.argv[3]
url = sys.argv[4]
theme = sys.argv[5]
custom_font = sys.argv[6]
result = 'result'

bg_w, bg_h = (1080, 1920)

if not os.path.exists(custom_font) or not os.path.isfile(custom_font):
    print("Error: %s is not a file" % custom_font[-4:])
    sys.exit()


def make_background(color, img, img1, colorA):
    background = Image.new('RGB', (bg_w, bg_h), color=color)

    w, h = img.size
    w1, h1 = img1.size

    offset = ((bg_w-w)//2, 1060)
    offset1 = ((bg_w-w1)//2, 1065)

    bar = img1
    bar.putalpha(img1.convert("L"))

    background.paste(img, offset)
    background.paste(img1.convert("L"), offset1, bar)

    pixels = background.load()
    for i in range(bg_w):
        for j in range(bg_h):
            if pixels[i, j] == colorA:
                pixels[i, j] = color

    background.save(result+".png")


def round_corner(radius, fill, color):
    corner = Image.new('RGB', (radius, radius), color)
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner


def round_rectangle(size, radius, fill, color):
    width, height = size
    rectangle = Image.new('RGB', size, fill)
    corner = round_corner(radius, fill, color)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius))
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle


def makeQR(fill_color, back_color):
    background = Image.open(result+".png", 'r')
    qr = qrcode.QRCode(
        version=4,
        box_size=15
    )
    qr.add_data(url)
    qr.make()
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    w, h = img.size
    offset = ((bg_w-w)//2, 1140)
    background.paste(img, offset)

    background.save(result+".png")


def addText(color):
    background = Image.open(result+".png", 'r')
    label_name = name
    label_username = "@" + username
    draw = ImageDraw.Draw(background)
    font_name = ImageFont.truetype(str(custom_font), 80)
    font_username = ImageFont.truetype(str(custom_font), 60)

    w, h = font_name.getsize(label_name)
    w1, h1 = font_username.getsize(label_username)

    draw.text(((bg_w-w)//2, 740), label_name, color, font=font_name)
    draw.text(((bg_w-w1)//2, 860), label_username, color, font=font_username)

    background.save(result+".png")


def crop_to_circle_add():
    background = Image.open(result+".png", 'r')
    try:
        response = requests.get(profile_pic)
        img = Image.open(BytesIO(response.content))
    except:
        img = Image.open(profile_pic)

    img = img.resize((320, 320), Image.ANTIALIAS)
    bigsize = (img.size[0] * 3, img.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(img.size, Image.ANTIALIAS)
    img.putalpha(mask)

    offset = ((bg_w-img.size[0])//2, 400)
    background.paste(img, (offset), img)

    background.save(result+".png")


if theme == "dark":
    img = round_rectangle(
        (880, 760), 35, (229, 229, 229), (26, 26, 26))
    img1 = round_rectangle((870, 750), 30, (26, 26, 26), (0, 0, 0))
    make_background((26, 26, 26), img, img1,  (208, 208, 208))
    makeQR('white', '#1a1a1a')
    addText('white')
else:
    img = round_rectangle(
        (880, 760), 35, (197, 196, 202), (255, 255, 255))
    img1 = round_rectangle((870, 750), 30, (255, 255, 255, 255), (0, 0, 0))
    make_background((255, 255, 255), img, img1,  (255, 255, 255))
    makeQR('black', '#ffffff')
    addText('black')

crop_to_circle_add()