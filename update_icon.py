import datetime
import requests
import json
from dotenv import load_dotenv
import os
import tweepy

#========================calc_percent=================
def get_submission():
    dt_now = datetime.datetime.now()
    dt_month = datetime.datetime(dt_now.year, dt_now.month, 1)
    unix_second = int(dt_month.timestamp())
    response = requests.get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user=kumakumaaaaa&from_second={unix_second}').json()
    return response

def get_new_diff():
    print('getting new diff')
    response = requests.get('https://kenkoooo.com/atcoder/resources/problem-models.json')
    data_file = open('diff_data.json', 'w')
    json.dump(response.json(), data_file)

def load_diff():
    get_new_diff()
    data_file = open('diff_data.json', 'r')
    data = json.load(data_file)
    # print(data['arc129_f']['difficulty'])
    return data

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
    diff_data = load_diff()
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

#========================update_icon=================

load_dotenv()

CK = os.getenv('API_KEY')
CS = os.getenv('API_KEY_SECRET')
AT = os.getenv('ACCESS_TOKEN')
AS = os.getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(CK, CS)
auth.set_access_token(AT, AS)
api = tweepy.API(auth)

percent = int(((calc_percent() * 100) // 5) * 5)
print(percent)
s = str(percent)
while len(s) != 3:
    s = '0' + s
filename = f"pie_chart_image/{s}.jpg"
api.update_profile_image(filename)
