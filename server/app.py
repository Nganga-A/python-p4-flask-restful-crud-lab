#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first().to_dict()
        return make_response(jsonify(plant), 200)
    
    
    def patch(self,id):
        plant = Plant.query.filter_by(id=id).first()
        if plant:
            for attr in request.form:
                setattr(plant,attr,request.form.get(attr))
            setattr(plant, "is_in_stock", False)
            db.session.add(plant)
            db.session.commit()
            plant_dict = plant.to_dict()
            return make_response(plant_dict, 200)
        else:
            raise NotFound
    

    '''
    def put(self, id):
        plant = Plant.query.get(id)
        if plant:
            plant.is_in_stock = True  # Set in stock to True
            db.session.commit()
            plant_dict = plant.to_dict()
            return make_response(plant_dict, 200)
        else:
            raise NotFound
        
    def patch_price(self, id):
        plant = Plant.query.get(id)
        if plant:
            for attr in request.form:
                setattr(plant, attr, request.form.get(attr))
            db.session.commit()
            plant_dict = plant.to_dict()
            return make_response(plant_dict, 200)
        else:
            raise NotFound
    '''



    def delete(self,id):
        plant = Plant.query.filter_by(id=id).first()
        if plant:
            db.session.delete(plant)
            db.session.commit()
            response_body = {
                "delete_successful":True,
                "message": "Delete Successful!"
            }
            return make_response('', 204)
        else:
            raise NotFound

api.add_resource(PlantByID, '/plants/<int:id>')

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: The requested resource does not exist.",
        404
    )
    return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)
