# -*- coding: UTF-8 -*-

import json
import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import urllib

cookieFilePath = ''
already_cookie = False
dirname = ''


def initial():
    try:
        init_dir()
        get_login_status()
        write_cookie_to_driver()
    except Exception as e:
        print("初始化失败")
        print(e)


# 初始化本次图片保存的地址
def init_dir():
    global dirname
    dirname = '/Users/yangbaochuan/Desktop/' + driver.title + '_img' + '/'
    if not os.path.exists(dirname):
        os.mkdir(dirname)


def get_login_status():
    global cookieFilePath
    if platform == 1:
        cookieFilePath = 'tb_cookie.json'
    else:
        cookieFilePath = 'tm_cookie.json'

    driver.get(url)
    if os.path.exists(cookieFilePath):
        last_modify_time = int(os.stat(cookieFilePath).st_mtime)
        if int(time.time()) - last_modify_time < 3600:
            global already_cookie
            already_cookie = True
            return driver

    # waiting for login
    time.sleep(10)

    with open(cookieFilePath, 'w') as cookie_handle:
        cookie_handle.write(json.dumps(driver.get_cookies()))


def write_cookie_to_driver():
    if not os.path.exists(cookieFilePath):
        print("cookie 文件为空")
        return False
    with open(cookieFilePath, 'r') as cookie_handle:
        # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
        cookies_list = json.load(cookie_handle)
        for cookie in cookies_list:
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)


# 获取图片src列表
def get_img_list(type):
    global driver
    global already_cookie

    driver.refresh()
    if already_cookie:
        wait = WebDriverWait(driver, 10)
        sub_btn_ele = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'fm-submit')))
        sub_btn_ele.click()

    # 等待滑动获取懒加载
    time.sleep(5)
    result = []

    if type == 1:
        desc = driver.find_element_by_id("J_DivItemDesc")
        img_tags = desc.find_elements_by_tag_name("img")
        if len(img_tags):
            for img in img_tags:
                src = img.get_attribute('src')
                if src:
                    result.append(src)
        else:
            print("没有获取到详情图")
    else:
        desc_div_list = driver.find_elements_by_class_name("descV8-singleImage")
        if len(desc_div_list):
            for i in desc_div_list:
                img_tag = i.find_element_by_tag_name("img")
                src = img_tag.get_attribute("data-src")
                if src:
                    result.append(src)

    return result


# 下载图片
def down_img(imgs):
    for img in imgs:
        suffix = os.path.splitext(img)[-1]
        new_file_name = dirname + str(imgs.index(img)) + suffix
        try:
            print("下载图片(" + img + "):", end="")
            urllib.request.urlretrieve(img, new_file_name)
            print("done")
        except Exception as e:
            print(e)
            print("下载失败")
        print("done")


if __name__ == '__main__':
    platform = input("请输入平台编号（1 淘宝 2 天猫）：")
    url = input("请输入url:")
    driver = webdriver.Chrome(executable_path='/usr/local/etc/chromedriver')

    try:
        initial()
        img_list = get_img_list(platform)
        down_img(img_list)
    except Exception as e:
        print(e)

    driver.close()
