from flask import Flask, render_template, jsonify, request, session, redirect, url_for
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb://agapao:5561@3.34.98.182', 27017)
db = client.aunae

arr=["a","b","c","d","e","f","g"]

doc={
    'abc':arr
}
db.solution.update_one({'name':'아린'}, {'$set':{'solution':arr}})