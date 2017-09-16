#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, Response
from flask import request
import json
from flask import jsonify
from flask.ext.cors import CORS, cross_origin
from train import *

app = Flask(__name__)

app.secret_key = "Make twitter great again"
app.debug = True

@app.route("/", methods=['GET','POST'])
@cross_origin()
def hello():
	text = str(request.form["text"].encode('utf-8'))
	p = generate_answer(text);
	print("INPUT: " + text)
	print(p)
	resp = Response(response=p,
                    status=200,
                    mimetype="text/plain")
	return resp

if __name__ == "__main__":
    app.run(threaded=True)