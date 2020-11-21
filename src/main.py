"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)



# TO GET ALL OF THE TODOS 

@app.route('/todos', methods=['GET'])
def handle_todos():
    todos_query=Todo.query.all()
    response_body = list(map(lambda x: x.serialize(), todos_query))


    return jsonify(response_body), 200


# TO ADD THE TODOS

@app.route('/todos', methods=['POST'])
def add_todo():
    
    body = request.get_json()
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'label' not in body:
        raise APIException('You need to specify the label', status_code=400)
    if 'done' not in body:
        raise APIException('You need to specify done', status_code=400)

    todo = Todo(label=body['label'], done=body['done'])
    db.session.add(todo)
    db.session.commit()
    return "ok", 200

# delete todo

@app.route('/todos/<int:id>', methods=['DELETE'])
def delete_todos(id):
    todo = Todo.query.get(id)
    if todo is None:
        raise APIException('Todo not found', status_code=404)
    db.session.delete(todo)
    db.session.commit()
    return "ok", 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
