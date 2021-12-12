import datetime
import requests
import json
from dotenv import load_dotenv
import os
import tweepy
from PIL import Image
import numpy as np

#========================calc_percent=================
def get_submission():
    dt_now = datetime.datetime.now()
    dt_month = datetime.datetime(dt_now.year, dt_now.month, 1)
    unix_second = int(dt_month.timestamp())
    response = requests.get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user=kumakumaaaaa&from_second={unix_second}').json()
    return response

def get_diff():
    print('getting new diff')
    response = requests.get('https://kenkoooo.com/atcoder/resources/problem-models.json').json()
    return response

def load_goal():
    color = ['灰', '茶', '緑', '水', '青', '黄', '橙', '赤', '銅', '銀', '金']
    goal_diff_vec = [0 for _ in range(len(color))]
    with open('goal.txt') as f:
        l = f.readlines()
        for i in range(len(l)):
            l[i] = l[i].replace("\n", "")
            for j in range(len(color)):
                if color[j] in l[i]:
                    goal_diff_vec[j] = int(l[i][1:])
    return goal_diff_vec

def make_diff_vec():
    diff_data = get_diff()
    diff_num = 11
    diff_vec = [0 for _ in range(diff_num)]
    submission = get_submission()
    s = set()
    for sub in submission:
        if sub['result'] == 'AC':
            s.add(sub['problem_id'])
    for id in s:
        if id not in diff_data:
            print(f"id:{id} not in diff data")
            #アイコンにエラー表示
            continue
        diff = max(0, diff_data[id]['difficulty'])
        if 5000 < diff:
            print(f"unexpected diff on id:{id}")
            continue;
        diff_vec[diff // 400] += 1
    return diff_vec

def calc_percent():
    diff_vec = make_diff_vec()
    goal_diff_vec = load_goal()
    for i in range(len(diff_vec)):
        diff_vec[i] = min(diff_vec[i], goal_diff_vec[i])
    percent = sum(diff_vec) / sum(goal_diff_vec)
    return percent

#========================make_icon=================

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

def make_partiall_circle(sx, sy, inner_d, outer_d, min_percent, max_percent, color, img):
    width, height = img.size
    for y in range(height):
        for x in range(width):
            if inner_d ** 2 < (x - sx) ** 2 + (y - sy) ** 2 <= outer_d ** 2:
                if min_percent <= calc_deg(x - sx, y - sy) / 360 <= max_percent:
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

#========================update_icon=================

load_dotenv()

CK = os.getenv('API_KEY')
CS = os.getenv('API_KEY_SECRET')
AT = os.getenv('ACCESS_TOKEN')
AS = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)

def pie_chart_colorful():
    img = Image.open('original_icon.jpg')
    width, height = img.size
    diff_vec = make_diff_vec()
    goal_diff_vec = load_goal()
    all = 0
    for i in range(len(goal_diff_vec)):
        all += goal_diff_vec[i]
    rgb = [(129, 129, 129), (129, 63, 0), (0, 129, 0), (0, 192, 192), (0, 0, 255), (192, 192, 0), (255, 129, 0), (255, 0, 0), (225, 82, 15), (192, 192, 192), (255, 195, 10)]
    # for i in range(len(rgb)):
    #     t = list(rgb[i])
    #     for j in range(3):
    #         t[j] = t[j]
    #     rgb[i] = tuple(t)
    #gray
    make_partiall_circle(width // 2 - 1, height // 2 - 1, 152, 202, 0 / 100, 0 / 100, (224, 224, 222), img)
    for i in range(len(diff_vec)):
        diff_vec[i] = min(diff_vec[i], goal_diff_vec[i])
    #black
    make_partiall_circle(width // 2 - 1, height // 2 - 1, 152, 202, 0 / 100, sum(diff_vec) / sum(goal_diff_vec), (0, 0, 0), img)
    now = sum(diff_vec)
    for i in range(len(diff_vec)):
        now_end = now + (goal_diff_vec[i] - diff_vec[i])
        make_partiall_circle(width // 2 - 1, height // 2 - 1, 152, 202, now / sum(goal_diff_vec), now_end / sum(goal_diff_vec), rgb[i], img)
        now = now_end
    filename = "created_icon.jpg"
    img.save(filename)
    img.show()

def pie_chart_partiall_colorful():
    img = Image.open('original_icon.jpg')
    width, height = img.size
    diff_vec = make_diff_vec()
    goal_diff_vec = load_goal()
    all = 0
    for i in range(len(goal_diff_vec)):
        all += goal_diff_vec[i]
    rgb = [(129, 129, 129), (129, 63, 0), (0, 129, 0), (0, 192, 192), (0, 0, 255), (192, 192, 0), (255, 129, 0), (255, 0, 0), (225, 82, 15), (192, 192, 192), (255, 195, 10)]
    make_partiall_circle(width // 2 - 1, height // 2 - 1, 152, 202, 0 / 100, 100 / 100, (224, 224, 222), img)
    for i in range(len(diff_vec)):
        diff_vec[i] = min(diff_vec[i], goal_diff_vec[i])
    now = 0
    for i in range(len(diff_vec)):
        now_end = now + diff_vec[i] + 0.1
        make_partiall_circle(width // 2 - 1, height // 2 - 1, 152, 202, now / sum(goal_diff_vec), now_end / sum(goal_diff_vec), rgb[i], img)
        now += goal_diff_vec[i]
    filename = "created_icon.jpg"
    img.save(filename)
    img.show()

pie_chart_partiall_colorful()
