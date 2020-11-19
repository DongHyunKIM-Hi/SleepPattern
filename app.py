# -*- coding:utf-8 -*-
import hashlib
import datetime
import jwt
from flask_restful import Resource, Api, reqparse, abort
import json
import os
import sys
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, make_response
from pymongo import MongoClient
client = MongoClient('mongodb://agapao1:1998@15.164.163.148/', 27017)
db = client.aunae


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
        data = db.solution.find_one({'name': '아린'}, {'_id': 0})
        data = json.dumps(data, ensure_ascii=False, indent=4)
        dat = make_response(data)
        return dat


api.add_resource(TodoList, '/todos/')
api.add_resource(Todo, '/todos/<string:todo_id>')
api.add_resource(Demotest, '/test')


# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'apple'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;

#################################
##  HTML을 주는 부분             ##
#################################


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    return render_template('logout.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/mypage')
def mypage():
    return render_template('mypage.html')


@app.route('/reservation')
def reservation():
    return render_template('reservation.html')


@app.route('/result')
def result():
    want_name = request.args.get('name')
    return render_template('report.html', name=want_name)


@app.route('/solution')
def solution():
    return render_template('solution.html')


@app.route('/popup')
def popup():
    want_name = request.args.get('name')
    return render_template('popup.html', name=want_name)


@app.route('/cusadd')
def cusadd():
    print('hi')
    return render_template('customeradd.html')


#################################
##  로그인을 위한 API            ##
#################################

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one(
        {'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=1800)
        }
        token = jwt.encode(payload, SECRET_KEY,
                           algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)


@app.route('/api/nick', methods=['GET'])
def api_valid():
    # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
    # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
    token_receive = request.headers['token_give']

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})


@app.route('/show', methods=['GET'])
def show():
    name = request.args.get('name')
    orders = list(db.solution.find({}, {'_id': 0}))
    return jsonify({'result': 'success', 'all_orders': orders})


@app.route('/showsolution', methods=['GET'])
def showsolution():
    name = request.args.get('name')
    want_item = db.solution.find_one({'name': name}, {'_id': 0})
    order = list(want_item['solution'])
    return jsonify({'result': 'success', 'all_orders': order})


@app.route('/showscore', methods=['GET'])
def showscore():
    name = request.args.get('name')
    want_item = db.solution.find_one({'name': name}, {'_id': 0})
    score1 = list(want_item['score1'])
    score2 = list(want_item['score2'])
    score3 = list(want_item['score3'])
    score4 = list(want_item['score4'])
    score5 = list(want_item['score5'])
    return jsonify({'result': 'success', 'score1': score1, 'score2': score2, 'score3': score3, 'score4': score4, 'score5': score5})


@app.route('/show2', methods=['GET'])
def show2():
    name = request.args.get('name')
    want_date = db.solution.find_one({'name': name}, {'_id': 0})
    order = list(want_date['year'])
    return jsonify({'result': 'success', 'all_orders': order})


@app.route('/savedb', methods=['POST'])
def savedb():
    data = request.get_json()
    name_receive = data['name_give']
    sol_receive = data['arr']
    db.solution.update_one({'name': name_receive}, {
                           '$set': {'solution': sol_receive}})
    return jsonify({'result': 'success'})


@app.route('/savescore1', methods=['POST'])
def savescore1():
    data = request.get_json()
    name_receive = data['name_give']
    score1 = data['number1']
    score2 = data['number2']
    score3 = data['number3']
    score4 = data['number4']
    score5 = data['number5']
    db.solution.update({'name': name_receive}, {
        '$push': {'score1': score1}})
    db.solution.update({'name': name_receive}, {
        '$push': {'score2': score2}})
    db.solution.update({'name': name_receive}, {
        '$push': {'score3': score3}})
    db.solution.update({'name': name_receive}, {
        '$push': {'score4': score4}})
    db.solution.update({'name': name_receive}, {
        '$push': {'score5': score5}})
    return jsonify({'result': 'success'})



@app.route('/addcustomer', methods=['POST'])
def addcustomer():
    name_receive = request.form['name_give']
    age_receive = request.form['age_give']
    phone_receive = request.form['phone_give']
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    image_receive = request.form['image_give']

    doc = {
        'name': name_receive,
        'age': age_receive,
        'phone': phone_receive,
        'id': id_receive,
        'password': password_receive,
        'image': image_receive
    }

    db.solution.insert_one(doc)

    return jsonify({'result': 'success', 'msg': '저장이 완료되었습니다'})


if __name__ == '__main__':
    app.run('localhost', port=5000, debug=True)