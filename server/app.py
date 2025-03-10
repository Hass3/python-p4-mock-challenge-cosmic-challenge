#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
from sqlalchemy.orm import configure_mappers
configure_mappers()
Mission.__mapper__.confirm_deleted_rows = False
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = []
        for scientist in Scientist.query.all():
            scientist_json = {
                "id" : scientist.id,
                "name" : scientist.name,
                "field_of_study" : scientist.field_of_study
            }
            scientists.append(scientist_json)
        return scientists, 200
    
    def post(self):
        
        try:
            new_scientist =  Scientist(name = request.get_json()['name'],field_of_study =  request.get_json()['field_of_study'])
            db.session.add(new_scientist)
            db.session.commit()
            scientist_json = {
                "id" : new_scientist.id,
                "name" : new_scientist.name,
                "field_of_study" : new_scientist.field_of_study,
                "missions" : new_scientist.missions
            }
            return scientist_json, 201
        except:
            return {"errors": ["validation errors"]}, 400
        

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        
        return make_response(scientist.to_dict(), 200)
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        try:
            for attr in request.get_json():
                setattr(scientist, attr, request.get_json()[attr])
            db.session.add(scientist)
            db.session.commit()
            scientist_json = {
                "id" : scientist.id,
                "name" : scientist.name,
                "field_of_study" : scientist.field_of_study,
                "missions" : scientist.missions
            }
            return scientist_json,202
        except:
             return {"errors": ["validation errors"]}, 400
        
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id ==id).first()
        if not scientist:
            return {"error": "Scientist not found"}, 404
        
        db.session.delete(scientist)
        db.session.commit()
     
        return {}, 204
    
class Planets(Resource):
    def get(self):
        planets = [planet.to_dict() for planet in Planet.query.all()]
        return planets, 200
    

class Missions(Resource):
    def post(self):
        try:
            new_mission = Mission(name = request.get_json()["name"], scientist_id = request.get_json()['scientist_id'], planet_id = request.get_json()['planet_id'])
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        except:
            return {"errors": ["validation errors"]}, 400


api.add_resource(Scientists,'/scientists')
api.add_resource(ScientistById, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
