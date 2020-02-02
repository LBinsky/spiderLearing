import requests
from PIL import Image
import re
import time
import random
import execjs
from io import BytesIO
import ast


UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
headers = {
    "user-agent": UA
}

def firstRequest():
    '''
    第一次请求，获取data_site_key参数
    :return: data_site_key参数
    '''
    login_url = "https://my.luosimao.com/auth/login"
    resp = requests.get(login_url, headers=headers)
    data_site_key = re.findall(r"data-site-key=\"(.*?)\"", resp.text)[0]
    return data_site_key

data_site_key = firstRequest()

def secondRequest():
    '''
    第二次请求，获取data_token参数
    :return: data_token参数
    '''
    captcha_api_url = "https://captcha.luosimao.com/api/widget?k={}&l=zh-cn&s=normal&i=_tu4chs1dd".format(data_site_key)
    resp = requests.get(captcha_api_url, headers=headers)
    data_token = re.findall(r"data-token=\"(.*?)\"", resp.text)[0]
    # data_key = re.findall(r"data-key=\"(.*?)\"", resp.text)[0]
    return data_token

data_token = secondRequest()
# 第三次请求需要的两个参数
raw_bg = UA + "||" + data_token + "||1920:1080||win32||webkit"
raw_b = "64,41:" + str(int(time.time()*1000)) + "||13,22:" + str(int(time.time()*1000) + random.randint(200, 300))

def getEncrypt():
    '''
    对参数进行加密
    :return: 加密对象
    '''
    with open("luosimao.js", "r") as f:
        js_code = f.read()
        # print(js_code)
        js_obj = execjs.compile(js_code)
        return js_obj

encrypt = getEncrypt()
def thirdRequest():
    '''
    第三次请求，获取后续请求参数
    :return: json对象结果
    '''
    encrypt_key = "c28725d494c78ad782a6199c341630ee"
    captcha_url = "https://captcha.luosimao.com/api/request?k={}&l=zh-cn".format(data_site_key)
    parame = {
        "bg": encrypt.call("AES", raw_bg, encrypt_key),
        "b": encrypt.call("AES", raw_b, encrypt_key)
    }
    resp = requests.post(captcha_url, headers=headers, data=parame)
    return resp.json()
result = thirdRequest()
# 图片标题，需要的点击的图形
title = re.sub(r"<i>||</i>","", result["w"])
print(title)
data_h = result["h"]
data_i = result["i"]
data_s = result["s"]

def imageReduction(position):
    '''
    对原始图片进行还原
    :param position: 还原坐标列表
    :return:
    '''
    image = Image.open("luosimao.png") # 原始图片
    image_new = Image.new("RGB", [300, 160]) # 创建像素为300*160的空白图片
    # 分割图片的宽高，分割后的小图片为20*80像素
    w_scale = 20
    h_scale = 80
    for index, point in enumerate(position):
        p1 = [int(point[0]), int(point[1])] # 左上角坐标
        p2 = [int(point[0]) + w_scale, int(point[1]) + h_scale]
        pic = image.crop(p1 + p2) # 图片分割
        # 将原始图片分为两部分，坐标列表前15为上半部分，列表后15位下半部分
        if index < 15:
            p1 = (w_scale * index, 0)
            p2 = (w_scale * (index + 1), h_scale)
        else:
            p1 = (w_scale * (index - 15), h_scale)
            p2 = (w_scale * (index - 15 + 1), h_scale * 2)
        image_new.paste(pic, p1 + p2) # 图片还原
    image_new.save("image_new.png") # 保存还原后的图片
    # image_new.show()

def fourthRequest():
    '''
    第四次请求，获取原始图片和还原坐标
    :return:
    '''
    image_url = "https://captcha.luosimao.com/api/frame?s=" + data_s + "&i=_4tp0enoiy&l=zh-cn"
    resp = requests.get(image_url, headers=headers)
    # 获取原始图片并保存
    captcha_image_url = re.findall(r"p:\[\'(.*?)\',", resp.text)[0]
    image_resp = requests.get(captcha_image_url, headers=headers)
    image = Image.open(BytesIO(image_resp.content))
    image.save("luosimao.png")
    # 获取原始坐标
    position = re.findall(r"l: (.*)};", resp.text)[0]
    # 还原图片
    imageReduction(ast.literal_eval(position))

def fifthRequest():
    '''
    最后一次请求，需输入点击坐标
    :return:
    '''
    coordinate = input("coordinate:") # 注意：坐标为输入为(y,x)，不是(x,y)
    captcha_verify_url = "https://captcha.luosimao.com/api/user_verify"
    parma = {
        "h": data_h,
        "v": encrypt.call("AES", coordinate, data_i).replace("+", "-").replace("/", "_").replace("/=+/", ""),
        "s": encrypt.call("MD5", coordinate)
    }
    resp = requests.post(captcha_verify_url, headers=headers, data=parma)
    print(resp.text)

def main():
    fourthRequest()
    fifthRequest()

if __name__ == '__main__':
    main()
