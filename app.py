from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os, subprocess, json, requests
from flask_restx import Resource, Api
from API.Broadcast import BroadcastApi
app = Flask(__name__)
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #파일 업로드 용량 제한 단위:바이트
#HTML 렌더링
api = Api(
    app,
    version='0.1',
    title="RoboTeer's API Server",
    description="RoboTeer's Broadcast API Server!",
    terms_url="/",
    contact="ing03201@gmail.com",
    license="MIT"
)
jsonPath = "./json/"

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/<ip>')
def device_page(ip):

    res = requests.post(f"http://{ip}/getMacAddress")
    with open(f"{jsonPath}{ip}.json") as f:
        jsonData = json.load(f)
    try :
        res.raise_for_status()
    except:
        return None

    return 


#서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug = True)