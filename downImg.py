# -*- coding: UTF-8 -*-

import json
import os
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import urllib.request

cookieFilePath = ''
dirname = '/'


def initial():
    try:
        login()
    except Exception as e:
        print("初始化失败")
        print(e)


def login():
    driver.get(url)
    if get_login_status():
        # 登录过，写Cookie后点击快速进入按钮
        write_cookie_to_driver()

        if platform == 1:
            wait = WebDriverWait(driver, 10)
            sub_btn_ele = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'fm-submit')))
            sub_btn_ele.click()
    else:
        # waiting for login
        print("请进行登录操作...")
        time.sleep(10)
        with open(cookieFilePath, 'w') as cookie_handle:
            cookie_handle.write(json.dumps(driver.get_cookies()))
        write_cookie_to_driver()


# 初始化本次图片保存的地址
def set_dirname():
    global dirname
    if len(driver.title) == 0:
        title = driver.find_element_by_class_name("tb-main-title").get_attribute("data-title")
    else:
        title = driver.title
    dirname = dirname + title + '/'
    if not os.path.exists(dirname):
        os.mkdir(dirname)


def get_login_status():
    global cookieFilePath
    if platform == 1:
        cookieFilePath = 'tb_cookie.json'
    else:
        cookieFilePath = 'tm_cookie.json'

    # 已有cookie文件且未超过一个小时直接使用
    if os.path.exists(cookieFilePath) and os.path.getsize(cookieFilePath) > 0:
        last_modify_time = int(os.stat(cookieFilePath).st_mtime)
        if int(time.time()) - last_modify_time < 3600:
            return True

    return False


def write_cookie_to_driver():
    if not os.path.exists(cookieFilePath):
        print("cookie 文件为空!")
        return False
    with open(cookieFilePath, 'r') as cookie_handle:
        # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
        cookies_list = json.load(cookie_handle)
        for cookie in cookies_list:
            if 'expiry' in cookie:
                del cookie['expiry']
            driver.add_cookie(cookie)
    driver.refresh()


# 获取图片src列表
def get_src_list():
    # 等待滑动获取懒加载 TODO 替换成window.scroll
    print("请滑动加载所有图片")
    time.sleep(5)
    set_dirname()

    result = {
        "detail": [],  # 详情图
        "main": [],  # 主图
        # "sku": [],  # sku图
    }

    if platform == 1:
        # 详情图
        desc = driver.find_element_by_id("J_DivItemDesc")
        if desc:
            img_tags = desc.find_elements_by_tag_name("img")
            if len(img_tags):
                for img in img_tags:
                    src = img.get_attribute('src')
                    if not src:
                        continue
                    result["detail"].append(src)
            else:
                print("没有获取到详情图!")

        # 主图
        main_ul = driver.find_element_by_id("J_UlThumb")
        if main_ul:
            pic_list = main_ul.find_elements_by_class_name("tb-pic")
            if len(pic_list):
                for pic in pic_list:
                    img = pic.find_element_by_tag_name("img")
                    if not img:
                        continue

                    src = img.get_attribute("data-src")
                    if not src:
                        continue

                    src = src.replace("50x50", "400x400")  # 替换尺寸
                    result["main"].append(src)
            else:
                print("没有获取到主图")

    else:
        desc_div_list = driver.find_elements_by_class_name("descV8-singleImage")
        if len(desc_div_list):
            for i in desc_div_list:
                img_tag = i.find_element_by_tag_name("img")
                src = ""
                try:
                    src = img_tag.get_attribute("data-src")
                except Exception:
                    pass
                if not src:
                    src = img_tag.get_attribute("src")

                if src:
                    result["detail"].append(src)
        else:
            print("没有获取到详情图!")

        try:
            video = driver.find_element_by_id("mainPicVideoEl").find_element_by_tag_name("video")
            video_src = video.get_attribute("src")
            result["main"].append(video_src)
        except Exception:
            pass

    return result


# 下载图片
def down(source_list):
    for img_type in source_list:
        for img in source_list[img_type]:
            # 去掉get参数
            img_src = img[:img.rfind("?")] if img.rfind("?") > 0 else img
            # 没有带协议的加协议
            if not img_src.startswith("http:") and not img_src.startswith("https:"):
                head = "https:" if img.startswith("//") else "https://"
                img_src = head + img_src

            suffix = os.path.splitext(img_src)[-1]
            new_file_name = dirname + img_type + "_" + str(source_list[img_type].index(img)) + suffix
            try:
                print("下载图片(" + img_src + "):", end="")
                urllib.request.urlretrieve(img_src, new_file_name)
                print("done!")
            except Exception as e:
                print(e)
                print("下载失败!")


if __name__ == '__main__':
    platform = int(input("请输入平台编号（1 淘宝 2 天猫）："))
    url = input("请输入url:")
    driver = webdriver.Chrome(executable_path='/usr/local/etc/chromedriver')

    try:
        initial()
        src_list = get_src_list()
        down(src_list)
    except Exception as e:
        print(e)

    driver.close()
