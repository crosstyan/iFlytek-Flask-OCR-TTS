from application import app
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
import requests
import time
import hashlib
import base64
import json
import websocket
import datetime
import hmac
from urllib.parse import urlencode
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os
from PIL import Image
from flask_bootstrap import Bootstrap


# Config Begin
STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOADED_IMAGE_DEST'] = os.path.join(
    basedir, 'static', app.config['UPLOAD_IMAGE_PATH'])
app.config['UPLOADED_AUDIO_DEST'] = os.path.join(
    basedir, 'static', app.config['UPLOAD_AUDIO_PATH'])
# Config Finished

# Route Begin


@app.route('/')
@app.route('/index')
def index():
    delete_expired(180)
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    uploaded_time = int(time.time())
    if request.method == 'POST':
        uploaded_file = request.files['image']
        if uploaded_file and is_image(uploaded_file):
            convert_image(uploaded_file, uploaded_time)
            return redirect(url_for('view', file_id=uploaded_time))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/view/<file_id>')
def view(file_id):
    os.path.join
    ocr_result = json_parser(upload_ocr(file_id))
    tts(ocr_result, file_id)
    jpeg_standalone_file_name = file_id+".jpg"
    audio_standalone_file_name = file_id+".mp3"
    jpeg_file_url = url_for(
        'static', filename=app.config['UPLOAD_IMAGE_PATH']+"/"+jpeg_standalone_file_name)
    audio_file_url = url_for(
        'static', filename=app.config['UPLOAD_AUDIO_PATH']+"/"+audio_standalone_file_name)
    ocr_result = ocr_result.split('\n')
    return render_template('view.html', text_result=ocr_result, jpeg_file_url=jpeg_file_url, audio_file_url=audio_file_url, file_id=file_id)
# Route finished

# Other functions


def is_image(file):
    ALLOWED_EXT = {'jpg', 'jpeg', 'png'}
    #ALLOWED_MIME_TYPES = {'image/jpeg'}
    if '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
    else:
        return False

    #mime_type = magic.from_buffer(file.stream.read(), mime=True)
    if (ext in ALLOWED_EXT):
        return True
    else:
        return False


def convert_image(file, uploaded_time):
    JPEG_FILE = {'jpg', 'jpeg'}
    #ALLOWED_MIME_TYPES = {'image/jpeg'}
    if '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
    #mime_type = magic.from_buffer(file.stream.read(), mime=True)
    if (ext in JPEG_FILE):
        filename = str(uploaded_time)+".jpg"
        file.save(os.path.join(app.config['UPLOADED_IMAGE_DEST'], filename))
    else:
        im = Image.open(file).convert("RGB")
        filename = str(uploaded_time)+".jpg"
        im.save(os.path.join(
            app.config['UPLOADED_IMAGE_DEST'], filename), "jpeg")


def getHeader():
    curTime = str(int(time.time()))
    param = {"engine_type": "recognize_document"}
    param = json.dumps(param)
    paramBase64 = base64.b64encode(param.encode('utf-8'))
    m2 = hashlib.md5()
    str1 = app.config['OCR_KEY'] + curTime + str(paramBase64, 'utf-8')
    m2.update(str1.encode('utf-8'))
    checkSum = m2.hexdigest()
    # 组装http请求头
    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': app.config['APPID'],
        'X-CheckSum': checkSum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    return header


def upload_ocr(file_id):
    filename = file_id+".jpg"
    with open(os.path.join(app.config['UPLOADED_IMAGE_DEST'], filename), 'rb') as f:
        f1 = f.read()
    f1_base64 = str(base64.b64encode(f1), 'utf-8')
    data = {
        'image': f1_base64
    }
    r = requests.post(app.config['OCR_API'], data=data, headers=getHeader())
    result = str(r.content, 'utf-8')
    return result


def json_parser(json_file):
    data = json.loads(json_file)
    result = ''
    for each in data['data']['document']['blocks']:
        result += (each['lines'][0]['text']+"\n")
    return result



class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {
            "aue": "lame", "auf": "audio/L16;rate=16000", "vcn": "xiaoyan", "tte": "utf8"}
        self.Data = {"status": 2, "text": str(
            base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        # 使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(
            signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(
            authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


def tts(text, file_id):
    global filename
    filename = str(file_id)+".mp3"

    def on_message(ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            # print(message)
            if status == 2:
                #print("ws is closed")
                ws.close()
            if code != 0:
                errMsg = message["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                with open(os.path.join(app.config['UPLOADED_AUDIO_DEST'], filename), 'ab') as f:
                    f.write(audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)
    # 收到websocket错误的处理

    def on_error(ws, error):
        print("### error:", error)

    # 收到websocket关闭的处理

    def on_close(ws):
        print("### closed ###")

    # 收到websocket连接建立的处理

    def on_open(ws):
        def run(*args):
            d = {"common": wsParam.CommonArgs,
                 "business": wsParam.BusinessArgs,
                 "data": wsParam.Data,
                 }
            d = json.dumps(d)
            # print("------>开始发送文本数据")
            ws.send(d)
            if os.path.exists(os.path.join(app.config['UPLOADED_AUDIO_DEST'], filename)):
                os.remove(os.path.join(
                    app.config['UPLOADED_AUDIO_DEST'], filename))

        thread.start_new_thread(run, ())
    wsParam = Ws_Param(APPID=app.config['APPID'], APIKey=app.config['TTS_KEY'],
                       APISecret=app.config['TTS_SECRET'],
                       Text=text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(
        wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def delete_expired(seconds):
    def walk_throgh(rootdir):
        rootdir = str(rootdir)
        # three tuple, make the first whose name is root, the second's name is dirs, and the third is files. (you can name them arbitrary)
        for root, dirs, files in os.walk(rootdir):
            for file_name in files:
                # print(file_name)
                file_time = int(os.path.splitext(file_name)[0])
                now_time = time.time()
                if now_time-file_time > seconds:
                    os.remove(os.path.join(rootdir, file_name))
    walk_throgh(app.config['UPLOADED_IMAGE_DEST'])
    walk_throgh(app.config['UPLOADED_AUDIO_DEST'])
