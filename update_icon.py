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
            l[i] = l[i].replace('\n', '')
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
            print(f'id:{id} not in diff data')
            #アイコンにエラー表示
            continue
        diff = max(0, diff_data[id]['difficulty'])
        if 5000 < diff:
            print(f'unexpected diff on id:{id}')
            continue
        diff_vec[diff // 400] += 1
    return diff_vec

def calc_percent(diff_vec, goal_diff_vec):
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

def is_update(percent):
    file_path = 'last_percent.txt'
    with open(file_path) as f:
        s = f.read()
        if s == str(percent):
            return False
    with open(file_path, mode='w') as f:
        f.write(str(percent))
    return True
#========================update_icon=================


def pie_chart(percent):
    img = Image.open('original_icon.jpg')
    width, height = img.size
    make_circle(width // 2 - 1, height // 2 - 1, 152, 202, 100 / 100, (224 ,224, 222), img)
    print('update icon')
    make_partiall_circle(width // 2 - 1, height // 2 - 1, 152, 202, 0 / 100, percent, (0, 0, 0), img)
    img.save('created_icon.jpg')

#========================make_dm=================
def make_dm(diff_vec, goal_diff_vec, percent):
    color = ['灰', '茶', '緑', '水', '青', '黄', '橙', '赤', '銅', '銀', '金']
    dm = ''
    for i in range(len(diff_vec)):
        dif = diff_vec[i]
        goal = goal_diff_vec[i]
        if goal != 0:
            dm += f'{color[i]} {dif}/{goal}\n'
    dm += f'達成率 {int(percent * 100)}%'
    return dm

def main():
    load_dotenv()

    CK = os.getenv('API_KEY')
    CS = os.getenv('API_KEY_SECRET')
    AT = os.getenv('ACCESS_TOKEN')
    AS = os.getenv('ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    diff_vec = make_diff_vec()
    goal_diff_vec = load_goal()
    percent = calc_percent(diff_vec, goal_diff_vec)
    if not is_update(percent):
        return

    pie_chart(percent)
    api.update_profile_image('created_icon.jpg')
    recipient_id = 1112313327235956738
    api.send_direct_message(recipient_id=recipient_id, text=make_dm(diff_vec, goal_diff_vec, percent))

if __name__ == '__main__':
    main()
