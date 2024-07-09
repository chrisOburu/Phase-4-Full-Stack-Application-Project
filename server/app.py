#!/usr/bin/env python3
from models import db, Freelancer, Project, Client
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Freelancing Project Management</h1>"


class Freelancers(Resource):
    def get(self):
        response_dict_list = [n.to_dict() for n in Freelancer.query.all()]
        response = make_response(
            jsonify(response_dict_list),
            200,
        )
        return response


class FreelancerByID(Resource):
    def get(self, id):
        response_dict = Freelancer.query.filter_by(id=id).first()
        if response_dict:
            response = make_response(
                jsonify(response_dict.to_dict()),
                200,
            )
        else:
            response = make_response(
                jsonify({"error": "freelancer not found"}),
                404
            )
        return response


class Clients(Resource):
    def get(self):
        response_dict_list = [n.to_dict() for n in Client.query.all()]
        response = make_response(
            jsonify(response_dict_list),
            200,
        )
        return response


class Projects(Resource):
    def get(self):
        response_dict_list = [p.to_dict() for p in Project.query.all()]
        response = make_response(
            jsonify(response_dict_list),
            200,
        )
        return response

    def post(self):
        try:
            new_record = Project(
                title=request.form["title"],
                description=request.form["description"],
                rate=request.form["rate"],
                freelancer_id=request.form["freelancer_id"],
                client_id=request.form["client_id"]
            )

            db.session.add(new_record)
            db.session.commit()
            response = new_record.to_dict()
            response['client'] = new_record.client.to_dict(only=('id', 'name'))
            response['freelancer'] = new_record.freelancer.to_dict(only=('id', 'name'))
            return make_response(jsonify(response), 201)

        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)


class ProjectByID(Resource):
    def get(self, id):
        project = Project.query.filter_by(id=id).first()
        if project:
            response = make_response(
                jsonify(project.to_dict()),
                200,
            )
        else:
            response = make_response(
                jsonify({"error": "project not found"}),
                404
            )
        return response

    def patch(self, id):
        project = Project.query.filter_by(id=id).first()
        if project:
            try:
                for key, value in request.form.items():
                    setattr(project, key, value)
                db.session.commit()
                response = make_response(
                    jsonify(project.to_dict()),
                    200
                )
            except Exception as e:
                response = make_response(
                    jsonify({"errors": [str(e)]}),
                    400
                )
        else:
            response = make_response(
                jsonify({"error": "project not found"}),
                404
            )
        return response

    def delete(self, id):
        project = Project.query.filter_by(id=id).first()
        if project:
            db.session.delete(project)
            db.session.commit()
            response_dict = {"message": "record successfully deleted"}
            response = make_response(
                jsonify(response_dict),
                200
            )
        else:
            response = make_response(
                jsonify({"error": "project not found"}),
                404
            )
        return response


api.add_resource(Freelancers, "/freelancers")
api.add_resource(FreelancerByID, "/freelancers/<int:id>")
api.add_resource(Clients, "/clients")
api.add_resource(Projects, "/projects")
api.add_resource(ProjectByID, "/projects/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
