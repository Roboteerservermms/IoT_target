from flask import request
from flask_restx import Resource, Api, Namespace, fields

WebApi = Namespace(
    'WebApi',
    description="Web사이트 배포를 위한 API.",
)

@WebApi.route("IoT")
class WebApiIoT(Resource):
    def get(self,data):
        request.get_json()
    def post(self):
        request.get_json()

@WebApi.route("direct")
class WebApiDirect(Resource):
    def post(self):
        request.get_json()

@WebApi.route("schedule")
class WebApiSchedule(Resource):
    def post(self):
        request.get_json()