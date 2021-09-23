from flask import request, jsonify
from flask_restx import Resource, Api, Namespace

BroadcastApi = Namespace('BroadcastApi')

@BroadcastApi.route("/IoT")
class IoT(Resource):
    def post(self):
        command = request.get_json()
        recvFile = request.get_file()

@BroadcastApi.route("/direct")
class direct(Resource):
    def post(self):
        request.get_json()

@BroadcastApi.route("/schedule")
class schedule(Resource):
    def post(self):
        request.get_json()

@BroadcastApi.route("/getMacAddress")
class schedule(Resource):
    def post(self):
        request.get_json()
    def delete(self):
        request.get_json()