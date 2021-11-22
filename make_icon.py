from PIL import Image
import numpy as np

def calc_deg(x, y):
    vec_a = np.array([0, -1]) - np.array([0, 0])
    vec_b = np.array([x, y]) - np.array([0, 0])
    length_vec_a = np.linalg.norm(vec_a)
    length_vec_b = np.linalg.norm(vec_b)
    inner_product = np.inner(vec_a, vec_b)
    cos = inner_product / (length_vec_a * length_vec_b)
    rad = np.arccos(cos)
    degree = np.rad2deg(rad)
    if x < 0:
        degree = 360 - degree
    return degree

#中心 width // 2 - 1, height // 2 - 1
#中の白 d = 152
#外の黒　d = 202
def make_circle(sx, sy, inner_d, outer_d, percent, color, img):
    width, height = img.size
    for y in range(height):
        for x in range(width):
            if inner_d ** 2 < (x - sx) ** 2 + (y - sy) ** 2 <= outer_d ** 2:
                # temp = int(calc_deg(x - sx, y - sy) / 360 * 250)
                # print(temp)
                # img.putpixel((x, y), (temp, temp, temp))

                if calc_deg(x - sx, y - sy) / 360 <= percent:
                    img.putpixel((x, y), color)

def make_bow(sx, sy, d, percent, color, img):
    width, height = img.size
    H = 2 * d
    for y in range(height):
        h_now = (sy + d) - y
        for x in range(width):
            temp = img.getpixel((x, y))
            if sum(temp) <= 500:
                continue
            if (x - sx) ** 2 + (y - sy) ** 2 <= d ** 2:
                if h_now / H <= percent:
                    img.putpixel((x, y), color)

for i in range(21):
    percent = i * 5
    img = Image.open('original_icon.jpg')
    width, height = img.size
    make_bow(width // 2 - 1, height // 2 - 1, 152, percent / 100, (255, 225, 178), img)
    # img.show()
    s = str(percent)
    while len(s) != 3:
        s = '0' + s
    img.save(f'image/{s}.jpg')

# img = Image.open('original_icon.jpg')
# width, height = img.size
# make_circle(width // 2 - 1, height // 2 - 1, 152, 202, 100 / 100, (0, 0, 0), img)
# make_bow(width // 2 - 1, height // 2 - 1, 152, 100 / 100, (255, 225, 178), img)
# img.show()
# img.save(f'original_icon.jpg')
