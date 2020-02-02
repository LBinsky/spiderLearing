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
    ��һ�����󣬻�ȡdata_site_key����
    :return: data_site_key����
    '''
    login_url = "https://my.luosimao.com/auth/login"
    resp = requests.get(login_url, headers=headers)
    data_site_key = re.findall(r"data-site-key=\"(.*?)\"", resp.text)[0]
    return data_site_key

data_site_key = firstRequest()

def secondRequest():
    '''
    �ڶ������󣬻�ȡdata_token����
    :return: data_token����
    '''
    captcha_api_url = "https://captcha.luosimao.com/api/widget?k={}&l=zh-cn&s=normal&i=_tu4chs1dd".format(data_site_key)
    resp = requests.get(captcha_api_url, headers=headers)
    data_token = re.findall(r"data-token=\"(.*?)\"", resp.text)[0]
    # data_key = re.findall(r"data-key=\"(.*?)\"", resp.text)[0]
    return data_token

data_token = secondRequest()
# ������������Ҫ����������
raw_bg = UA + "||" + data_token + "||1920:1080||win32||webkit"
raw_b = "64,41:" + str(int(time.time()*1000)) + "||13,22:" + str(int(time.time()*1000) + random.randint(200, 300))

def getEncrypt():
    '''
    �Բ������м���
    :return: ���ܶ���
    '''
    with open("luosimao.js", "r") as f:
        js_code = f.read()
        # print(js_code)
        js_obj = execjs.compile(js_code)
        return js_obj

encrypt = getEncrypt()
def thirdRequest():
    '''
    ���������󣬻�ȡ�����������
    :return: json������
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
# ͼƬ���⣬��Ҫ�ĵ����ͼ��
title = re.sub(r"<i>||</i>","", result["w"])
print(title)
data_h = result["h"]
data_i = result["i"]
data_s = result["s"]

def imageReduction(position):
    '''
    ��ԭʼͼƬ���л�ԭ
    :param position: ��ԭ�����б�
    :return:
    '''
    image = Image.open("luosimao.png") # ԭʼͼƬ
    image_new = Image.new("RGB", [300, 160]) # ��������Ϊ300*160�Ŀհ�ͼƬ
    # �ָ�ͼƬ�Ŀ�ߣ��ָ���СͼƬΪ20*80����
    w_scale = 20
    h_scale = 80
    for index, point in enumerate(position):
        p1 = [int(point[0]), int(point[1])] # ���Ͻ�����
        p2 = [int(point[0]) + w_scale, int(point[1]) + h_scale]
        pic = image.crop(p1 + p2) # ͼƬ�ָ�
        # ��ԭʼͼƬ��Ϊ�����֣������б�ǰ15Ϊ�ϰ벿�֣��б��15λ�°벿��
        if index < 15:
            p1 = (w_scale * index, 0)
            p2 = (w_scale * (index + 1), h_scale)
        else:
            p1 = (w_scale * (index - 15), h_scale)
            p2 = (w_scale * (index - 15 + 1), h_scale * 2)
        image_new.paste(pic, p1 + p2) # ͼƬ��ԭ
    image_new.save("image_new.png") # ���滹ԭ���ͼƬ
    # image_new.show()

def fourthRequest():
    '''
    ���Ĵ����󣬻�ȡԭʼͼƬ�ͻ�ԭ����
    :return:
    '''
    image_url = "https://captcha.luosimao.com/api/frame?s=" + data_s + "&i=_4tp0enoiy&l=zh-cn"
    resp = requests.get(image_url, headers=headers)
    # ��ȡԭʼͼƬ������
    captcha_image_url = re.findall(r"p:\[\'(.*?)\',", resp.text)[0]
    image_resp = requests.get(captcha_image_url, headers=headers)
    image = Image.open(BytesIO(image_resp.content))
    image.save("luosimao.png")
    # ��ȡԭʼ����
    position = re.findall(r"l: (.*)};", resp.text)[0]
    # ��ԭͼƬ
    imageReduction(ast.literal_eval(position))

def fifthRequest():
    '''
    ���һ������������������
    :return:
    '''
    coordinate = input("coordinate:") # ע�⣺����Ϊ����Ϊ(y,x)������(x,y)
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
