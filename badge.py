import qrcode
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageFilter, ImageOps
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

if not os.path.exists(custom_font) or not os.path.isfile(custom_font):
    print("Error: %s is not a file" % custom_font[-4:])
    sys.exit()


def make_wallpaper(color, img, img1):
    background = Image.new('RGB', (1080, 1920), color=color)

    bg_w, bg_h = background.size
    w, h = img.size
    w1, h1 = img1.size

    offset = ((bg_w-w)//2, 1060)
    offset1 = ((bg_w-w1)//2, 1065)
    mask = img1
    mask = mask.convert("L")
    bar = img1
    bar.putalpha(mask)
    background.paste(img, offset)
    background.paste(mask, offset1, bar)
    background.save('assets/background.png')


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


def makeQR(username, filename, fill_color, back_color):
    qr = qrcode.QRCode(
        version=4,
        box_size=15
    )
    qr.add_data(url)
    qr.make()
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img.save(filename+'.png')


def addQR(qr, bkgrd, final):
    img = Image.open(qr+".png", 'r')
    w, h = img.size
    background = Image.open(bkgrd+".png", 'r')
    bg_w, bg_h = background.size
    offset = ((bg_w-w)//2, 1140)
    background.paste(img, offset)
    background.save(final+".png")
    os.remove("qr.png")


def addText(username, name, final, color):
    msg = name
    msg1 = "@" + username

    img = Image.open(final+".png")
    bg_w, bg_h = img.size

    draw = ImageDraw.Draw(img)
    if custom_font[-4:] == '.ttf':
        font = ImageFont.truetype(str(custom_font), 80)
        font1 = ImageFont.truetype(str(custom_font), 60)
    else:
        print("Font non valido")

    w, h = font.getsize(msg)
    w1, h1 = font1.getsize(msg1)

    draw.text(((bg_w-w)//2, 740), msg, color, font=font)
    draw.text(((bg_w-w1)//2, 860), msg1, color, font=font1)

    img.save(final+".png")


def crop_to_circle_add(color, recolor, final):
    try:
        response = requests.get(profile_pic)
        im = Image.open(BytesIO(response.content))
    except:
        im = Image.open(profile_pic)
    im = im.resize((320, 320), Image.ANTIALIAS)
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    im.putalpha(mask)
    output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    img_w, img_h = im.size
    background = Image.open(final+".png", 'r')
    bg_w, bg_h = background.size
    offset = ((bg_w-img_w)//2, 390)
    background.paste(im, offset, im)

    pixels = background.load()
    for i in range(background.size[0]):
        for j in range(background.size[1]):
            if pixels[i, j] == color:
                pixels[i, j] = recolor

    background.save(final+".png")


if theme == "dark":
    img = round_rectangle(
        (880, 760), 35, (229, 229, 229, 229), (26, 26, 26, 26))
    img1 = round_rectangle((870, 750), 30, (26, 26, 26, 26), (0, 0, 0, 0))
    make_wallpaper((26, 26, 26), img, img1)

    makeQR(username, 'qr', 'white', '#1a1a1a')
    addQR('qr', 'assets/background', result)
    addText(username, name, result, (255, 255, 255))
    crop_to_circle_add((208, 208, 208), (26, 26, 26), result)

else:
    img = round_rectangle(
        (880, 760), 35, (197, 196, 202, 0), (255, 255, 255, 255))
    img1 = round_rectangle((870, 750), 30, (255, 255, 255, 255), (0, 0, 0, 0))
    make_wallpaper((255, 255, 255), img, img1)

    makeQR(username, 'qr', 'black', '#ffffff')
    addQR('qr', 'assets/background', result)
    addText(username, name, result, (0, 0, 0))
    crop_to_circle_add((255, 255, 255), (255, 255, 255, 255), result)
