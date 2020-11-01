import requests
import urllib.request
import os
import time
import json
import random
import re
from hashlib import md5
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def download_obj(data, path):
    with open(path, "wb") as file:
        file.write(data)
        file.close()

def get_json(url):
    try:
        response = requests.get(url, headers = headers, timeout = 10)
        return response.json()
    except Exception as e:
        print(e)
        time.sleep(60 + float(random.randint(1,1000)) / 100)
        return get_json(url)

def get_html(url):
    response = requests.get(url, headers = headers)
    return response.text # text return Unicode data -> get text

def get_content(url):
    response = requests.get(url, headers = headers, timeout = 10)
    return response.content # content return bytes(binary) data -> get image, video, file and etc

def get_cookie(IG_name_url):
    username = "jerry840622@gmail.com"
    password = "lovechorong0622"

    ChromeOptions = Options()
    #ChromeOptions.add_argument('--headless')
    # Can not use '--headless'

    driver = webdriver.Chrome(chrome_options = ChromeOptions)
    time.sleep(3)
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)

    driver.find_element_by_name("username").send_keys(username)
    time.sleep(3)
    driver.find_element_by_name("password").send_keys(password)

    # Click "Sign in"
    #driver.find_element_by_class_name("Igw0E.IwRSH.eGOV_._4EzTm.bkEs3.CovQj.jKUp7.DhRcB").click()
    driver.find_elements_by_xpath('/html[1]/body[1]/div[1]/section[1]/main[1]/div[1]/article[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[3]/button[1]')[0].click()
    time.sleep(3)

    # Click "later"
    #driver.find_element_by_class_name("sqdOP.L3NKy.y3zKF").click()
    driver.find_elements_by_xpath('/html[1]/body[1]/div[1]/section[1]/main[1]/div[1]/div[1]/div[1]/section[1]/div[1]/button[1]')[0].click()
    driver.implicitly_wait(3)

    # Click " Not allowed"                                                                                                   
    driver.find_elements_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]')[0].click()

    driver.get(IG_name_url)
    time.sleep(3)

    # Lazy to add Xpath, sorry
    driver.find_element_by_class_name("XjzKX").click()
    time.sleep(1)

    current_url = driver.current_url

    # get_cookies() is python func
    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
    cookiestr = ";".join(item for item in cookie)
    
    driver.quit()
    return cookiestr, current_url

def get_id(html):

    user_id = ""
    
    doc = pq(html)
    items = doc('script[type="text/javascript"]').items()
    
    for item in items:
        if item.text().strip().startswith('window._sharedData'):
            js_data = json.loads(item.text()[21:-1], encoding = 'utf-8')
            user_id = js_data["entry_data"]["StoriesPage"][0]["user"]["id"]
            break

    return user_id

def get_story(story_url, user_id):

    urls = []

    url = story_url.format(user_id = user_id)

    js_data = get_json(url)

    items = js_data["data"]["reels_media"]
    for item in items:
        infos = item["items"]
        for info in infos:
            display_url = info["display_url"]
            urls.append(display_url)
    return urls

def main(user_id, IG_name):

    story_url_base = "https://www.instagram.com/graphql/query/?query_hash=c9c56db64beb4c9dea2d17740d0259d9&variables=%7B%22reel_ids%22%3A%5B%22{user_id}%22%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%5D%2C%22precomposed_overlay%22%3Afalse%2C%22show_story_viewer_list%22%3Atrue%2C%22story_viewer_fetch_count%22%3A50%2C%22story_viewer_cursor%22%3A%22%22%2C%22stories_video_dash_manifest%22%3Afalse%7D"

    urls = get_story(story_url = story_url_base, user_id = user_id)

    dirpath = r'.\ig\{0}'.format(IG_name)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    print('\n total img {0}: '.format(len(urls)))

    for i in range(len(urls)):
        print('\n Downloading img {0}: \n'.format(i + 1) + urls[i], '\n Remaining {0} img'.format(len(urls) - i - 1))
        try:
            content = get_content(urls[i])
            ext = re.findall(".jpg?", urls[i])
            urlext = "jpg" if ext else "mp4"
            file_path = r'.\ig\{0}\{1}.{2}'.format(IG_name, md5(content).hexdigest(), urlext)

            if not os.path.exists(file_path):
                download_obj(content, file_path)
                print('\n Img {0} complete: '.format(i + 1) + urls[i])
            else:
                print('\n Img {0} complete: '.format(i + 1) + urls[i])
        except Exception as e:
            print(e)
            print('Fail')

IG_name = input('Enter IG account:')

IG_name_url = "https://www.instagram.com/{0}/".format(IG_name)

cookie_data, current_url = get_cookie(IG_name_url)

# How many content should headers need?
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    'cookie': cookie_data
}

user_id = get_id(current_url)

start = time.time()

main(user_id = user_id, IG_name = IG_name)

print(' Success !!!! ╮(╯  _  ╰ )╭')

end = time.time()

total_time = end - start
hour = total_time // 3600
min = (total_time - 3600 * hour) // 60
sec = total_time - 3600 * hour - 60 * min
print(f'一共花費了{int(hour)}h {int(min)}m {int(sec)}s')
