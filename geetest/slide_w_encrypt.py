import rsa
import json
import os
import binascii
import random
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad



sec_key = binascii.hexlify(os.urandom(8))

def encrypted_request(initData, userresponse, passtime, aa):
    '''
    加密参数
    :param initData: 请求含背景图片的响应值
    :param userresponse: userresponse参数, 由滑动轨迹轨迹生成
    :param passtime: passtime参数，滑动数组的最后提个滑动时间
    :param aa: 滑动轨迹数组加密后的参数
    :return: 最后一次请求需要的参数
    '''
    # md5 加密
    hash = hashlib.md5()
    hash.update(bytes(initData['gt'], encoding='utf-8'))
    hash.update(bytes(initData['challenge'][0:32], encoding='utf-8'))
    hash.update(bytes(str(passtime), encoding='utf-8'))
    text = {
        "userresponse": userresponse,
        "passtime": passtime,
        "imgload": random.randint(100, 800),
        "aa": aa,
        "ep": {"v": "6.0.9"},
        'rp': hash.hexdigest()
    }
    text = json.dumps(text, separators=(',', ':'))

    # rsa 不对称性对 aes的密钥进行加密
    enc_sec_key = rsa_encrpt()

    # aes 对称加密  进行轨迹加密
    enc_text = aes_encrypt(text)

    # base64 编码
    enc_text = b64encode(enc_text)

    data = {
        'gt': initData['gt'],
        'challenge': initData['challenge'],
        'w': enc_text + enc_sec_key,
        # 'callback': 'geetest_' + str(int(time.time() * 1000)),
    }
    return data




def rsa_encrpt():
    '''
    RSA加密，JS中的s
    :return: 加密后结果
    '''
    n = "00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D945" \
        "1F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D68" \
        "6D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81"
    e = "10001"
    PublicKey = rsa.PublicKey(int(n, 16), int(e, 16))
    rs = rsa.encrypt(sec_key, PublicKey)
    # print(rs.hex())
    return rs.hex()

# s = rsa_encrpt()


def aes_encrypt(text):
    """
    AES加密，JS中的a
    :param text: 文本
    :return: 加密后结果
    """
    iv = b"0000000000000000"
    encryptor = AES.new(sec_key, AES.MODE_CBC, iv)
    pad_pkcs7 = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
    ciphertext = encryptor.encrypt(pad_pkcs7)
    print(ciphertext)
    return ciphertext

def b64encode(s):
    '''
    base加密，JS中的_
    :param s: 加密参数
    :return: 加密后结果
    '''
    def separate_24_to_6(n, base):
        res = 0
        for i in range(24, -1, -1):
            if base >> i & 1 == 1:
                res = (res << 1) + (n >> i & 1)
        return res

    base64chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789()"
    r = ""
    p = ""
    c = len(s) % 3
    if c > 0:
        for _ in range(c, 3):
            p += '.'
            s += b'\0'

    for c in range(0, len(s), 3):
        # we add newlines after every 76 output characters, according to the MIME specs
        # if c > 0 and (c / 3 * 4) % 76 == 0:
        #     r += "\r\n"

        # these three 8-bit (ASCII) characters become one 24-bit number
        n = (s[c] << 16) + (s[c + 1] << 8) + (s[c + 2])

        # this 24-bit number gets separated into four 6-bit numbers
        # n = [n >> 18 & 63, n >> 12 & 63, n >> 6 & 63, n & 63]

        n = [separate_24_to_6(n, base) for base in [7274496, 9483264, 19220, 235]]

        r += base64chars[n[0]] + base64chars[n[1]] + base64chars[n[2]] + base64chars[n[3]]

    # add the actual padding string, after removing the zero pad
    return r[0: len(r) - len(p)] + p

def cal_userresponse(a, b):
    d = []
    c = b[32:]
    for e in range(len(c)):
        f = ord(str(c[e]))
        tmp = f - 87 if f > 57 else f - 48
        d.append(tmp)

    c = 36 * d[0] + d[1]
    g = int(round(a)) + c
    b = b[:32]

    i = [[], [], [], [], []]
    j = {}
    k = 0
    e = 0
    for e in range(len(b)):
        h = b[e]
        if h in j:
            pass
        else:
            j[h] = 1
            i[k].append(h)
            k += 1
            k = 0 if (k == 5) else k

    n = g
    o = 4
    p = ""
    q = [1, 2, 5, 10, 50]
    while n > 0:
        if n - q[o] >= 0:
            m = int(random.random() * len(i[o]))
            p += str(i[o][m])
            n -= q[o]
        else:
            del (i[o])
            del (q[o])
            o -= 1
    return p

def fun_u(a, v1z, T1z):
    while not v1z or not T1z:
        pass
    else:
        x1z = 0
        c1z = a
        y1z = v1z[0]
        k1z = v1z[2]
        L1z = v1z[4]

        i1z = T1z[x1z:x1z + 2]
        while i1z:
            x1z += 2
            n1z = int(i1z, 16)
            M1z = chr(n1z)
            I1z = (y1z * n1z * n1z + k1z * n1z + L1z) % len(a)
            c1z = c1z[0:I1z] + M1z + c1z[I1z:]  # 插入一个值
            i1z = T1z[x1z:x1z + 2]
        return c1z


# 计算每次间隔  相当于c函数
def fun_c(a):
    g = []
    e = []
    f = 0
    for h in range(len(a) - 1):
        b = int(round(a[h + 1][0] - a[h][0]))
        c = int(round(a[h + 1][1] - a[h][1]))
        d = int(round(a[h + 1][2] - a[h][2]))
        g.append([b, c, d])

        if b == c == d == 0:
            pass
        else:
            if b == c == 0:
                f += d
            else:
                e.append([b, c, d + f])
                f = 0
    if f != 0:
        e.append([b, c, f])
    return e


def fun_e(item):  # 相当于e函数
    b = [[1, 0], [2, 0], [1, -1], [1, 1], [0, 1], [0, -1], [3, 0], [2, -1], [2, 1]]
    c = 'stuvwxyz~'
    for i, t in enumerate(b):
        if t == item[:2]:
            return c[i]
    return 0


def fun_d(a):
    b = '()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr'
    c = len(b)
    d = ''
    e = abs(a)
    f = int(e / c)
    if f >= c:
        f = c - 1
    if f > 0:
        d = b[f]
    e %= c
    g = ''
    if a < 0:
        g += '!'
    if d:
        g += '$'
    return g + d + b[e]

def fun_f(track_list):
    skip_list = fun_c(track_list)
    g, h, i = [], [], []
    for j in range(len(skip_list)):
        b = fun_e(skip_list[j])
        if b:
            h.append(b)
        else:
            g.append(fun_d(skip_list[j][0]))
            h.append(fun_d(skip_list[j][1]))
        i.append(fun_d(skip_list[j][2]))
    return ''.join(g) + '!!' + ''.join(h) + '!!' + ''.join(i)

def get_userresponse_a(initData, track_list):
    '''
    生成加密后userresponse和aa参数
    :param initData: 带图片地址的响应
    :param track_list: 滑动数组
    :return:
    '''
    challenge = initData['challenge']
    l = track_list[-1][0]

    a = fun_f(track_list)
    arr = [12, 58, 98, 36, 43, 95, 62, 15, 12]
    s = initData['s']
    a = fun_u(a, arr, s)
    userresponse = cal_userresponse(l, challenge)
    return userresponse, a

