let CryptoJS = require("crypto-js");

// AES加密
function AES(data, encrypt_key) {
    const iv = "2801003954373300";
    let key = CryptoJS.enc.Utf8.parse(encrypt_key);
    let iv_parse = CryptoJS.enc.Utf8.parse(iv);
    return CryptoJS.AES.encrypt(data, key, {
        iv: iv_parse,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.ZeroPadding
    }).toString()
}
// MD5加密，最后的s参数需要
function MD5(data) {
    return CryptoJS.MD5(data).toString()
}

