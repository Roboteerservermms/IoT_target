 
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os, subprocess, json
from flask_restx import Resource, Api
from API.Web import WebApi
from API.Broadcast import BroadcastApi
app = Flask(__name__, static_url_path='', static_folder='frontend/build')
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

api.add_namespace(WebApi, '/Web')
api.add_namespace(BroadcastApi, '/Broadcast')

@app.route("/", defaults={'path':''})
def serve(path):
    return send_from_directory(app.static_folder,'index.html')

#서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug = True)