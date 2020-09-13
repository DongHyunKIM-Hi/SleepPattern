import json
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
#-*- coding:utf-8 -*-
from pymongo import MongoClient
client = MongoClient('mongodb://agapao:5561@3.34.98.182/', 27017)
db = client.aunae

from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
api = Api(app)


# 할일 정의
Todos = {
    'todo1': {"task": "영진"},
    'todo2': {'task': "bb"},
    'todo3': {'task': 'cc'}
}

# 예외처리
def exception(todo_id):
    if todo_id not in Todos:
        abort(404, message="Todos - {0} not exists".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task')


# 할일
class Todo(Resource):

    def get(self, todo_id):
        exception(todo_id)
        return Todos[todo_id]

    def delete(self, todo_id):
        exception(todo_id)
        del Todos[todo_id]
        return "", 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        Todos[todo_id] = task
        return task, 201


class TodoList(Resource):
    def get(self):
        return Todos

    def post(self):
        args = parser.parse_args()
        todo_id = "todo{}".format(len(Todos) + 1)
        Todos[todo_id] = {'task': args['task']}
        return Todos[todo_id], 201

class Demotest(Resource):
   def get(self):      
      data = db.solution.find_one({'name':'아린'}, {'_id':0})
      data = json.dumps(data, ensure_ascii=False, indent=4)
      dat = make_response(data)
      return dat

api.add_resource(TodoList, '/todos/')
api.add_resource(Todo, '/todos/<string:todo_id>')
api.add_resource(Demotest,'/test')

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)