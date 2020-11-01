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

def get_cookies():
    username = input('Enter you account')
    password = input('Enter you password')

    ChromeOptions = Options()
    ChromeOptions.add_argument('--headless')

    driver = webdriver.Chrome(chrome_options = ChromeOptions)
    time.sleep(3)
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)

    # use xpath (Could be better?)
    driver.find_element_by_name("username").send_keys(username)
    time.sleep(3)
    driver.find_element_by_name("password").send_keys(password)

    # click "Sign in"
    #driver.find_element_by_class_name("Igw0E.IwRSH.eGOV_._4EzTm.bkEs3.CovQj.jKUp7.DhRcB").click()
    driver.find_elements_by_xpath('/html[1]/body[1]/div[1]/section[1]/main[1]/div[1]/article[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[3]/button[1]')[0].click()
    time.sleep(3)

    # click "later"
    #driver.find_element_by_class_name("sqdOP.L3NKy.y3zKF").click()
    driver.find_elements_by_xpath('/html[1]/body[1]/div[1]/section[1]/main[1]/div[1]/div[1]/div[1]/section[1]/div[1]/button[1]')[0].click()
    driver.implicitly_wait(3)

    # click " Not allowed"                                                                                                   
    #driver.find_elements_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]')[0].click()

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
    cookiestr = ";".join(item for item in cookie)
    
    driver.quit()
    return cookiestr

def get_tag(html):

    urls = []
    
    doc = pq(html)
    items = doc('script[type="text/javascript"]').items()
    
    for item in items:
        if item.text().strip().startswith('window._sharedData'):
            js_data = json.loads(item.text()[21:-1], encoding = 'utf-8')
            edges = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["edges"]
            flag = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"]["has_next_page"]
            cursor = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]["edge_hashtag_to_media"]["page_info"]["end_cursor"]
            for edge in edges:
                if edge["node"]["is_video"]:
                    video_url = edge["node"]["video_url"]
                    if video_url:
                            print(video_url + "\n")
                            urls.append(video_url)
                else:
                    if edge["node"]["display_url"]:
                        display_url = edge["node"]["display_url"];
                        print(display_url + "\n")
                        urls.append(display_url)
            print(cursor, flag)
            print("\n")
    while flag:
        url = uri_tag.format(user_id = tag_name, cursor = cursor)
        js_data = get_json(url)
        infos = js_data['data']['hashtag']['edge_hashtag_to_media']['edges']
        cursor = js_data["data"]['hashtag']['edge_hashtag_to_media']["page_info"]["end_cursor"]
        flag = js_data["data"]['hashtag']['edge_hashtag_to_media']["page_info"]["has_next_page"]

        for info in infos:
            if info["node"]["is_video"]:
                video_url = info["node"]["display_url"]
                if video_url:
                    print(video_url + "\n")
                    urls.append(video_url)
            else:
                if info["node"]["display_url"]:
                    display_url = info["node"]["display_url"];
                    print(display_url + "\n")
                    urls.append(display_url)
        print(cursor, flag)
        print("\n")

    return urls

def main(uri_base):

    url = uri_base + tag_name + '/'
    html = get_html(url)
    urls = get_tag(html)

    dirpath = r'.\ig\{0}'.format("tag_name")
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    print('\n total img {0}: '.format(len(urls)))

    for i in range(len(urls)):
        print('\n Downloading img {0}: \n'.format(i + 1) + urls[i], '\n Remaining {0} img'.format(len(urls) - i - 1))
        try:
            content = get_content(urls[i])
            ext = re.findall(".jpg?", urls[i])
            urlext = "jpg" if ext else "mp4"
            file_path = r'.\ig\{0}\{1}.{2}'.format("123", md5(content).hexdigest(), urlext)
            if not os.path.exists(file_path):
                download_obj(content, file_path)
                print('\n Img {0} complete: '.format(i + 1) + urls[i])
            else:
                print('\n Img {0} complete: '.format(i + 1) + urls[i])
        except Exception as e:
            print(e)
            print('Fail!')

uri_base = "https://www.instagram.com/explore/tags/"

uri_tag = "https://www.instagram.com/graphql/query/?query_hash=9b498c08113f1e09617a1703c22b2f32&variables=%7B%22tag_name%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D"

cookie_data = get_cookies()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
    'cookie': cookie_data
}

tag_name = input('Enter IG tag without "#" :');

start = time.time()

main(uri_base)

print(' Success !!!! ╮(╯  _ ╰ )╭')

end = time.time()

total_time = end - start
hour = total_time // 3600
min = (total_time - 3600 * hour) // 60
sec = total_time - 3600 * hour - 60 * min
print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')
